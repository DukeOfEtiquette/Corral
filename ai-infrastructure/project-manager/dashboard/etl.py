"""
Corral project-manager dashboard ETL.

Reads markdown sources from the repo mount (read-only /repo) and writes
data.json to the container-internal served directory (SERVED_DIR env var,
default: /served).

Sources:
  (a) Roadmap: roadmap block in /repo/ai-infrastructure/project-manager/STATUS.md
      frontmatter. Phase status is DERIVED from the top-level `phase` field:
      phase < current -> "done", phase == current -> "current",
      phase > current -> "upcoming". Never add to or edit this block.
  (b) Coordinator and workspace STATUS: /repo/ai-infrastructure/*/STATUS.md
      frontmatter, parsed tolerantly (missing fields omitted, not errored).
  (c) Department roster: the ADR-021 blessed list, encoded as DEPARTMENTS_ROSTER
      below. ADR-021 is the authority for this list.
  (d) Shared task pool: /repo/ai-infrastructure/project-manager/tasks/{backlog,
      in-progress,blocked,done}/*.md. Status is taken from the CONTAINING
      DIRECTORY (authoritative per tasks/README.md), not from frontmatter.
      Labels are parsed from frontmatter with PyYAML.
  (e) Coordinator ADRs: /repo/ai-infrastructure/project-manager/decisions/ADR-*.md
      frontmatter (id, adr, title, status, date).
  (f) Observations count: count COR-NN entries in
      /repo/ai-infrastructure/project-manager/OBSERVATIONS.md.

JSON contract shape (data.json):
  meta:            generated_at, source, project, current_phase,
                   current_phase_title, last_updated, next_step
  roadmap:         [ {phase, title, deliverables, status} ]
  org_chart:       ASCII string
  departments:     [ {slug, domain, exists, orchestrator_command, label,
                       status, task_counts} ]
  coordinator:     {slug, phase, phase_title, last_updated}
  workspace_details: { <slug>: {header, recent_updates, adrs,
                                observations_count, task_counts} }
  recent_activity: [ {workspace, date, text} ] newest-first, capped 30
"""

import json
import os
import re
import sys
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
    {"slug": "docs-curation",      "domain": "ai-infrastructure"},
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


def extract_next_step(status_path: Path) -> str:
    """
    Extract the narrative text from the '## Next step' section of STATUS.md.
    Returns the stripped text or an empty string if not found.
    """
    try:
        text = status_path.read_text(encoding="utf-8")
    except OSError:
        return ""
    m = re.search(
        r"^## Next step\s*\n(.*?)(?=\n## |\Z)", text, re.MULTILINE | re.DOTALL
    )
    if m:
        return m.group(1).strip()
    return ""


def build_org_chart(departments: list) -> str:
    """
    Generate a simple ASCII org chart with project-manager at the root and
    departments as branches, grouped by domain.
    """
    ai_depts = [d["slug"] for d in departments if d["domain"] == "ai-infrastructure"]
    web_depts = [d["slug"] for d in departments if d["domain"] == "web-app"]

    lines = [
        "project-manager (coordinator)",
        "|",
        "+-- AI-infrastructure domain",
    ]
    for i, slug in enumerate(ai_depts):
        prefix = "|   +-- " if i < len(ai_depts) - 1 else "|   `-- "
        lines.append(prefix + slug)
    lines.append("|")
    lines.append("`-- Web-app domain")
    for i, slug in enumerate(web_depts):
        prefix = "    +-- " if i < len(web_depts) - 1 else "    `-- "
        lines.append(prefix + slug)

    return "\n".join(lines)


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

def collect_adrs(decisions_dir: Path) -> list:
    """
    Parse frontmatter from ADR-*.md files. Returns list of dicts with
    id, adr, title, status, date.
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
        })
    adrs.sort(key=lambda x: x["adr"])
    return adrs


# ---------------------------------------------------------------------------
# Main ETL
# ---------------------------------------------------------------------------

def run_etl(repo_root: Path, served_dir: Path) -> None:
    pm_dir = repo_root / "ai-infrastructure" / "project-manager"
    status_path = pm_dir / "STATUS.md"
    tasks_root = pm_dir / "tasks"
    decisions_dir = pm_dir / "decisions"
    observations_path = pm_dir / "OBSERVATIONS.md"
    commands_dir = repo_root / ".claude" / "commands"

    # -- (a) Coordinator STATUS frontmatter ---------------------------------
    coordinator_fm = parse_frontmatter(status_path)
    current_phase = int(coordinator_fm.get("phase", 0))
    current_phase_title = str(coordinator_fm.get("phase_title", ""))
    last_updated = str(coordinator_fm.get("last_updated", ""))
    next_step = extract_next_step(status_path)

    # -- (a) Roadmap ---------------------------------------------------------
    roadmap_raw = coordinator_fm.get("roadmap", [])
    if not isinstance(roadmap_raw, list):
        roadmap_raw = []
    roadmap = []
    for item in roadmap_raw:
        if not isinstance(item, dict):
            continue
        phase_num = int(item.get("phase", 0))
        deliverables = item.get("deliverables", "")
        if isinstance(deliverables, list):
            deliverables = "; ".join(str(d) for d in deliverables)
        roadmap.append({
            "phase": phase_num,
            "title": str(item.get("title", "")),
            "deliverables": str(deliverables),
            "status": derive_roadmap_status(phase_num, current_phase),
        })

    # -- (d) Shared task pool ------------------------------------------------
    all_tasks = collect_tasks(tasks_root)
    overall_task_counts = compute_task_counts(all_tasks)

    # -- (e) ADRs ------------------------------------------------------------
    adrs = collect_adrs(decisions_dir)

    # -- (f) Observations count ----------------------------------------------
    observations_count = count_observations(observations_path)

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
            "phase": fm.get("phase"),
            "last_updated": str(fm.get("last_updated", "")),
        }

    departments = []
    for entry in DEPARTMENTS_ROSTER:
        slug = entry["slug"]
        label = f"dept:{slug}"
        exists = dept_exists(slug)
        task_counts = compute_task_counts(all_tasks, label_prefix=label)
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

    # -- Org chart -----------------------------------------------------------
    org_chart = build_org_chart(DEPARTMENTS_ROSTER)

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
        "task_counts": compute_task_counts(
            all_tasks, label_prefix=f"dept:{COORDINATOR_SLUG}"
        ),
    }

    # Department details
    for entry in DEPARTMENTS_ROSTER:
        slug = entry["slug"]
        exists = dept_exists(slug)
        label = f"dept:{slug}"
        task_counts = compute_task_counts(all_tasks, label_prefix=label)

        if not exists:
            workspace_details[slug] = {
                "header": {
                    "slug": slug,
                    "display_name": slug_to_display(slug),
                    "domain": entry["domain"],
                    "role": "department",
                    "exists": False,
                    "planned": True,
                    "phase": None,
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
                    "phase": fm.get("phase"),
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
        "org_chart": org_chart,
        "departments": departments,
        "coordinator": coordinator,
        "workspace_details": workspace_details,
        "recent_activity": recent_activity,
    }

    served_dir.mkdir(parents=True, exist_ok=True)
    out_path = served_dir / "data.json"
    out_path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    print(f"ETL: wrote {out_path} ({out_path.stat().st_size} bytes)", flush=True)


if __name__ == "__main__":
    repo_root = Path(os.environ.get("REPO_ROOT", "/repo"))
    served_dir = Path(os.environ.get("SERVED_DIR", "/served"))
    if not repo_root.exists():
        print(f"ETL error: REPO_ROOT {repo_root} does not exist", file=sys.stderr)
        sys.exit(1)
    run_etl(repo_root, served_dir)
