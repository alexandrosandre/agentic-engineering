#!/usr/bin/env python3
"""Tests for the README workflow status checker."""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "check_readme_workflows.py"
SPEC = importlib.util.spec_from_file_location("check_readme_workflows", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class ReadmeWorkflowStatusTests(unittest.TestCase):
    """Verify discovery and status classification used by the CI sheriff."""

    def test_discovers_only_status_badges_above_the_readme_body(self):
        """The README badge block is the exact monitored workflow inventory."""
        readme = """### Live probes on staging
[![probe](https://github.com/example-org/example-repo/actions/workflows/probe.yml/badge.svg)](run)

### Code workflows
[![core](https://github.com/example-org/example-repo/actions/workflows/core.yml/badge.svg)](run)
-----------------------------
[![example](https://github.com/example-org/example-repo/actions/workflows/example.yml/badge.svg)](run)
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "README.md"
            path.write_text(readme)
            badges = MODULE.read_workflow_badges(path)

        self.assertEqual(
            [(badge.section, badge.name, badge.workflow) for badge in badges],
            [
                ("Live probes on staging", "probe", "probe.yml"),
                ("Code workflows", "core", "core.yml"),
            ],
        )

    def test_classifies_completed_and_active_runs(self):
        """Only successful completions are green; active runs remain pending."""
        badge = MODULE.WorkflowBadge("Code workflows", "core", "core.yml")
        common = {
            "html_url": "https://github.com/example-org/example-repo/actions/runs/1",
            "created_at": "2026-08-06T12:00:00Z",
            "head_sha": "abc",
            "display_title": "A merge",
        }

        green = MODULE.classify_run(
            badge, {**common, "status": "completed", "conclusion": "success"}
        )
        red = MODULE.classify_run(
            badge, {**common, "status": "completed", "conclusion": "cancelled"}
        )
        pending = MODULE.classify_run(
            badge, {**common, "status": "in_progress", "conclusion": None}
        )

        self.assertEqual((green.state, red.state, pending.state), ("green", "red", "pending"))

    def test_missing_runs_and_api_errors_are_distinct(self):
        """A missing badge result is red, while an unreadable result is a monitor error."""
        badge = MODULE.WorkflowBadge("Client workflows", "client", "client.yml")

        missing = MODULE.classify_run(badge, None)
        unreadable = MODULE.unreadable_status(badge, "GitHub API unavailable")

        self.assertEqual(missing.state, "red")
        self.assertEqual(unreadable.state, "unknown")
        self.assertEqual(MODULE.exit_code([missing]), 1)
        self.assertEqual(MODULE.exit_code([unreadable]), 2)

    def test_a_workflow_that_never_ran_anywhere_awaits_its_first_run(self):
        """A workflow merged with its badge is registered at once but runs only when its trigger
        fires (a post-deploy check, after the next deploy): until then it awaits its first run. One
        that has run elsewhere but never on master is still red."""
        badge = MODULE.WorkflowBadge("Live probes", "staging-smoke", "staging-smoke.yml")

        def latest(total_anywhere):
            def fake_run(command, **_kwargs):
                on_any_branch = not any(arg.startswith("branch=") for arg in command)
                count = total_anywhere if on_any_branch else 0
                body = f'{{"total_count": {count}, "workflow_runs": []}}'
                return MODULE.subprocess.CompletedProcess(command, 0, body, "")

            original = MODULE.subprocess.run
            MODULE.subprocess.run = fake_run
            try:
                return MODULE.query_latest_run("o/r", "master", badge)
            finally:
                MODULE.subprocess.run = original

        self.assertEqual(
            (latest(0).state, latest(0).status), ("pending", "awaiting_first_run")
        )
        self.assertEqual(latest(3).state, "red")

if __name__ == "__main__":
    unittest.main()
