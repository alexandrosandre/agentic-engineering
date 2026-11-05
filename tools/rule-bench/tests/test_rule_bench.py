"""Tests for rule-bench.py: reading a headless run and comparing arms."""
import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_SCRIPT_PATH = Path(__file__).resolve().parents[1] / "rule-bench.py"
_spec = spec_from_file_location("rule_bench", _SCRIPT_PATH)
rb = module_from_spec(_spec)
_spec.loader.exec_module(rb)


def test_parse_stream_keeps_answer_cost_and_tool_calls():
    """Goal: a stream-json run yields the final answer, its cost and every tool the agent called."""
    stream = "\n".join(json.dumps(event) for event in [
        {"type": "system", "subtype": "init"},
        {"type": "assistant", "message": {"content": [
            {"type": "text", "text": "Looking."},
            {"type": "tool_use", "name": "Bash", "input": {"command": "git log -1"}}]}},
        {"type": "user", "message": {"content": [{"type": "tool_result", "content": "abc"}]}},
        {"type": "result", "result": "Because of X.", "is_error": False,
         "total_cost_usd": 0.42, "duration_ms": 9000, "num_turns": 3},
    ]) + "\nnot json"
    record = rb.parse_stream(stream)
    assert record["answer"] == "Because of X."
    assert record["is_error"] is False
    assert record["cost_usd"] == 0.42
    assert [call["name"] for call in record["tool_calls"]] == ["Bash"]


def test_run_without_result_event_counts_as_error():
    """Goal: a run that died before its result event is an error, never a graded empty answer."""
    assert rb.parse_stream('{"type": "system"}')["is_error"] is True


def test_case_passes_on_majority_of_graded_repeats():
    """Goal: a case passes for an arm only when most graded repeats score fully."""
    assert rb.case_passes([{"score": 1.0}, {"score": 1.0}, {"score": 0.5}])
    assert not rb.case_passes([{"score": 1.0}, {"score": 0.5}, {"score": 0.0}])
    assert not rb.case_passes([{"is_error": True}])


def test_mcnemar_exact_p_values():
    """Goal: the paired test matches the exact binomial values for small discordant counts."""
    assert rb.mcnemar_p(0, 0) == 1.0
    assert rb.mcnemar_p(0, 5) == 0.0625
    assert rb.mcnemar_p(1, 4) == 0.375


def test_off_limits_paths_are_denied_and_flag_contaminated_runs(tmp_path):
    """Goal: an off-limits file and directory are denied to Read, themselves and below."""
    answers = tmp_path / "answers"
    answers.mkdir()
    transcript = tmp_path / "session.jsonl"
    transcript.write_text("{}")
    spec = {"max_turns": 5, "off_limits": [str(answers), str(transcript)]}
    command = rb.claude_command(spec, "why?", "m")
    for rule in (f"Read(/{answers})", f"Read(/{answers}/**)", f"Read(/{transcript})"):
        assert rule in command
    named = {"tool_calls": [{"name": "Bash", "input": f'{{"command": "cat {transcript}"}}'}]}
    assert rb.contaminated(named, spec["off_limits"])


def _stream_with_output(command, output):
    return "\n".join(json.dumps(event) for event in [
        {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": command}}]}},
        {"type": "user", "message": {"content": [
            {"type": "tool_result", "tool_use_id": "t1", "content": output}]}},
        {"type": "result", "result": "done", "is_error": False},
    ])


def test_output_reaching_off_limits_is_caught_on_the_full_text(tmp_path):
    """Goal: a search printing a file inside an off-limits directory, or an off-limits file
    itself, counts even past the stored clip; a bare directory listing or a transcript
    listing does not."""
    answers = tmp_path / "answers"
    answers.mkdir()
    off_limits = [str(answers), str(tmp_path / "session.jsonl")]
    (tmp_path / "session.jsonl").write_text("{}")
    far_hit = "x" * 5000 + f" {answers}/s.jsonl: the reason"
    assert rb.contaminated(rb.parse_stream(_stream_with_output("grep -r 20 ~", far_hit),
                                           off_limits), off_limits)
    file_hit = "session.jsonl:42: the reason"
    assert rb.contaminated(rb.parse_stream(_stream_with_output("grep -r 20 ~", file_hit),
                                           off_limits), off_limits)
    listing = rb.parse_stream(_stream_with_output("ls ~/x", "answers\nother"), off_limits)
    assert not rb.contaminated(listing, off_limits)
    sessions = rb.parse_stream(
        _stream_with_output("find-transcripts.py --list", f"{answers}/s.jsonl"), off_limits)
    assert not rb.contaminated(sessions, off_limits)


def test_a_long_command_naming_an_off_limits_path_late_is_caught(tmp_path):
    """Goal: the input check runs on the full command, not the stored 2,000-character clip."""
    answers = tmp_path / "answers"
    answers.mkdir()
    command = "echo " + "y" * 3000 + f" && cat {answers}/s.jsonl"
    record = rb.parse_stream(_stream_with_output(command, "the reason"), [str(answers)])
    assert rb.contaminated(record, [str(answers)])


def test_a_listing_piped_into_a_read_is_still_checked(tmp_path):
    """Goal: only a bare transcript listing is exempt; a listing chained into a search is not."""
    answers = tmp_path / "answers"
    answers.mkdir()
    hit = f"{answers}/s.jsonl: the reason"
    chained = rb.parse_stream(
        _stream_with_output("find-transcripts.py --list | xargs grep reason", hit), [str(answers)])
    assert rb.contaminated(chained, [str(answers)])


def test_an_output_directory_keeps_the_commit_of_its_first_run(tmp_path):
    """Goal: a resume reuses the recorded commit even after the ref moved; a changed spec is
    refused."""
    spec = {"ref": "origin/master", "arms": [{"name": "a", "files": {}}], "cases": []}
    (tmp_path / "experiment.json").write_text(
        json.dumps({"spec": rb.spec_fingerprint(spec), "ref": "origin/master", "sha": "abc123"}))
    assert rb.check_out_dir(spec, tmp_path) == "abc123"
    changed = dict(spec, ref="origin/other")
    try:
        rb.check_out_dir(changed, tmp_path)
        raise AssertionError("a changed spec was accepted")
    except SystemExit:
        pass
