#!/usr/bin/env python3
"""Extract what the user typed in agent sessions over a date window.

Used by ``/dream``'s rule-learning pass. Reads the IDE agent and Claude Code transcripts that
``find-transcripts.py`` locates, keeps the user's own turns and drops everything the harness
injects under the user role — tool results, system reminders, attached skill bodies, task
notifications, slash-command envelopes, compaction summaries — so a reader sees the
corrections and conventions the user actually stated.

Output: Markdown, one ``##`` heading per session (date, source, project slug, session title,
then the transcript path, so a reader can open the full conversation around a turn) and one
bullet per turn: ``HH:MM`` plus the text, whitespace collapsed, long turns truncated, followed
by an excerpt of the agent's last words before it — the context a correction answers.
Sessions and turns are in chronological order. With ``--out-dir`` the turns go to
one file per ISO week (``turns-<YYYY>-W<ww>.md``) and the file paths are printed one per
line; without it everything goes to stdout.
"""
import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from importlib.util import module_from_spec, spec_from_file_location
from operator import attrgetter
from pathlib import Path

# Dashed filename, so load the locator via importlib (same as its tests do). Its helpers are
# module-private by naming only; this sibling is one of their intended callers.
# pylint: disable=protected-access
_spec = spec_from_file_location(
    "find_transcripts", Path(__file__).resolve().with_name("find-transcripts.py")
)
ft = module_from_spec(_spec)
_spec.loader.exec_module(ft)

DEFAULT_WINDOW_DAYS = 31
MAX_TURN_CHARS = 1500
MAX_CONTEXT_CHARS = 300

# Payloads the harness injects under the user role, matched on the stripped text's prefix.
_INJECTED_PREFIXES = (
    "<task-notification",
    "<ci-monitor-event",  # the desktop app's PR-watch events
    "<side-sessions-event",  # the desktop app's notes from sessions this one started
    "<local-command-",
    "<command-name>",
    "<command-message>",
    "<scheduled-task",
    "<artifact-view-context",
    "<create-pr-command",
    "<ide_opened_file",
    "<bash-stdout",  # output of a `!` shell command, saved under the user role
    "<bash-stderr",
    "Base directory for this skill:",
    "[Request interrupted by user",
    "Your response above was cut off mid-stream",
)
# Envelopes the harness appends to or wraps around a user entry: Claude Code's
# <system-reminder>, and the IDE agent's envelopes from find-transcripts.py's TODO block.
_ENVELOPE_TAGS = "|".join(map(re.escape, ("system-reminder", *ft.IDE_ENVELOPE_TAGS)))
_ENVELOPE_RE = re.compile(rf"<({_ENVELOPE_TAGS})>.*?</\1>", re.DOTALL)
# Text the user pasted, which may carry instructions they did not write. The harness tags the
# block with a random id so the paste cannot close its own envelope; only the tag with the same
# id ends it.
_PASTED_RE = re.compile(r'<pasted_content id="([^"]+)">.*?</pasted_content id="\1">', re.DOTALL)


@dataclass
class Turn:
    """One thing the user typed, with what the agent had last said before it."""
    when: datetime
    source: str
    slug: str
    title: str
    path: Path
    text: str
    context: str


def user_turn_text(entry: dict) -> str | None:
    """The user's own text in a transcript entry, or None when the entry is harness-injected."""
    if ft._entry_role(entry) != "user" or entry.get("isMeta") or entry.get("isCompactSummary"):
        return None
    text = ft._unwrap_ide_payload(ft._extract_user_text(entry))
    text = _PASTED_RE.sub("", _ENVELOPE_RE.sub("", text)).strip()
    if not text or text.startswith(_INJECTED_PREFIXES):
        return None
    # A bare slash command ("/lgtm") is an invocation, not something the user said.
    if text.startswith("/") and len(text.split()) == 1:
        return None
    return text


def _entry_time(entry: dict, fallback: datetime) -> datetime:
    stamp = entry.get("timestamp")
    if not stamp:
        return fallback
    return datetime.fromisoformat(stamp.replace("Z", "+00:00")).astimezone().replace(tzinfo=None)


def _session_slug(source: str, path: Path) -> str:
    # IDE agent: <slug>/<transcripts-dir>/<sid>/<sid>.jsonl; Claude Code: <slug>/<uuid>.jsonl
    return path.parents[2].name if source == "ide" else path.parent.name


def _first_turn_time(turns: list[Turn]) -> datetime:
    return turns[0].when


def collect_turns(sessions: list[tuple[str, Path]], since: datetime, until: datetime) -> list[Turn]:
    """User turns of the given (source, path) sessions whose time falls in [since, until).

    Sessions are ordered by their first turn in the window and kept whole, so a reader
    follows one conversation at a time even when sessions ran in parallel.
    """
    per_session: list[list[Turn]] = []
    for source, path in sessions:
        mtime = datetime.fromtimestamp(path.stat().st_mtime)
        if mtime < since or ft._is_trivial_session(path):
            continue
        slug = _session_slug(source, path)
        title = None
        context = ""
        turns: list[Turn] = []
        try:
            with path.open() as handle:
                for line in handle:
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if ft._entry_role(entry) == "assistant":
                        # A tool-only assistant turn keeps the last words that preceded it.
                        context = " ".join(ft._extract_user_text(entry).split()) or context
                        continue
                    text = user_turn_text(entry)
                    if text is None:
                        continue
                    # The session's first real turn names it, whether or not it is in the window.
                    title = title or " ".join(text.split())[:120]
                    when = _entry_time(entry, mtime)
                    if since <= when < until:
                        turns.append(Turn(when, source, slug, title, path, text, context))
        except OSError as exc:
            print(f"warning: cannot read {path}: {exc}", file=sys.stderr)
        if turns:
            turns.sort(key=attrgetter("when"))
            per_session.append(turns)
    per_session.sort(key=_first_turn_time)
    return [turn for turns in per_session for turn in turns]


def _clip(text: str, limit: int) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[:limit] + " […]"


def render(turns: list[Turn], max_turn_chars: int = MAX_TURN_CHARS) -> str:
    """Markdown: a heading per session (in order of its first turn), a bullet per turn."""
    lines: list[str] = []
    current = None
    for turn in turns:
        if turn.path != current:
            current = turn.path
            lines.append(f"\n## {turn.when:%Y-%m-%d} {turn.source} {turn.slug} — {turn.title}\n")
            lines.append(f"transcript: {turn.path}\n")
        lines.append(f"- {turn.when:%H:%M} {_clip(turn.text, max_turn_chars)}")
        if turn.context:
            lines.append(f"  (answering the agent's: {_clip(turn.context, MAX_CONTEXT_CHARS)})")
    return "\n".join(lines).strip() + "\n" if lines else ""


def write_weekly(turns: list[Turn], out_dir: Path, max_turn_chars: int) -> list[Path]:
    """One file per ISO week, chronological; returns the paths written."""
    by_week: dict[str, list[Turn]] = {}
    for turn in turns:
        by_week.setdefault(turn.when.strftime("%G-W%V"), []).append(turn)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for week in sorted(by_week):
        path = out_dir / f"turns-{week}.md"
        path.write_text(render(by_week[week], max_turn_chars))
        paths.append(path)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--since", default=None,
        help=f"First day of the window (YYYY-MM-DD); default: {DEFAULT_WINDOW_DAYS} days ago.",
    )
    parser.add_argument("--until", default=None, help="Last day of the window, inclusive.")
    parser.add_argument(
        "--workspace-substring", default="",
        help="Only projects whose slug contains this substring (default: all).",
    )
    parser.add_argument("--out-dir", default=None, help="Write one file per ISO week here.")
    parser.add_argument("--max-turn-chars", type=int, default=MAX_TURN_CHARS)
    args = parser.parse_args()

    if args.since:
        since = datetime.fromisoformat(args.since)
    else:
        first_day = date.today() - timedelta(days=DEFAULT_WINDOW_DAYS)
        since = datetime.combine(first_day, datetime.min.time())
    # Both bounds are exclusive at the end: an --until day runs through its last second.
    until = datetime.fromisoformat(args.until) + timedelta(days=1) if args.until else datetime.max

    substrings = {args.workspace_substring}
    sessions: list[tuple[str, Path]] = []
    for d in ft._find_ide_transcript_dirs(substrings):
        sessions.extend(("ide", p) for p in ft._list_jsonl_files_ide(d))
    for d in ft._find_claude_project_dirs(substrings):
        sessions.extend(("claude", p) for p in ft._list_jsonl_files_claude(d))

    turns = collect_turns(sessions, since, until)
    if args.out_dir:
        for path in write_weekly(turns, Path(args.out_dir), args.max_turn_chars):
            print(path)
    else:
        sys.stdout.write(render(turns, args.max_turn_chars))


if __name__ == "__main__":
    main()
