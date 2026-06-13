"""
Corral project-manager dashboard ETL.

Reads markdown sources from the repo mount (read-only /repo) and writes
data.json to the container-internal served directory (SERVED_DIR env var,
default: /served).

Sources:
  (a) Roadmap: roadmap block in /repo/ai-infrastructure/project-manager/STATUS.md
      frontmatter. Phase status is DERIVED from epic/task rollup (ADR-036):
      current_phase = lowest phase that is not fully done; phase < current ->
      "done", phase == current -> "current", phase > current -> "upcoming".
      Never add to or edit this block.
  (b) Coordinator and workspace STATUS: /repo/ai-infrastructure/*/STATUS.md
      frontmatter, parsed tolerantly (missing fields omitted, not errored).
  (c) Department roster: the ADR-021 blessed list, encoded as DEPARTMENTS_ROSTER
      below. ADR-021 is the authority for this list.
  (d) Per-workspace task trees (ADR-031): /repo/ai-infrastructure/project-manager/tasks/
      plus /repo/ai-infrastructure/<dept>/tasks/ for each existing department.
      Status is taken from the CONTAINING DIRECTORY (authoritative per
      tasks/README.md), not from frontmatter. Per-department counts come from
      that department's own tree; overall counts are the union across all trees.
  (e) Coordinator ADRs: /repo/ai-infrastructure/project-manager/decisions/ADR-*.md
      frontmatter (id, adr, title, status, date).
  (f) Observations count: count COR-NN entries in
      /repo/ai-infrastructure/project-manager/OBSERVATIONS.md.
  (g) Cross-department agents: /repo/.claude/agents/*.md frontmatter
      (name, model, kind, purpose). purpose is the first sentence of the
      frontmatter description field (text up to and including the first
      period-then-whitespace; whole description when no such match exists).
      Files whose frontmatter is absent or invalid are skipped (tolerant
      parsing). Output is sorted by name.

JSON contract shape (data.json):
  meta:            generated_at, source, project, current_phase (DERIVED from
                   roadmap epic/task rollup per ADR-036), current_phase_title
                   (DERIVED), last_updated, next_step (DERIVED from first
                   non-done epic of current phase, formatted as '<id>: <title>')
  roadmap:         [ {phase, title, deliverables, legacy, status,
                      epics: [...], warning} ]
                    legacy: true only on Phase 0 (bootstrap); absent otherwise.
                    status: derived via derive_roadmap_status.
                    warning: string when cardinality violation detected, else null.
                    Each epic: {id, title, dept, status, task_count, done_count,
                      tasks: [resolved task refs], adrs: [resolved adr refs],
                      warning, cross_dept_warning}
                    epic.dept: owning department slug (from STATUS.md epic.dept field).
                    epic.status: rolled up from task refs only (ADR-036):
                      all tasks done -> 'done'; partial progress or any
                      in-progress/blocked -> 'in-progress'; 0 tasks -> 'planned';
                      all backlog -> 'planned'.
                    epic.warning: string when epic has exactly 1 task, else null.
                    epic.cross_dept_warning: string when any resolved task belongs
                      to a workspace other than epic.dept, else null (dormant on
                      current data; ADR-036 "Epic scope").
                    Resolved ref shape (tasks and adrs lists):
                      label: display string (e.g. "COR-T-014", "ADR-001-009")
                      resolved_status: one of done / accepted / in-progress /
                        blocked / backlog / pending / planned / mixed / unresolved
                      type: "task" | "adr"
                      flavor: "single" | "range" | "unresolved"
                    Range references additionally carry:
                      member_count: int (number of expanded members)
                      rollup_status: the rollup color state (same values as
                        resolved_status)
  departments:     [ {slug, domain, exists, orchestrator_command, label,
                       status, task_counts} ]
                    status is null for planned depts; for existing depts:
                    {last_updated} only (no phase: departments have no phase field).
  coordinator:     {slug, phase, phase_title, last_updated}
  workspace_details: { <slug>: {header, recent_updates, adrs,
                                observations_count, task_counts} }
                    department headers carry {slug, display_name, domain, role,
                    exists, planned, last_updated} - no phase key.
                    coordinator header carries phase (the derived current_phase).
                    adrs list entries carry {id, adr, title, status, date, body}
                    where body is the post-frontmatter markdown text (the YAML
                    block stripped). body is an empty string when the file body
                    cannot be read.
  recent_activity: [ {workspace, date, text} ] newest-first, capped 30
  agents:          [ {name, model, kind, purpose} ] name-sorted.
                    name: frontmatter `name`; model: frontmatter `model`;
                    kind: frontmatter `kind` (executor | dispatch);
                    purpose: first sentence of frontmatter `description`
                    (text up to and including the first period-then-whitespace;
                    whole description when no such match exists).
"""

import argparse
import json
import os
import re
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# ADR-021 blessed department roster. This list is the authority; do not
# add or remove entries here without a corresponding ADR-021 amendment.
DEPARTMENTS_ROSTER = [
    {"slug": "agent-development",  "domain": "ai-infrastructure"},
    {"slug": "test-design",        "domain": "ai-infrastructure"},
    {"slug": "docs",               "domain": "ai-infrastructure"},
    {"slug": "backend-api",        "domain": "web-app"},
    {"slug": "database",           "domain": "web-app"},
    {"slug": "mcp-server",         "domain": "web-app"},
    {"slug": "frontend-ui",        "domain": "web-app"},
    {"slug": "devops",             "domain": "web-app"},
]

COORDINATOR_SLUG = "project-manager"
TASK_STATUSES = ["backlog", "in-progress", "blocked", "done"]
RECENT_ACTIVITY_CAP = 30
RECENT_UPDATES_CAP = 10


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_frontmatter(path: Path) -> dict:
    """
    Parse YAML frontmatter from a markdown file. Returns {} on any error
    (tolerant parsing: missing files, malformed YAML, no frontmatter).
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    try:
        return yaml.safe_load(text[3:end]) or {}
    except yaml.YAMLError:
        return {}


def slug_to_display(slug: str) -> str:
    return slug.replace("-", " ").title()


def count_observations(obs_path: Path) -> int:
    """Count COR-NN entries in OBSERVATIONS.md."""
    try:
        text = obs_path.read_text(encoding="utf-8")
    except OSError:
        return 0
    return len(re.findall(r"###\s+COR-\d+", text))


def parse_recent_updates(fm: dict) -> list:
    """
    Extract recent_updates list from frontmatter. Each entry is either a
    plain string "DATE: text" or a dict {date, text}. Normalise to
    {date, text} dicts, newest-first, capped at RECENT_UPDATES_CAP.
    """
    raw = fm.get("recent_updates", [])
    if not isinstance(raw, list):
        return []
    result = []
    for item in raw:
        if isinstance(item, dict):
            result.append({
                "date": str(item.get("date", "")),
                "text": str(item.get("text", "")),
            })
        elif isinstance(item, str):
            # "YYYY-MM-DD: text" format used in STATUS.md
            m = re.match(r"^(\d{4}-\d{2}-\d{2}):\s*(.*)", item, re.DOTALL)
            if m:
                result.append({"date": m.group(1), "text": m.group(2).strip()})
            else:
                result.append({"date": "", "text": item.strip()})
    return result[:RECENT_UPDATES_CAP]


def derive_roadmap_status(phase: int, current_phase: int) -> str:
    if phase < current_phase:
        return "done"
    if phase == current_phase:
        return "current"
    return "upcoming"


def derive_current_phase(
    roadmap_raw: list,
    all_tasks: list | None = None,
    adrs: list | None = None,
) -> int:
    """
    Derive the current phase number from per-epic effective statuses (ADR-036).

    A phase is fully done if:
      - It carries legacy: true (bootstrap phase, always done), OR
      - It has at least 1 epic and every epic's task-only rollup status is 'done'.
    A phase with an empty epics list (and no legacy flag) is NOT fully done.
    Returns the lowest phase that is not fully done. If every phase is fully
    done, returns the maximum phase number. Returns 0 for an empty roadmap.
    """
    if all_tasks is None:
        all_tasks = []
    if adrs is None:
        adrs = []
    if not roadmap_raw:
        return 0
    phase_nums = []
    for item in roadmap_raw:
        if not isinstance(item, dict):
            continue
        phase_nums.append(int(item.get("phase", 0)))
    if not phase_nums:
        return 0
    for item in roadmap_raw:
        if not isinstance(item, dict):
            continue
        phase_num = int(item.get("phase", 0))
        # Legacy phases (Phase 0 bootstrap) are always done.
        if item.get("legacy"):
            continue
        epics = item.get("epics", [])
        if not isinstance(epics, list):
            epics = []
        if not epics:
            return phase_num
        if not all(
            isinstance(ep, dict)
            and derive_epic_status(ep, all_tasks, adrs) == "done"
            for ep in epics
        ):
            return phase_num
    return max(phase_nums)


def derive_current_phase_title(roadmap_raw: list, current_phase: int) -> str:
    """
    Return the title of the roadmap entry whose phase equals current_phase.
    Returns an empty string if no entry matches.
    """
    for item in roadmap_raw:
        if not isinstance(item, dict):
            continue
        if int(item.get("phase", -1)) == current_phase:
            return str(item.get("title", ""))
    return ""


def derive_next_step(
    roadmap_raw: list,
    current_phase: int,
    all_tasks: list | None = None,
    adrs: list | None = None,
) -> str:
    """
    Return the first non-done epic of the current phase, formatted as
    '<id>: <title>' (ADR-036). Returns an empty string if the current phase
    has no non-done epic.
    """
    if all_tasks is None:
        all_tasks = []
    if adrs is None:
        adrs = []
    for item in roadmap_raw:
        if not isinstance(item, dict):
            continue
        if int(item.get("phase", -1)) != current_phase:
            continue
        epics = item.get("epics", [])
        if not isinstance(epics, list):
            return ""
        for ep in epics:
            if not isinstance(ep, dict):
                continue
            eff_status = derive_epic_status(ep, all_tasks, adrs)
            if eff_status == "done":
                continue
            ep_id = str(ep.get("id", ""))
            ep_title = str(ep.get("title", ""))
            return f"{ep_id}: {ep_title}"
    return ""


# ---------------------------------------------------------------------------
# Reference resolution helpers
# ---------------------------------------------------------------------------

def expand_range_token(token: str) -> list[str]:
    """
    Expand a '..' range token like 'ADR-001..009' or 'COR-T-001..006' into
    a list of individual IDs. Returns a single-element list for bare IDs
    (no '..' in the token). Handles numeric padding: uses the width of the
    start number.

    Examples:
      'ADR-001..009' -> ['ADR-001', 'ADR-002', ..., 'ADR-009']
      'COR-T-001..006' -> ['COR-T-001', 'COR-T-002', ..., 'COR-T-006']
      'COR-T-014' -> ['COR-T-014']
    """
    if ".." not in token:
        return [token]
    left, right = token.split("..", 1)
    # The right side is a numeric suffix; the left side ends with digits too.
    # Split prefix from the trailing digits of the left side.
    m = re.match(r"^(.*?)(\d+)$", left)
    if not m:
        return [token]  # Cannot parse; treat as bare
    prefix = m.group(1)
    start_str = m.group(2)
    end_str = right.strip()
    try:
        start = int(start_str)
        end = int(end_str)
    except ValueError:
        return [token]
    width = len(start_str)
    return [f"{prefix}{str(i).zfill(width)}" for i in range(start, end + 1)]


def resolve_ref_status(ref_id: str, all_tasks: list, adrs: list) -> tuple[str, str]:
    """
    Resolve a single reference ID to (status, type).
    type is 'task' or 'adr'.
    status is one of: done / in-progress / blocked / backlog / accepted /
      pending / unresolved.

    ADR resolution: the collect_adrs 'id' field is typically a bare integer
    string (e.g. "12") because the ADR frontmatter has 'adr: 12' with no
    separate 'id' field. References use the 'ADR-012' form. We normalise
    both sides to a bare integer for comparison.
    """
    # Determine type by prefix: 'ADR-NNN' is an adr; everything else is a task.
    upper = ref_id.upper()
    adr_match = re.match(r"^ADR-(\d+)$", upper)
    if adr_match:
        ref_num = int(adr_match.group(1))
        for adr in adrs:
            # adr['adr'] is the integer field; adr['id'] may be "12" or "ADR-012"
            # Try matching via the integer 'adr' key first.
            adr_num = adr.get("adr")
            if adr_num is not None:
                try:
                    if int(adr_num) == ref_num:
                        return str(adr.get("status", "unresolved")), "adr"
                    continue
                except (ValueError, TypeError):
                    pass
            # Fallback: parse the 'id' field
            adr_id_str = str(adr.get("id", "")).upper()
            m2 = re.match(r"^(?:ADR-)?(\d+)$", adr_id_str)
            if m2 and int(m2.group(1)) == ref_num:
                return str(adr.get("status", "unresolved")), "adr"
        return "unresolved", "adr"
    else:
        # Task
        for task in all_tasks:
            task_id = str(task.get("id", "")).upper()
            if task_id == upper:
                return str(task.get("status", "unresolved")), "task"
        return "unresolved", "task"


def _normalise_adr_id(adr_id: str) -> str:
    """Normalise 'ADR-001' and 'ADR-1' to the same canonical string."""
    m = re.match(r"^ADR-(\d+)$", adr_id)
    if m:
        return f"ADR-{int(m.group(1))}"
    return adr_id


def _rollup_statuses(statuses: list[str]) -> str:
    """
    Roll up a list of statuses for a range badge.
    - All identical -> that status.
    - Any in-progress or blocked -> 'in-progress'.
    - Otherwise -> 'mixed'.
    """
    if not statuses:
        return "unresolved"
    unique = set(statuses)
    if len(unique) == 1:
        return unique.pop()
    # Any active work state -> in-progress
    if any(s in ("in-progress", "blocked") for s in statuses):
        return "in-progress"
    return "mixed"


def resolve_milestone_refs(ms: dict, all_tasks: list, adrs: list) -> list:
    """
    Given a milestone dict (with optional 'tasks' and 'adrs' lists from
    STATUS.md frontmatter), expand range tokens and resolve each ID.
    Returns a list of resolved ref objects. Each object has:
      label, resolved_status, type, flavor
    Range objects additionally have member_count and rollup_status.
    """
    refs = []

    def process_list(raw_list: list, expected_type_hint: str) -> None:
        if not isinstance(raw_list, list):
            return
        for token in raw_list:
            token = str(token).strip()
            if ".." in token:
                # Range token
                members = expand_range_token(token)
                member_statuses = []
                for mid in members:
                    status, _t = resolve_ref_status(mid, all_tasks, adrs)
                    member_statuses.append(status)
                rollup = _rollup_statuses(member_statuses)
                # Build a display label: strip the leading type prefix on the
                # end token to show e.g. "ADR-001-009" or "COR-T-001-006"
                # Format: <prefix><start>-<end_digits>
                m = re.match(r"^(.*?)(\d+)\.\.(.*\D)?(\d+)$", token)
                if m:
                    label = f"{m.group(1)}{m.group(2)}-{m.group(4)}"
                else:
                    label = token.replace("..", "-")
                refs.append({
                    "label": label,
                    "resolved_status": rollup,
                    "type": expected_type_hint,
                    "flavor": "range",
                    "member_count": len(members),
                    "rollup_status": rollup,
                })
            else:
                # Bare ID
                status, ref_type = resolve_ref_status(token, all_tasks, adrs)
                flavor = "unresolved" if status == "unresolved" else "single"
                refs.append({
                    "label": token,
                    "resolved_status": status,
                    "type": ref_type,
                    "flavor": flavor,
                })

    process_list(ms.get("tasks", []), "task")
    process_list(ms.get("adrs", []), "adr")
    return refs


def derive_effective_status(ms: dict, refs: list) -> str:
    """
    Derive the effective status for a milestone (legacy helper, preserved for
    compatibility). Only TASK refs drive effective status (done-ness); ADR refs
    are informational and do not affect the rollup.
    If task refs exist, roll them up:
      - All done/accepted -> 'done'
      - Any in-progress or blocked -> 'in-progress'
      - Otherwise -> 'planned'
    If there are ZERO task refs (regardless of ADR refs), fall back to
    the hand-set 'status' frontmatter field.
    ADR refs are still resolved and emitted in the refs list for badge
    rendering; they simply do not influence effective_status.
    """
    task_refs = [r for r in refs if r.get("type") == "task"]
    if task_refs:
        statuses = [r["resolved_status"] for r in task_refs]
        if all(s in ("done", "accepted") for s in statuses):
            return "done"
        if any(s in ("in-progress", "blocked") for s in statuses):
            return "in-progress"
        return "planned"
    # No task refs: use hand-set status
    return str(ms.get("status", "planned"))


def derive_epic_status(ep: dict, all_tasks: list, adrs: list) -> str:
    """
    Derive the rolled-up status for an epic (ADR-036 "Completion and status").
    Resolves the epic's 'tasks' list; ADRs are informational and never
    drive completion.
      - 0 tasks -> 'planned'
      - All tasks done/accepted -> 'done'
      - Some tasks done but not all, OR any task in-progress or blocked ->
        'in-progress' (partial progress reads as in-progress, not planned)
      - Otherwise (all backlog/planned) -> 'planned'
    """
    raw_tasks = ep.get("tasks", [])
    if not isinstance(raw_tasks, list) or not raw_tasks:
        return "planned"
    # Resolve each task token (may include range tokens)
    task_statuses = []
    for token in raw_tasks:
        token = str(token).strip()
        members = expand_range_token(token)
        for mid in members:
            status, _t = resolve_ref_status(mid, all_tasks, adrs)
            task_statuses.append(status)
    if not task_statuses:
        return "planned"
    if all(s in ("done", "accepted") for s in task_statuses):
        return "done"
    if any(s in ("in-progress", "blocked") for s in task_statuses):
        return "in-progress"
    # Partial progress: some done but not all -> in-progress (ADR-036)
    if any(s in ("done", "accepted") for s in task_statuses):
        return "in-progress"
    return "planned"


# ---------------------------------------------------------------------------
# Task pool
# ---------------------------------------------------------------------------

def collect_tasks(tasks_root: Path) -> list:
    """
    Walk backlog/in-progress/blocked/done directories. Status is taken from
    the containing directory (authoritative). Returns a list of task dicts
    with keys: id, title, labels, status.
    """
    tasks = []
    for status_dir in TASK_STATUSES:
        dir_path = tasks_root / status_dir
        if not dir_path.is_dir():
            continue
        for md_file in sorted(dir_path.glob("*.md")):
            fm = parse_frontmatter(md_file)
            if not fm:
                continue
            labels = fm.get("labels", [])
            if not isinstance(labels, list):
                labels = []
            tasks.append({
                "id": fm.get("id", ""),
                "title": fm.get("title", ""),
                "labels": [str(l) for l in labels],
                "status": status_dir,  # directory is authoritative
            })
    return tasks


def compute_task_counts(tasks: list, label_prefix: str | None = None) -> dict:
    """
    Count tasks by status. If label_prefix is provided, filter to tasks
    carrying a label that starts with that prefix (dept: reads by prefix only,
    per ADR-018 pending-decoupling rule).
    """
    counts = {s: 0 for s in TASK_STATUSES}
    for task in tasks:
        if label_prefix is not None:
            if not any(l.startswith(label_prefix) for l in task["labels"]):
                continue
        counts[task["status"]] += 1
    counts["total"] = sum(counts.values())
    return counts


# ---------------------------------------------------------------------------
# ADR parsing
# ---------------------------------------------------------------------------

def extract_body(path: Path) -> str:
    """
    Return the post-frontmatter markdown body from a file, stripping the
    leading ---\\n...\\n---\\n block. Returns the full text if no frontmatter
    is found, and an empty string on read error.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ""
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    if end == -1:
        return text
    # Skip past the closing --- and the trailing newline.
    body_start = end + 4  # len("\n---") == 4
    if body_start < len(text) and text[body_start] == "\n":
        body_start += 1
    return text[body_start:]


def collect_adrs(decisions_dir: Path) -> list:
    """
    Parse frontmatter from ADR-*.md files. Returns list of dicts with
    id, adr, title, status, date, body.
    body is the post-frontmatter markdown text (YAML block stripped).
    """
    adrs = []
    for md_file in sorted(decisions_dir.glob("ADR-*.md")):
        fm = parse_frontmatter(md_file)
        if not fm or "adr" not in fm:
            continue
        adrs.append({
            "id": str(fm.get("id", fm.get("adr", ""))),
            "adr": int(fm.get("adr", 0)),
            "title": str(fm.get("title", "")),
            "status": str(fm.get("status", "")),
            "date": str(fm.get("date", "")),
            "body": extract_body(md_file),
        })
    adrs.sort(key=lambda x: x["adr"])
    return adrs


# ---------------------------------------------------------------------------
# Agent fleet
# ---------------------------------------------------------------------------

def collect_agents(agents_dir: Path) -> list:
    """
    Scan agents_dir for *.md files and extract agent metadata via a line-based
    scan of the frontmatter block. Does NOT use yaml or parse_frontmatter
    because the agent `description` field is a single long plain-scalar line
    containing colon-space sequences (e.g. "Context: ", "user: ") that PyYAML
    rejects as mapping values. Line-based extraction is robust against these.

    Isolates the frontmatter block using the same text.find("\\n---", 3) idiom
    that parse_frontmatter and extract_body use. Extracts name, model, kind,
    and description by scanning for lines whose stripped text starts with the
    matching key prefix and taking the value after the first colon.

    Returns a list of dicts with keys: name, model, kind, purpose.
    purpose is the first sentence of the frontmatter description field (text
    up to and including the first period-then-whitespace; falls back to the
    whole description when no such match exists). Skips files where name,
    model, or kind is missing or empty (tolerant parsing). Output is sorted
    by name.
    """
    agents = []
    for md_file in sorted(agents_dir.glob("*.md")):
        try:
            text = md_file.read_text(encoding="utf-8")
        except OSError:
            continue
        # Isolate the frontmatter block: must start with --- and close with \n---
        if not text.startswith("---"):
            continue
        end = text.find("\n---", 3)
        if end == -1:
            continue
        fm_block = text[3:end]
        # Extract fields by line-based scan
        name = ""
        model = ""
        kind = ""
        description = ""
        for line in fm_block.splitlines():
            stripped = line.strip()
            if stripped.startswith("name:") and not name:
                name = stripped[len("name:"):].strip()
            elif stripped.startswith("model:") and not model:
                model = stripped[len("model:"):].strip()
            elif stripped.startswith("kind:") and not kind:
                kind = stripped[len("kind:"):].strip()
            elif stripped.startswith("description:") and not description:
                description = stripped[len("description:"):].strip()
        # Skip if any required field is missing or empty
        if not name or not model or not kind:
            continue
        # Extract first sentence of description: text up to and including the
        # first period that is immediately followed by whitespace. Falls back
        # to the whole description when no such match exists.
        m = re.search(r"\.\s", description)
        if m:
            purpose = description[: m.start() + 1]
        else:
            purpose = description.strip()
        agents.append({
            "name": name,
            "model": model,
            "kind": kind,
            "purpose": purpose,
        })
    agents.sort(key=lambda x: x["name"])
    return agents


# ---------------------------------------------------------------------------
# Main ETL
# ---------------------------------------------------------------------------

def collect_all_tasks(repo_root: Path) -> tuple[list, dict]:
    """
    Collect tasks from every workspace tree (coordinator + each existing
    department). Returns (all_tasks_combined, per_workspace_tasks) where
    per_workspace_tasks maps slug -> list of task dicts for that tree only.

    Per ADR-031: the tree is the department partition. Per-department counts
    come from that department's own tree; overall counts are the union.
    """
    pm_tasks_root = repo_root / "ai-infrastructure" / "project-manager" / "tasks"
    coordinator_tasks = collect_tasks(pm_tasks_root)
    per_workspace: dict = {COORDINATOR_SLUG: coordinator_tasks}

    for entry in DEPARTMENTS_ROSTER:
        slug = entry["slug"]
        dept_tasks_root = repo_root / "ai-infrastructure" / slug / "tasks"
        if dept_tasks_root.is_dir():
            per_workspace[slug] = collect_tasks(dept_tasks_root)
        else:
            per_workspace[slug] = []

    combined = []
    for tasks in per_workspace.values():
        combined.extend(tasks)

    return combined, per_workspace


def run_etl(repo_root: Path, served_dir: Path) -> None:
    pm_dir = repo_root / "ai-infrastructure" / "project-manager"
    status_path = pm_dir / "STATUS.md"
    decisions_dir = pm_dir / "decisions"
    observations_path = pm_dir / "OBSERVATIONS.md"
    commands_dir = repo_root / ".claude" / "commands"
    agents_dir = repo_root / ".claude" / "agents"

    # -- (a) Coordinator STATUS frontmatter ---------------------------------
    coordinator_fm = parse_frontmatter(status_path)
    last_updated = str(coordinator_fm.get("last_updated", ""))

    # -- (d) Per-workspace task trees (ADR-031) ------------------------------
    # Collected here (before roadmap assembly) so reference resolution can
    # use them when deriving effective milestone statuses.
    # all_tasks is the union across all trees; per_workspace_tasks maps
    # slug -> tasks for that tree only (used for per-department counts).
    all_tasks, per_workspace_tasks = collect_all_tasks(repo_root)
    overall_task_counts = compute_task_counts(all_tasks)

    # -- (e) ADRs ------------------------------------------------------------
    # Collected here (before roadmap assembly) for the same reason.
    adrs = collect_adrs(decisions_dir)

    # -- (a) Roadmap ---------------------------------------------------------
    roadmap_raw = coordinator_fm.get("roadmap", [])
    if not isinstance(roadmap_raw, list):
        roadmap_raw = []

    # Derive current_phase, current_phase_title, and next_step via epic/task
    # rollup per ADR-036. Legacy phases are always done; non-legacy phases
    # are done iff all their epics are done (task-refs-only rollup).
    current_phase = derive_current_phase(roadmap_raw, all_tasks, adrs)
    current_phase_title = derive_current_phase_title(roadmap_raw, current_phase)
    next_step = derive_next_step(roadmap_raw, current_phase, all_tasks, adrs)

    # SPOT-TEST (cross-dept warning): temporarily inject a coordinator-tree task
    # into E2.1 (dept=database) to confirm the cross-dept check fires.
    # This block is reverted immediately after the test; STATUS.md is not touched.
    _spot_test_active = False  # spot-test complete; set True to re-enable
    if _spot_test_active:
        for _item in roadmap_raw:
            if not isinstance(_item, dict):
                continue
            for _ep in _item.get("epics", []):
                if isinstance(_ep, dict) and _ep.get("id") == "E2.1":
                    _ep_tasks = list(_ep.get("tasks", []))
                    _ep_tasks.append("COR-T-001")  # coordinator task, not database
                    _ep["tasks"] = _ep_tasks

    roadmap = []
    for item in roadmap_raw:
        if not isinstance(item, dict):
            continue
        phase_num = int(item.get("phase", 0))
        deliverables = item.get("deliverables", "")
        if isinstance(deliverables, list):
            deliverables = "; ".join(str(d) for d in deliverables)
        is_legacy = bool(item.get("legacy", False))
        raw_epics = item.get("epics", [])
        if not isinstance(raw_epics, list):
            raw_epics = []

        # Cardinality check (ADR-036): non-legacy phase with fewer than 2 epics.
        phase_warning = None
        if not is_legacy and len(raw_epics) < 2:
            phase_warning = f"Phase {phase_num} has {len(raw_epics)} epic(s); expected >= 2 (ADR-036)."

        epics_out = []
        for ep in raw_epics:
            if not isinstance(ep, dict):
                continue
            # Resolve task refs for this epic using resolve_milestone_refs
            # (epics share the same tasks/adrs fields as milestones did).
            refs = resolve_milestone_refs(ep, all_tasks, adrs)
            task_refs = [r for r in refs if r.get("type") == "task"]
            adr_refs = [r for r in refs if r.get("type") == "adr"]

            # Epic status: task-refs-only rollup (ADR-036).
            epic_status = derive_epic_status(ep, all_tasks, adrs)

            # Epic owning department (ADR-036 "Epic scope").
            epic_dept = str(ep.get("dept", ""))

            # Count tasks: expand all task tokens to get true counts.
            raw_task_list = ep.get("tasks", [])
            if not isinstance(raw_task_list, list):
                raw_task_list = []
            task_count = 0
            done_count = 0
            for token in raw_task_list:
                token = str(token).strip()
                members = expand_range_token(token)
                for mid in members:
                    task_count += 1
                    status, _t = resolve_ref_status(mid, all_tasks, adrs)
                    if status in ("done", "accepted"):
                        done_count += 1

            # Cardinality check: exactly 1 task is a smell (ADR-036).
            # 0 tasks is "forming", not flagged.
            epic_warning = None
            if task_count == 1:
                epic_warning = f"Epic {ep.get('id', '?')} has exactly 1 task; consider whether it should be a standalone task (ADR-036)."

            # Cross-department consistency check (ADR-036 "Epic scope").
            # Each task in an epic must belong to the epic's owning dept tree.
            # Dormant on current data (every epic is single-tree).
            cross_dept_warning = None
            if epic_dept:
                offenders = []
                for token in raw_task_list:
                    token = str(token).strip()
                    members = expand_range_token(token)
                    for mid in members:
                        mid_upper = mid.upper()
                        # Determine which workspace owns this task id.
                        owning_ws = None
                        for ws_slug, ws_tasks in per_workspace_tasks.items():
                            for t in ws_tasks:
                                if str(t.get("id", "")).upper() == mid_upper:
                                    owning_ws = ws_slug
                                    break
                            if owning_ws is not None:
                                break
                        if owning_ws is not None and owning_ws != epic_dept:
                            offenders.append(f"{mid} (in {owning_ws})")
                if offenders:
                    cross_dept_warning = (
                        f"Epic {ep.get('id', '?')} (dept={epic_dept}) has tasks "
                        f"from a foreign workspace: {', '.join(offenders)} (ADR-036)."
                    )

            epics_out.append({
                "id": str(ep.get("id", "")),
                "title": str(ep.get("title", "")),
                "dept": epic_dept,
                "status": epic_status,
                "task_count": task_count,
                "done_count": done_count,
                "tasks": task_refs,
                "adrs": adr_refs,
                "warning": epic_warning,
                "cross_dept_warning": cross_dept_warning,
            })

        roadmap.append({
            "phase": phase_num,
            "title": str(item.get("title", "")),
            "deliverables": str(deliverables),
            "legacy": is_legacy,
            "status": derive_roadmap_status(phase_num, current_phase),
            "epics": epics_out,
            "warning": phase_warning,
        })

    # -- (f) Observations count ----------------------------------------------
    observations_count = count_observations(observations_path)

    # -- (g) Cross-department agents -----------------------------------------
    agents = collect_agents(agents_dir)

    # -- (c) Department roster + existence check ----------------------------
    def dept_exists(slug: str) -> bool:
        return (repo_root / "ai-infrastructure" / slug / "STATUS.md").exists()

    def orchestrator_command_exists(slug: str) -> bool:
        return (commands_dir / f"{slug}-orchestrator.md").exists()

    def dept_status(slug: str) -> dict | None:
        p = repo_root / "ai-infrastructure" / slug / "STATUS.md"
        if not p.exists():
            return None
        fm = parse_frontmatter(p)
        return {
            "last_updated": str(fm.get("last_updated", "")),
        }

    departments = []
    for entry in DEPARTMENTS_ROSTER:
        slug = entry["slug"]
        label = f"dept:{slug}"
        exists = dept_exists(slug)
        # Per ADR-031: per-department counts come from the department's own
        # tasks/ tree, not from label-filtering the shared pool.
        dept_tree_tasks = per_workspace_tasks.get(slug, [])
        task_counts = compute_task_counts(dept_tree_tasks)
        departments.append({
            "slug": slug,
            "domain": entry["domain"],
            "exists": exists,
            "orchestrator_command": orchestrator_command_exists(slug),
            "label": label,
            "status": dept_status(slug),
            "task_counts": task_counts,
        })

    # -- Coordinator struct --------------------------------------------------
    coordinator = {
        "slug": COORDINATOR_SLUG,
        "phase": current_phase,
        "phase_title": current_phase_title,
        "last_updated": last_updated,
    }

    # -- workspace_details ---------------------------------------------------
    workspace_details = {}

    # Coordinator detail
    coord_recent = parse_recent_updates(coordinator_fm)
    workspace_details[COORDINATOR_SLUG] = {
        "header": {
            "slug": COORDINATOR_SLUG,
            "display_name": "Project Manager (Coordinator)",
            "domain": "ai-infrastructure",
            "role": "coordinator",
            "exists": True,
            "planned": False,
            "phase": current_phase,
            "last_updated": last_updated,
        },
        "recent_updates": coord_recent,
        "adrs": adrs,
        "observations_count": observations_count,
        # Per ADR-031: coordinator counts come from its own tasks/ tree.
        "task_counts": compute_task_counts(
            per_workspace_tasks.get(COORDINATOR_SLUG, [])
        ),
    }

    # Department details
    for entry in DEPARTMENTS_ROSTER:
        slug = entry["slug"]
        exists = dept_exists(slug)
        # Per ADR-031: per-department counts come from the department's own
        # tasks/ tree, not from label-filtering the combined pool.
        dept_tree_tasks = per_workspace_tasks.get(slug, [])
        task_counts = compute_task_counts(dept_tree_tasks)

        if not exists:
            workspace_details[slug] = {
                "header": {
                    "slug": slug,
                    "display_name": slug_to_display(slug),
                    "domain": entry["domain"],
                    "role": "department",
                    "exists": False,
                    "planned": True,
                    "last_updated": None,
                },
                "recent_updates": None,
                "adrs": None,
                "observations_count": None,
                "task_counts": task_counts,
            }
        else:
            dept_status_dir = repo_root / "ai-infrastructure" / slug
            fm = parse_frontmatter(dept_status_dir / "STATUS.md")
            dept_recent = parse_recent_updates(fm)
            dept_decisions_dir = dept_status_dir / "decisions"
            dept_adrs = collect_adrs(dept_decisions_dir) if dept_decisions_dir.is_dir() else None
            dept_obs_path = dept_status_dir / "OBSERVATIONS.md"
            dept_obs = count_observations(dept_obs_path) if dept_obs_path.exists() else None
            workspace_details[slug] = {
                "header": {
                    "slug": slug,
                    "display_name": slug_to_display(slug),
                    "domain": entry["domain"],
                    "role": "department",
                    "exists": True,
                    "planned": False,
                    "last_updated": str(fm.get("last_updated", "")),
                },
                "recent_updates": dept_recent or None,
                "adrs": dept_adrs,
                "observations_count": dept_obs,
                "task_counts": task_counts,
            }

    # -- recent_activity (aggregate all workspace recent_updates, newest-first)
    activity_items = []
    for slug_key, details in workspace_details.items():
        ru = details.get("recent_updates") or []
        for item in ru:
            activity_items.append({
                "workspace": slug_key,
                "date": item["date"],
                "text": item["text"],
            })
    activity_items.sort(key=lambda x: x["date"], reverse=True)
    recent_activity = activity_items[:RECENT_ACTIVITY_CAP]

    # -- meta ----------------------------------------------------------------
    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "markdown",  # seam: flips to app/MCP at dogfood milestone (ADR-008)
        "project": "Corral",
        "current_phase": current_phase,
        "current_phase_title": current_phase_title,
        "last_updated": last_updated,
        "next_step": next_step,
    }

    # -- Assemble and write --------------------------------------------------
    data = {
        "meta": meta,
        "roadmap": roadmap,
        "departments": departments,
        "coordinator": coordinator,
        "workspace_details": workspace_details,
        "recent_activity": recent_activity,
        "agents": agents,
    }

    served_dir.mkdir(parents=True, exist_ok=True)
    out_path = served_dir / "data.json"
    out_path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    print(f"ETL: wrote {out_path} ({out_path.stat().st_size} bytes)", flush=True)


# ---------------------------------------------------------------------------
# Watch patterns: the ETL source set (mirrors module docstring)
# ---------------------------------------------------------------------------

# Allowlist of regex patterns that match files the ETL actually reads.
# Only events matching one of these patterns trigger a rebuild, preventing
# spurious triggers from unrelated files in the watched trees.
WATCH_PATTERNS = [
    re.compile(r".*/ai-infrastructure/.*\.md$"),
    re.compile(r".*\.claude/commands/.*\.md$"),
    re.compile(r".*\.claude/agents/.*\.md$"),
]


def is_watched(path_str: str) -> bool:
    return any(p.search(path_str) for p in WATCH_PATTERNS)


def run_watch(repo_root: Path, served_dir: Path) -> None:
    """
    Watch the ETL source trees for content changes and re-run run_etl on
    each relevant change. Uses PollingObserver (bind-mount safe on all
    hosts, including Docker Desktop and Linux). Debounces at 350ms via a
    cancel/restart threading.Timer. A rebuild exception is logged but does
    not kill the watch loop.
    """
    from watchdog.observers.polling import PollingObserver
    from watchdog.events import FileSystemEventHandler

    _timer = [None]
    _lock = threading.Lock()

    def schedule_rebuild():
        with _lock:
            if _timer[0] is not None:
                _timer[0].cancel()
            t = threading.Timer(0.35, do_rebuild)
            _timer[0] = t
            t.start()

    def do_rebuild():
        try:
            run_etl(repo_root, served_dir)
        except Exception as e:
            print(f"ERROR: ETL rebuild failed: {e}", file=sys.stderr)

    # Only react to actual content changes. watchdog 4.0+ reports opened /
    # closed / closed_no_write events for every file open, including the
    # reads the build itself does, which causes a feedback loop. Restrict
    # to events that signify the file's content actually changed.
    CONTENT_CHANGE_EVENTS = {"modified", "created", "deleted", "moved"}

    class Handler(FileSystemEventHandler):
        def on_any_event(self, event):
            if event.is_directory:
                return
            if event.event_type not in CONTENT_CHANGE_EVENTS:
                return
            src = getattr(event, "src_path", "")
            dest = getattr(event, "dest_path", "")
            if is_watched(src) or is_watched(dest):
                schedule_rebuild()

    watch_dirs = [
        repo_root / "ai-infrastructure",
        repo_root / ".claude" / "commands",
        repo_root / ".claude" / "agents",
    ]

    observer = PollingObserver()
    for d in watch_dirs:
        if d.exists():
            observer.schedule(Handler(), str(d), recursive=True)

    observer.start()
    print("ETL watch: watching for changes (Ctrl+C to stop)...", flush=True)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Corral project-manager dashboard ETL")
    parser.add_argument(
        "--watch",
        action="store_true",
        help="After the initial build, watch source files and rebuild on changes.",
    )
    args = parser.parse_args()

    repo_root = Path(os.environ.get("REPO_ROOT", "/repo"))
    served_dir = Path(os.environ.get("SERVED_DIR", "/served"))
    if not repo_root.exists():
        print(f"ETL error: REPO_ROOT {repo_root} does not exist", file=sys.stderr)
        sys.exit(1)
    run_etl(repo_root, served_dir)
    if args.watch:
        run_watch(repo_root, served_dir)
