#!/usr/bin/env python3
"""Locate agent session transcripts for a given workspace.

Used by ``/contextual-review`` Phase 1 to populate ``TRANSCRIPT_PATHS``, by ``/snippets``
in list mode, and through its helpers by ``user-turns.py`` (the ``/dream`` rule-learning pass). Detects whether we are running in an IDE agent or a Claude Code
environment by looking for a project directory matching the workspace name
under ``<ide-agent-home>/projects`` and ``~/.claude/projects`` respectively.

Output: one absolute path per line on stdout, oldest-first (chronological
reading order). Empty stdout if no non-trivial transcripts are found. Exit
code is always 0; the caller decides what to do with empty output.

Layouts handled:

- IDE agent:  ``<ide-agent-home>/projects/<slug>/<transcripts-dir>/<session-id>/<session-id>.jsonl``
  (sample values; see the TODO block below)
- Claude Code: ``~/.claude/projects/<slug>/<session-uuid>.jsonl``

Filtering:

- Trivial sessions (whose first ~10 user entries are only meta-commands like
  ``/help``, ``/copy``, ``/compact``) are dropped.
- The most recent session is always included regardless of size; older sessions
  are added newest-first until the cumulative size exceeds 1 MB or 10 sessions
  are selected.

List mode (``--list``, used by ``/snippets``): instead of printing transcript
paths for one workspace, print one TSV row per non-trivial session across every
matching project — ``last-activity  source  project-slug  path  title`` — where
title is the first substantive user message. ``--since``/``--until`` bound the
last-activity date (inclusive, GitHub-style ``A..B`` semantics) and
``--workspace-substring`` filters project slugs. No session/size caps apply.
"""
import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

MAX_SESSIONS = 10
MAX_TOTAL_BYTES = 1_000_000

# Where Claude Code keeps its per-project session transcripts.
CLAUDE_HOME = Path.home() / ".claude"

# ---- TODO: the IDE agent's transcript format. ----
# The team also used an IDE-based agent. The values below are neutral samples, not any real
# agent's format: map them to your IDE agent's, or leave them and only Claude Code is read.
# Its sessions sit one folder deeper: <home>/projects/<slug>/<IDE_TRANSCRIPTS_DIR>/<sid>/<sid>.jsonl
IDE_AGENT_HOME = Path.home() / ".ide-agent"
IDE_TRANSCRIPTS_DIR = "transcripts"
# The wrapper around typed input, and the marker of a command invoked from the palette.
IDE_USER_INPUT_RE = re.compile(r"<user-input>\s*(.*?)\s*</user-input>", re.DOTALL)
IDE_PALETTE_COMMAND_RE = re.compile(r'<palette-command name="([^"]+)"')
# Envelopes it adds around or after typed input (reminders, attached files and skills); they
# are not the user's words.
IDE_ENVELOPE_TAGS = ("ide-reminder", "ide-attached-files", "ide-attached-skills")
# ---- End of the IDE agent's format. ----

# Meta-commands that, if they're the only user content, mark a session trivial.
_META_COMMANDS = frozenset({
    "/copy",
    "/help",
    "/clear",
    "/compact",
})

# How many of the earliest substantive user entries to inspect when classifying triviality.
_FIRST_USER_ENTRIES_TO_CHECK = 10


def _find_ide_transcript_dirs(workspace_substrings: set[str]) -> list[Path]:
    base = IDE_AGENT_HOME / "projects"
    if not base.is_dir():
        return []
    matches = []
    for project_dir in base.iterdir():
        if not project_dir.is_dir() or not _name_matches(project_dir.name, workspace_substrings):
            continue
        transcripts_dir = project_dir / IDE_TRANSCRIPTS_DIR
        if transcripts_dir.is_dir():
            matches.append(transcripts_dir)
    return matches


def _find_claude_project_dirs(workspace_substrings: set[str]) -> list[Path]:
    base = CLAUDE_HOME / "projects"
    if not base.is_dir():
        return []
    return [d for d in base.iterdir()
            if d.is_dir() and _name_matches(d.name, workspace_substrings)]


def _name_matches(dir_name: str, workspace_substrings: set[str]) -> bool:
    return any(substring in dir_name for substring in workspace_substrings)


def _list_jsonl_files_ide(transcripts_dir: Path) -> list[Path]:
    return [p for p in transcripts_dir.glob("*/*.jsonl") if "subagents" not in p.parts]


def _list_jsonl_files_claude(project_dir: Path) -> list[Path]:
    return [p for p in project_dir.glob("*.jsonl") if p.is_file()]


def _extract_user_text(entry: dict) -> str:
    # The IDE agent wraps payload under "message"; some other formats store "content"
    # directly on the entry. Try both.
    message = entry.get("message", entry)
    content = message.get("content", "") if isinstance(message, dict) else message
    if isinstance(content, list):
        # Each block may be a text block, a tool_use, etc. Only text blocks count.
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
            elif isinstance(block, str):
                parts.append(block)
        return " ".join(parts)
    return str(content)


def _entry_role(entry: dict) -> str | None:
    # IDE agent: role at top level. Claude Code: role nested under "message",
    # or "type" at top level. Try them in that order.
    role = entry.get("role")
    if role:
        return role
    message = entry.get("message")
    if isinstance(message, dict) and message.get("role"):
        return message["role"]
    return entry.get("type")


def _unwrap_ide_payload(text: str) -> str:
    # Strip the IDE agent's envelopes so the meta-command check sees the actual user input; a
    # palette-invoked command surfaces in its slash form.
    user_input_match = IDE_USER_INPUT_RE.search(text)
    if user_input_match:
        return user_input_match.group(1).strip()
    ide_command_match = IDE_PALETTE_COMMAND_RE.search(text)
    if ide_command_match:
        return f"/{ide_command_match.group(1)}"
    return text


def _is_trivial_session(jsonl_path: Path) -> bool:
    user_messages_seen = 0
    try:
        with jsonl_path.open() as handle:
            for line in handle:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if _entry_role(entry) != "user":
                    continue
                payload = _unwrap_ide_payload(_extract_user_text(entry)).strip()
                if not payload:
                    # Blank entries don't count toward the budget — they would
                    # let real work slip past the inspection window.
                    continue
                user_messages_seen += 1
                first_token = payload.split(maxsplit=1)[0]
                if first_token not in _META_COMMANDS:
                    return False
                if user_messages_seen >= _FIRST_USER_ENTRIES_TO_CHECK:
                    break
    except OSError as exc:
        print(f"warning: cannot read {jsonl_path}: {exc}", file=sys.stderr)
        return False
    return True


def _session_title(jsonl_path: Path) -> str:
    """First substantive user message, meta-commands skipped, collapsed to one line."""
    try:
        with jsonl_path.open() as handle:
            for line in handle:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if _entry_role(entry) != "user":
                    continue
                payload = _unwrap_ide_payload(_extract_user_text(entry)).strip()
                if not payload:
                    continue
                if payload.split(maxsplit=1)[0] in _META_COMMANDS:
                    continue
                return " ".join(payload.split())[:120]
    except OSError as exc:
        print(f"warning: cannot read {jsonl_path}: {exc}", file=sys.stderr)
    return "(untitled)"


def _list_sessions(workspace_substrings: set[str], since: str | None, until: str | None) -> None:
    candidates: list[tuple[str, Path]] = []
    for d in _find_ide_transcript_dirs(workspace_substrings):
        candidates.extend(("ide", p) for p in _list_jsonl_files_ide(d))
    for d in _find_claude_project_dirs(workspace_substrings):
        candidates.extend(("claude", p) for p in _list_jsonl_files_claude(d))

    since_ts = datetime.fromisoformat(since).timestamp() if since else None
    until_ts = (datetime.fromisoformat(until) + timedelta(days=1)).timestamp() if until else None
    rows = []
    for source, path in candidates:
        mtime = path.stat().st_mtime
        if since_ts and mtime < since_ts:
            continue
        if until_ts and mtime >= until_ts:
            continue
        if _is_trivial_session(path):
            continue
        rows.append((mtime, source, path))

    for mtime, source, path in sorted(rows):
        stamp = datetime.fromtimestamp(mtime).strftime("%Y-%m-%dT%H:%M")
        # IDE agent: <slug>/<transcripts-dir>/<sid>/<sid>.jsonl; Claude Code: <slug>/<uuid>.jsonl
        slug = path.parents[2].name if source == "ide" else path.parent.name
        print(f"{stamp}\t{source}\t{slug}\t{path}\t{_session_title(path)}")


def _modified_time(path: Path) -> float:
    return path.stat().st_mtime


def _select_sessions(jsonl_paths: list[Path]) -> list[Path]:
    newest_first = sorted(jsonl_paths, key=_modified_time, reverse=True)
    non_trivial = [p for p in newest_first if not _is_trivial_session(p)]
    if not non_trivial:
        return []
    selected = [non_trivial[0]]
    total_bytes = non_trivial[0].stat().st_size
    for path in non_trivial[1:]:
        if len(selected) >= MAX_SESSIONS:
            break
        size = path.stat().st_size
        if total_bytes + size > MAX_TOTAL_BYTES:
            break
        selected.append(path)
        total_bytes += size
    # Chronological order: oldest first
    return list(reversed(selected))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--workspace",
        default=None,
        help=(
            "Workspace directory whose name is used as a unique substring to "
            "match the project slug. Defaults to the current working directory."
        ),
    )
    parser.add_argument(
        "--list", action="store_true",
        help="List sessions across matching projects as TSV instead of printing "
             "transcript paths for one workspace.",
    )
    parser.add_argument(
        "--since", default=None,
        help="List mode: keep sessions whose last activity is on/after this date (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--until", default=None,
        help="List mode: keep sessions whose last activity is on/before this date (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--workspace-substring", default=None,
        help="List mode: only projects whose slug contains this substring (default: all).",
    )
    args = parser.parse_args()

    if args.list:
        substrings = {args.workspace_substring} if args.workspace_substring else {""}
        _list_sessions(substrings, args.since, args.until)
        return

    workspace = Path(args.workspace).resolve() if args.workspace else Path.cwd().resolve()
    # Claude Code slugifies project dirs by replacing '/', '.', and '_' with '-', so a worktree
    # or branch name containing underscores never appears verbatim in the slug. Match against
    # both the raw directory name and its '-'-normalized form.
    workspace_substrings = {workspace.name, re.sub(r"[_./]", "-", workspace.name)}

    candidates: list[Path] = []
    for d in _find_ide_transcript_dirs(workspace_substrings):
        candidates.extend(_list_jsonl_files_ide(d))
    for d in _find_claude_project_dirs(workspace_substrings):
        candidates.extend(_list_jsonl_files_claude(d))

    if not candidates:
        sys.exit(0)

    for path in _select_sessions(candidates):
        print(path)


if __name__ == "__main__":
    main()
