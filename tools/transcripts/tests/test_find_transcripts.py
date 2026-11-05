"""Regression tests for find-transcripts.py.

Cover both the IDE agent and Claude Code JSONL shapes plus the edge cases that
review-time bugs surfaced: schema-aware role detection, IDE agent
envelope unwrapping, and the blank-message budget bug.
"""
import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

# The script uses a dashed filename (matching the repository's dashed
# script names), so it can't be imported with a regular ``import``
# statement; load it via importlib.
_SCRIPT_PATH = Path(__file__).resolve().parents[1] / "find-transcripts.py"
_spec = spec_from_file_location("find_transcripts", _SCRIPT_PATH)
ft = module_from_spec(_spec)
_spec.loader.exec_module(ft)


def _write_jsonl(tmp_path: Path, name: str, entries: list[dict]) -> Path:
    """Write a JSONL file under ``tmp_path`` and return its path."""
    path = tmp_path / name
    with path.open("w") as handle:
        for entry in entries:
            handle.write(json.dumps(entry) + "\n")
    return path


# ---------- _entry_role ----------


def test_entry_role_ide_top_level():
    """Goal: the IDE agent stores role at the top of the entry."""
    assert ft._entry_role({"role": "user", "message": {"content": []}}) == "user"


def test_entry_role_claude_code_nested():
    """Goal: Claude Code nests role inside ``message``; top-level type may also be present."""
    entry = {"type": "user", "message": {"role": "user", "content": []}}
    assert ft._entry_role(entry) == "user"


def test_entry_role_claude_code_type_only():
    """Goal: when only top-level ``type`` is present, fall back to it."""
    assert ft._entry_role({"type": "user", "message": {"content": []}}) == "user"


def test_entry_role_assistant_is_not_user():
    """Goal: assistant entries surface as ``assistant`` so the caller can skip them."""
    assert ft._entry_role({"role": "assistant"}) == "assistant"


def test_entry_role_missing_returns_none():
    """Goal: malformed entries with no role information surface as ``None``."""
    assert ft._entry_role({"foo": "bar"}) is None


# ---------- _unwrap_ide_payload ----------


def test_unwrap_user_input_envelope():
    """Goal: the user-input wrapper is stripped, leaving the inner payload."""
    text = "<user-input>\n/help\n</user-input>"
    assert ft._unwrap_ide_payload(text) == "/help"


def test_unwrap_user_input_among_other_envelopes():
    """Goal: the user input is extracted even when other IDE agent envelopes precede it."""
    text = (
        "<ide-reminder>noise</ide-reminder>"
        "<ide-attached-files>more noise</ide-attached-files>"
        "<user-input>real ask here</user-input>"
    )
    assert ft._unwrap_ide_payload(text) == "real ask here"


def test_unwrap_ide_command_palette_invocation():
    """Goal: palette-invoked slash commands surface as ``/<name>``."""
    text = '<palette-command name="simplify">\n...details...\n</palette-command>'
    assert ft._unwrap_ide_payload(text) == "/simplify"


def test_unwrap_returns_text_when_no_envelopes():
    """Goal: Claude Code text (no IDE agent envelopes) passes through unchanged."""
    assert ft._unwrap_ide_payload("just plain text") == "just plain text"


# ---------- _is_trivial_session ----------


def _ide_user_entry(text: str) -> dict:
    """Build an IDE-agent-shape user entry containing the given text."""
    return {"role": "user", "message": {"content": [{"type": "text", "text": text}]}}


def _claude_user_entry(text: str) -> dict:
    """Build a Claude Code-shape user entry (nested role) containing the given text."""
    return {
        "type": "user",
        "message": {"role": "user", "content": [{"type": "text", "text": text}]},
    }


def test_is_trivial_ide_only_meta_commands(tmp_path):
    """Goal: an IDE agent session of only /help calls is trivial."""
    path = _write_jsonl(tmp_path, "s.jsonl", [
        _ide_user_entry("<user-input>/help</user-input>"),
        _ide_user_entry("<user-input>/help</user-input>"),
    ])
    assert ft._is_trivial_session(path) is True


def test_is_trivial_ide_with_real_work(tmp_path):
    """Goal: an IDE agent session with substantive content is not trivial, even if it leads with a meta-command."""
    path = _write_jsonl(tmp_path, "s.jsonl", [
        _ide_user_entry("<user-input>/help</user-input>"),
        _ide_user_entry("<user-input>actually let's add a feature instead</user-input>"),
    ])
    assert ft._is_trivial_session(path) is False


def test_is_trivial_claude_code_with_real_work(tmp_path):
    """Goal: Claude Code's nested-role schema is recognized; substantive sessions are not trivial."""
    path = _write_jsonl(tmp_path, "s.jsonl", [
        _claude_user_entry("/help"),
        _claude_user_entry("can you debug this stack trace?"),
    ])
    assert ft._is_trivial_session(path) is False


def test_is_trivial_claude_code_only_meta(tmp_path):
    """Goal: a Claude Code session of only meta-commands is trivial."""
    path = _write_jsonl(tmp_path, "s.jsonl", [
        _claude_user_entry("/help"),
        _claude_user_entry("/copy"),
    ])
    assert ft._is_trivial_session(path) is True


def test_is_trivial_blank_messages_dont_consume_budget(tmp_path):
    """Goal: blank user entries don't fill the inspection window and bury later real work.

    Without this fix, 10 blanks would trip the budget cap and a substantive entry
    at position 11 would be missed, marking the session trivial.
    """
    blanks = [_ide_user_entry("<user-input></user-input>")] * 10
    path = _write_jsonl(tmp_path, "s.jsonl", blanks + [
        _ide_user_entry("<user-input>real task at position 11</user-input>"),
    ])
    assert ft._is_trivial_session(path) is False


def test_is_trivial_assistant_entries_are_skipped(tmp_path):
    """Goal: assistant entries don't count toward the budget."""
    path = _write_jsonl(tmp_path, "s.jsonl", [
        {"role": "assistant", "message": {"content": [{"type": "text", "text": "hi"}]}},
        _ide_user_entry("<user-input>/help</user-input>"),
    ])
    assert ft._is_trivial_session(path) is True


def test_is_trivial_malformed_jsonl_lines_are_tolerated(tmp_path):
    """Goal: a corrupt line doesn't abort classification of the rest of the file."""
    path = tmp_path / "s.jsonl"
    with path.open("w") as handle:
        handle.write("{ not json }\n")
        handle.write(json.dumps(_ide_user_entry("<user-input>real work</user-input>")) + "\n")
    assert ft._is_trivial_session(path) is False


def test_is_trivial_unreadable_file_returns_false_and_warns(tmp_path, capsys):
    """Goal: OSError warns to stderr and returns False (unknown != trivial)."""
    path = tmp_path / "missing.jsonl"
    assert ft._is_trivial_session(path) is False
    captured = capsys.readouterr()
    assert "warning:" in captured.err
    assert "missing.jsonl" in captured.err


# ---------- _session_title (list mode) ----------


def test_session_title_skips_meta_commands_and_collapses_whitespace(tmp_path):
    """Goal: the title is the first substantive user message, not a leading meta-command."""
    path = _write_jsonl(tmp_path, "s.jsonl", [
        _ide_user_entry("<user-input>/help</user-input>"),
        _ide_user_entry("<user-input>Fix the  export\nretry bug</user-input>"),
    ])
    assert ft._session_title(path) == "Fix the export retry bug"


def test_session_title_untitled_when_no_substantive_message(tmp_path):
    """Goal: sessions with only meta-commands fall back to a placeholder title."""
    path = _write_jsonl(tmp_path, "s.jsonl", [
        _ide_user_entry("<user-input>/help</user-input>"),
    ])
    assert ft._session_title(path) == "(untitled)"
