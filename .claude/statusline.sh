#!/usr/bin/env bash
# Claude Code statusLine for Corral.
#
# Renders: "<model> · ⚡ <effort> · 🧠 <ctx>% · <dir> (<branch>)".
#
# Receives session metadata as JSON on stdin; emits one line on stdout. Advisory: any
# failure degrades gracefully (a missing field just drops its segment; the line still
# renders).
set -uo pipefail

input="$(cat)"

proj="$(printf '%s' "$input" | jq -r '.workspace.current_dir // .cwd // ""' 2>/dev/null || true)"
[ -z "$proj" ] && proj="${CLAUDE_PROJECT_DIR:-$PWD}"

model="$(printf '%s' "$input" | jq -r '.model.display_name // "Claude"' 2>/dev/null || echo Claude)"
effort="$(printf '%s' "$input" | jq -r '.effort.level // empty' 2>/dev/null || true)"
dir="$(basename "$proj")"
branch="$(git -C "$proj" rev-parse --abbrev-ref HEAD 2>/dev/null || true)"

# Context-window usage %, derived from the session transcript: the latest main-chain
# (non-sidechain) assistant turn's usage carries the live prompt size as
# input + cache_creation + cache_read tokens — the same sum /context reports. Denominator
# is the model's context limit (1M variants advertise "1M" in the display name; else 200k).
transcript="$(printf '%s' "$input" | jq -r '.transcript_path // empty' 2>/dev/null || true)"
ctx=""
if [ -n "$transcript" ] && [ -f "$transcript" ]; then
  case "$model" in *1M*|*1m*) limit=1000000 ;; *) limit=200000 ;; esac
  used="$(grep '"usage"' "$transcript" 2>/dev/null \
    | jq -s 'map(select(.isSidechain != true and (.message.usage.input_tokens? != null)))
             | last.message.usage
             | (.input_tokens + (.cache_creation_input_tokens // 0) + (.cache_read_input_tokens // 0))' \
        2>/dev/null || true)"
  if [ -n "$used" ] && [ "$used" -gt 0 ] 2>/dev/null; then
    ctx="🧠 $(( used * 100 / limit ))%"
  fi
fi

line="$model"
[ -n "$effort" ] && line="$line · ⚡ $effort"
[ -n "$ctx" ] && line="$line · $ctx"
line="$line · $dir"
[ -n "$branch" ] && line="$line ($branch)"
printf '%s\n' "$line"
