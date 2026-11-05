#!/usr/bin/env python3
"""Replay real prompts through headless Claude Code under variants of the repo's agent rules.

Used to test whether a rule, a skill or nothing at all changes what an agent answers, before
the change lands (``/dream`` proposals, rule benchmarks). Each arm is a set of files laid over
``ref``; every case runs ``repeats`` times per arm, each run a new headless session in a clone
of its own, so nothing one run writes in its checkout reaches another (the provisioned
dependency folders are links into the main checkout and stay shared), and no session is
persisted, so the prompts never show up later as user turns in the transcripts ``/dream`` mines.

    rule-bench.py run    SPEC --out DIR [--arms A,B] [--cases id,...] [--repeats N] [--parallel K]
    rule-bench.py grade  SPEC --out DIR [--parallel K]
    rule-bench.py report SPEC --out DIR

SPEC is JSON::

    {
      "ref": "origin/master",
      "model": "claude-opus-5-5",
      "judge_model": "claude-opus-5-5",
      "max_turns": 60,
      "repeats": 3,
      "arms": [{"name": "today", "files": {}},
               {"name": "one-line", "files": {"AGENTS.md": "/abs/path/AGENTS.md"}}],
      "cases": [{"id": "flag-default", "prompt": "...", "rubric": "..."}]
    }

``files`` maps a repo path to the file that replaces (or adds) it in that arm. ``rubric`` is
what the blind judge grades against: the real answer, what a correct answer must contain, and
the plausible wrong one; the judge scores against whatever it says, so any rule about what an
agent answers fits. The judge sees one final answer at a time with no arm label, never the tool
calls, so the tool measures what an agent answers, not what it does.

Optional ``off_limits``: absolute paths (files or directories) that hold the answers, such as
the transcript of the session that wrote the cases. The Read tool is denied them, and a run whose
tool calls name one, or whose output prints one, is reported as contaminated and left out. The
check is best effort: a shell read through a wildcard that prints contents without file names
goes unnoticed, so keep answers out of reach where you can rather than relying on it.

An output directory belongs to one spec and one commit: the first ``run`` resolves ``ref`` and
records it, every later run and resume clones that same commit, and a changed spec needs a new
directory, which the tool enforces.

Isolation: each run's clone shares objects with this repository but has refs of its own and a
push URL that cannot work, and its overlay is folded into its commit, so every arm starts from a
clean tree and git commands run in the clone cannot move the real repository's branches or push.
The child's environment carries only the read-only cloud identity's resolved credentials and no
GitHub token, and the common git and GitHub write commands are denied by rule. Deny rules are
defaults, not a sandbox: rely on Claude Code's auto mode (MCP servers off, permission prompts
denied) to stop a deliberate write.

``claude_command`` builds the ``claude -p`` command line, whose ``stream-json`` output (assistant
messages with tool calls, tool results, and a final ``result`` event carrying the answer, cost and
duration) ``parse_stream`` reads.
"""
import argparse
import atexit
import functools
import hashlib
import json
import math
import operator
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUN_TIMEOUT_SECONDS = 1800
# What Claude Code answers instead of running once the account's usage window is spent.
LIMIT_MARKERS = ("hit your session limit", "hit your usage limit", "usage limit reached")
# Provisioned directories linked from the main checkout, so the session-start hook does not
# report an unprovisioned checkout and send the agent off to install dependencies.
PROVISIONED = [".venv", "web/node_modules"]
# `*` matches anywhere (code.claude.com/docs/en/permissions), so `gh * merge *` also catches
# `gh -R owner/repo pr merge 1`, and `git -C * push *` catches a push aimed at the main checkout;
# the plain `git push *` form also covers `cd <main checkout> && git push`, since each part of a
# compound command is checked. Git's any-position form is limited to -C and -c so reads such as
# `git grep config` stay allowed. A rule with two wildcards no longer matches the bare command,
# hence the bare form as well.
GIT_WRITE_VERBS = ("push", "commit", "reset", "checkout", "switch", "restore", "clean", "stash",
                   "merge", "rebase", "cherry-pick", "revert", "am", "apply", "tag", "update-ref",
                   "worktree", "remote", "config", "branch -d", "branch -D", "branch -f",
                   "branch -m")
GITHUB_WRITE_VERBS = ("comment", "create", "edit", "merge", "review", "close", "reopen", "ready",
                      "delete", "rerun", "cancel", "lock", "transfer", "update-branch", "develop",
                      "pin", "unpin", "enable", "disable", "item-add", "item-edit", "link")
# Whole gh command groups that write, denied with or without flags before them (`gh -R x api`).
GITHUB_WRITE_GROUPS = ("api", "workflow run", "release", "label", "secret", "variable", "repo",
                       "ssh-key", "gpg-key", "alias", "project", "auth", "extension", "gist")
DISALLOWED_TOOLS = [
    "Edit", "Write", "NotebookEdit", "Bash(rm *)",
    *(f"Bash(git {verb} *)" for verb in GIT_WRITE_VERBS),
    *(f"Bash(git {verb})" for verb in GIT_WRITE_VERBS),
    *(f"Bash(git {flag} * {verb}{tail})" for flag in ("-C", "-c") for verb in GIT_WRITE_VERBS
      for tail in (" *", "")),
    "Bash(git --git-dir*)", "Bash(git --work-tree*)",
    *(f"Bash(gh * {verb}{tail})" for verb in GITHUB_WRITE_VERBS for tail in (" *", "")),
    *(f"Bash(gh {group}{tail})" for group in GITHUB_WRITE_GROUPS for tail in (" *", "")),
    *(f"Bash(gh * {group}{tail})" for group in GITHUB_WRITE_GROUPS for tail in (" *", "")),
]
JUDGE_PROMPT = """You grade one answer a coding agent gave to a developer, against a rubric that says what is true and what the answer must do.

Question:
<<<
{prompt}
>>>

Rubric:
<<<
{rubric}
>>>

Answer to grade:
<<<
{answer}
>>>

Reply with JSON only, no prose around it:
{{"score": 1 when the answer satisfies everything the rubric requires, 0.5 when it satisfies part of it or hedges between it and what the rubric marks wrong, 0 otherwise,
  "invented": true when the answer states as established fact something the rubric contradicts, or something it only guessed, without marking it as inferred or unverified; details of what the code does are not inventions; else false,
  "reason": "one sentence"}}"""


# The login a fresh session still needs; every other CLAUDE_CODE_* variable describes the calling
# session and would make the child think it is part of it.
KEPT_CLAUDE_VARIABLES = ("CLAUDE_CODE_OAUTH_TOKEN",)
CLOUD_KEYS = ("CLOUD_ACCESS_KEY_ID", "CLOUD_SECRET_ACCESS_KEY", "CLOUD_SESSION_TOKEN")
# A token in the environment would let a script or curl write to GitHub past the gh deny rules;
# gh keeps its own login for reads.
GITHUB_TOKENS = ("GH_TOKEN", "GITHUB_TOKEN")
READ_ONLY_PROFILE = "READ_ONLY_PROFILE"


@functools.cache
def read_only_cloud_env():
    """Environment variables that give a session the read-only cloud identity and nothing else.

    The original resolves the read-only profile with the cloud provider's CLI into a private,
    temporary config and credentials file (mode 0600, removed at exit) holding only that
    identity, so a session can neither name a write-capable profile on the command line nor reach
    a profile the read-only one chains from.
    """
    # TODO: wire to your cloud provider's CLI: export the READ_ONLY_PROFILE credentials into a
    # private temporary file and return the variables that point the SDKs at it.
    folder = Path(tempfile.mkdtemp(prefix="rule-bench-cloud-"))
    atexit.register(shutil.rmtree, folder, ignore_errors=True)
    return {"CLOUD_PROFILE": READ_ONLY_PROFILE,
            "CLOUD_SHARED_CREDENTIALS_FILE": str(folder / "credentials")}


def child_env():
    """The parent's environment without its Claude Code session markers, cloud keys or GitHub
    tokens, seeing only the read-only cloud identity (AGENTS.md: agents read production with a
    read-only identity). ANTHROPIC_BASE_URL is dropped because a Claude Code host sets it to its
    own session's proxy."""
    env = {k: v for k, v in os.environ.items()
           if not ((k.startswith("CLAUDE_CODE_") and k not in KEPT_CLAUDE_VARIABLES)
                   or k in ("CLAUDECODE", "ANTHROPIC_BASE_URL", *CLOUD_KEYS, *GITHUB_TOKENS))}
    env.update(read_only_cloud_env())
    return env


def git(*args, cwd=REPO):
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True,
                          check=True).stdout.strip()


def main_checkout():
    porcelain = git("worktree", "list", "--porcelain")
    return Path(porcelain.splitlines()[0].split(" ", 1)[1])


def prepare_clone(arm, sha, path):
    """A clone of ``sha`` with the arm's files laid over it and no way to push."""
    subprocess.run(["git", "clone", "--quiet", "--shared", "--no-checkout", str(REPO), str(path)],
                   capture_output=True, text=True, check=True)
    git("checkout", "--quiet", "--detach", sha, cwd=path)
    git("remote", "set-url", "origin", git("remote", "get-url", "origin"), cwd=path)
    git("remote", "set-url", "--push", "origin", "no-push://disabled", cwd=path)
    checkout = main_checkout()
    for rel in PROVISIONED:
        if (checkout / rel).exists() and not (path / rel).exists():
            (path / rel).parent.mkdir(parents=True, exist_ok=True)
            (path / rel).symlink_to(checkout / rel)
    for rel, source in arm["files"].items():
        (path / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, path / rel)
    # Folding the overlay into the commit, in every arm alike, keeps the tree clean: a session
    # that starts with uncommitted changes is told to read them, which would point it at the
    # rule under test.
    if arm["files"]:
        git("add", "--", *arm["files"], cwd=path)
    git("-c", "commit.gpgsign=false", "commit", "--quiet", "--amend", "--no-edit", "--allow-empty",
        cwd=path)


def off_limits_rules(off_limits):
    """Read deny rules for each path itself and, for a directory, everything under it."""
    rules = []
    for path in map(Path, off_limits):
        rules += [f"Read(/{path})", f"Read(/{path}/**)"]
    return rules


def claude_command(spec, prompt, model, tools_off=False):
    command = ["claude", "-p", prompt, "--model", model, "--output-format", "stream-json",
               "--verbose", "--no-session-persistence", "--strict-mcp-config",
               "--permission-mode", "auto", "--permission-prompts", "none"]
    if tools_off:
        return command + ["--max-turns", "1", "--tools", ""]
    return command + ["--max-turns", str(spec["max_turns"]), "--disallowedTools",
                      *DISALLOWED_TOOLS, *off_limits_rules(spec.get("off_limits", []))]


def off_limits_markers(off_limits):
    """What a tool's output prints when it reached an off-limits path: a directory's name
    followed by a separator (a bare name in a listing reads nothing), or a file's name."""
    return [Path(p).name + "/" if Path(p).is_dir() else Path(p).name for p in off_limits]


def parse_stream(stdout, off_limits=()):
    """The run's answer, cost and tool calls. Each call is checked against the off-limits
    paths on its full input and output, before both are clipped for storage."""
    names = [Path(path).name for path in off_limits]
    markers = off_limits_markers(off_limits)
    tool_calls, result, by_id = [], {}, {}
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "assistant":
            for part in event.get("message", {}).get("content", []):
                if part.get("type") == "tool_use":
                    full_input = json.dumps(part.get("input"))
                    command = (part.get("input") or {}).get("command", "")
                    # Listing transcripts names every session without reading any; anything
                    # chained after the listing may read them, so only a bare listing is exempt.
                    listing_only = "find-transcripts" in command and not any(
                        sep in command for sep in ("|", "&", ";", "\n", "`", "$(", "xargs"))
                    call = {"name": part["name"], "input": full_input[:2000], "output": "",
                            "reached": any(name in full_input for name in names),
                            "listing_only": listing_only}
                    tool_calls.append(call)
                    if part.get("id"):
                        by_id[part["id"]] = call
        elif event.get("type") == "user":
            for part in event.get("message", {}).get("content", []):
                call = by_id.get(part.get("tool_use_id")) if isinstance(part, dict) else None
                if call is not None and part.get("type") == "tool_result":
                    output = json.dumps(part.get("content"))
                    if not call["listing_only"]:
                        call["reached"] |= any(marker in output for marker in markers)
                    call["output"] = output[:4000]
        elif event.get("type") == "result":
            result = event
    return {"answer": result.get("result", ""), "is_error": result.get("is_error", True),
            "cost_usd": result.get("total_cost_usd"), "duration_ms": result.get("duration_ms"),
            "num_turns": result.get("num_turns"), "tool_calls": tool_calls}


def run_one(spec, sha, arm, case, repeat, out, root):
    path = out / "runs" / f"{arm['name']}__{case['id']}__{repeat}.json"
    earlier_cost = 0
    if path.exists():
        earlier = json.loads(path.read_text())
        if not earlier["is_error"]:
            return
        earlier_cost = (earlier.get("cost_usd") or 0) + earlier.get("earlier_attempts_cost_usd", 0)
    clone = root / f"{arm['name']}__{case['id']}__{repeat}"
    prepare_clone(arm, sha, clone)
    try:
        proc = subprocess.run(claude_command(spec, case["prompt"], spec["model"]), cwd=clone,
                              stdin=subprocess.DEVNULL, capture_output=True, text=True,
                              env=child_env(), timeout=RUN_TIMEOUT_SECONDS, check=False)
        record = parse_stream(proc.stdout, spec.get("off_limits", []))
        record["stderr_tail"] = proc.stderr[-500:]
    except subprocess.TimeoutExpired:
        record = {"answer": "", "is_error": True, "timeout": True, "tool_calls": []}
    finally:
        shutil.rmtree(clone)
    limit_hit = any(marker in record["answer"] for marker in LIMIT_MARKERS)
    record.update({"arm": arm["name"], "case": case["id"], "repeat": repeat,
                   "earlier_attempts_cost_usd": earlier_cost,
                   "is_error": record["is_error"] or limit_hit})
    path.write_text(json.dumps(record, indent=1))
    print(f"{arm['name']} {case['id']} #{repeat}: error={record['is_error']} "
          f"cost={record.get('cost_usd')}", flush=True)
    if limit_hit:
        sys.exit(f"stopped: the usage limit was reached ({record['answer'][:120]}); rerun later "
                 "and the errored runs are retried")


def selected(items, names, key):
    return [item for item in items if not names or item[key] in names.split(",")]


def spec_fingerprint(spec):
    """Everything a run's answer depends on: the spec and the content of every arm file."""
    digest = hashlib.sha256(json.dumps(spec, sort_keys=True).encode())
    for arm in spec["arms"]:
        for rel in sorted(arm["files"]):
            digest.update(Path(arm["files"][rel]).read_bytes())
    return digest.hexdigest()


def check_out_dir(spec, out):
    """The commit an output directory's runs use, or None before its first run; refuses a
    directory whose runs were made under a different spec."""
    stamp = out / "experiment.json"
    if not stamp.exists():
        return None
    recorded = json.loads(stamp.read_text())
    if recorded["spec"] != spec_fingerprint(spec):
        sys.exit(f"{out} holds runs of a different spec; use a new --out directory")
    return recorded["sha"]


def command_run(spec, args):
    missing = [source for arm in spec["arms"] for source in arm["files"].values()
               if not Path(source).is_file()]
    if missing:
        sys.exit(f"arm files not found: {missing}")
    out = Path(args.out)
    sha = check_out_dir(spec, out)
    if sha is None:
        sha = git("rev-parse", spec["ref"])
        (out / "runs").mkdir(parents=True, exist_ok=True)
        (out / "experiment.json").write_text(
            json.dumps({"spec": spec_fingerprint(spec), "ref": spec["ref"], "sha": sha}))
    repeats = args.repeats or spec["repeats"]
    jobs = [(arm, case, r) for arm in selected(spec["arms"], args.arms, "name")
            for case in selected(spec["cases"], args.cases, "id") for r in range(1, repeats + 1)]
    root = Path(tempfile.mkdtemp(prefix="rule-bench-"))
    try:
        with ThreadPoolExecutor(max_workers=args.parallel) as pool:
            futures = [pool.submit(run_one, spec, sha, arm, case, r, out, root)
                       for arm, case, r in jobs]
            try:
                for future in as_completed(futures):
                    future.result()
            except BaseException:
                # Without this, leaving the block still starts every queued run.
                pool.shutdown(cancel_futures=True)
                raise
    finally:
        shutil.rmtree(root, ignore_errors=True)


def grade_one(spec, cases, path, cwd):
    record = json.loads(path.read_text())
    if "score" in record or record.get("is_error"):
        return
    case = cases[record["case"]]
    prompt = JUDGE_PROMPT.format(prompt=case["prompt"], rubric=case["rubric"],
                                 answer=record["answer"])
    proc = subprocess.run(claude_command(spec, prompt, spec["judge_model"], tools_off=True),
                          cwd=cwd, stdin=subprocess.DEVNULL,
                          capture_output=True, text=True,
                          env=child_env(), timeout=600, check=False)
    judged = parse_stream(proc.stdout)
    text = judged["answer"]
    if any(marker in text for marker in LIMIT_MARKERS):
        sys.exit(f"stopped grading: the usage limit was reached ({text[:120]}); rerun later")
    try:
        verdict = json.loads(text[text.index("{"): text.rindex("}") + 1])
    except ValueError:
        print(f"judge gave no verdict for {path.name}, left ungraded: {text[:120]}", flush=True)
        return
    record.update({"score": float(verdict["score"]), "invented": bool(verdict["invented"]),
                   "judge_reason": verdict["reason"], "judge_cost_usd": judged["cost_usd"]})
    path.write_text(json.dumps(record, indent=1))


def command_grade(spec, args):
    check_out_dir(spec, Path(args.out))
    cases = {case["id"]: case for case in spec["cases"]}
    paths = (Path(args.out) / "runs").glob("*.json")
    # An empty folder of our own: a judge session loads settings and CLAUDE.md from its cwd.
    with tempfile.TemporaryDirectory(prefix="rule-bench-judge-") as cwd, \
            ThreadPoolExecutor(max_workers=args.parallel) as pool:
        futures = [pool.submit(grade_one, spec, cases, p, cwd) for p in paths]
        try:
            for future in as_completed(futures):
                future.result()
        except BaseException:
            pool.shutdown(cancel_futures=True)
            raise


def mcnemar_p(only_first, only_second):
    """Two-sided exact McNemar p-value from the discordant pair counts."""
    n = only_first + only_second
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, k) for k in range(min(only_first, only_second) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def case_passes(records):
    """A case passes for an arm when most of its graded repeats score 1."""
    scores = [r["score"] for r in records if "score" in r]
    return bool(scores) and sum(s == 1 for s in scores) * 2 > len(scores)


def contaminated(record, off_limits):
    """True when a tool call named an off-limits path or its output printed one."""
    # The last component catches the same path written with ~ or relative to another directory.
    names = [Path(path).name for path in off_limits]
    return any(call.get("reached") or any(name in call["input"] for name in names)
               for call in record["tool_calls"])


def command_report(spec, args):
    check_out_dir(spec, Path(args.out))
    records = [json.loads(p.read_text()) for p in (Path(args.out) / "runs").glob("*.json")]
    off_limits = spec.get("off_limits", [])
    dirty = [r for r in records if contaminated(r, off_limits)]
    if dirty:
        print(f"contaminated runs left out: {[(r['arm'], r['case'], r['repeat']) for r in dirty]}")
    records = sorted((r for r in records if r not in dirty), key=operator.itemgetter("repeat"))
    arms = [arm["name"] for arm in spec["arms"] if any(r["arm"] == arm["name"] for r in records)]
    # Only cases with a graded run count, so unrun, errored and dropped cases are not failures.
    graded_cases = {arm: [c["id"] for c in spec["cases"] if any(
        r["arm"] == arm and r["case"] == c["id"] and "score" in r for r in records)]
        for arm in arms}
    passes = {}
    for arm in arms:
        mine = [r for r in records if r["arm"] == arm]
        graded = [r for r in mine if "score" in r]
        costs = [(r.get("cost_usd") or 0) + r.get("earlier_attempts_cost_usd", 0) for r in mine]
        seconds = [r["duration_ms"] / 1000 for r in mine if r.get("duration_ms")]
        cases = graded_cases[arm]
        passes[arm] = {c: case_passes([r for r in mine if r["case"] == c]) for c in cases}
        unstable = sum(len({r["score"] for r in graded if r["case"] == c}) > 1 for c in cases)
        print(f"{arm}: runs={len(mine)} errors={sum(bool(r.get('is_error')) for r in mine)} "
              f"cases passed={sum(passes[arm].values())}/{len(cases)} graded "
              f"mean score={statistics.mean(r['score'] for r in graded) if graded else 0:.2f} "
              f"invented={sum(r['invented'] for r in graded)}/{len(graded)} "
              f"cases with disagreeing repeats={unstable} "
              f"cost mean=${statistics.mean(costs) if costs else 0:.2f} "
              f"total=${sum(costs):.2f} "
              f"judge total=${sum(r.get('judge_cost_usd') or 0 for r in graded):.2f} "
              f"median minutes={statistics.median(seconds) / 60 if seconds else 0:.1f}")
    for case in [c["id"] for c in spec["cases"]]:
        cells = []
        for arm in arms:
            scores = [r.get("score") for r in records if r["arm"] == arm and r["case"] == case]
            cells.append(f"{arm}={scores}")
        print(f"  {case}: " + "  ".join(cells))
    for arm in arms[1:]:
        shared = [c for c in graded_cases[arm] if c in graded_cases[arms[0]]]
        only_base = sum(passes[arms[0]][c] and not passes[arm][c] for c in shared)
        only_arm = sum(passes[arm][c] and not passes[arms[0]][c] for c in shared)
        p_value = mcnemar_p(only_base, only_arm)
        print(f"{arm} vs {arms[0]} on {len(shared)} cases graded in both: cases only {arm} "
              f"passes={only_arm}, only {arms[0]} passes={only_base}, "
              f"exact McNemar p={p_value:.3f}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", maxsplit=1)[0])
    parser.add_argument("command", choices=["run", "grade", "report"])
    parser.add_argument("spec")
    parser.add_argument("--out", required=True)
    parser.add_argument("--arms", help="comma-separated arm names (default: all)")
    parser.add_argument("--cases", help="comma-separated case ids (default: all)")
    parser.add_argument("--repeats", type=int, help="override the spec's repeats")
    parser.add_argument("--parallel", type=int, default=3)
    args = parser.parse_args()
    spec = json.loads(Path(args.spec).read_text())
    {"run": command_run, "grade": command_grade, "report": command_report}[args.command](spec, args)


if __name__ == "__main__":
    sys.exit(main())
