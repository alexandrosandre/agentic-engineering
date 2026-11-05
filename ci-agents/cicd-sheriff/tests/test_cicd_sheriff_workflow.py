#!/usr/bin/env python3
"""Regression tests for the scheduled CI sheriff workflow.

Paths resolve against this folder (workflow.yml, skills/); in an adopting repository point
WORKFLOW and SKILL at .github/workflows/cicd-sheriff.yml and skills/cicd-sheriff/SKILL.md.
"""
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
WORKFLOW = HERE / "workflow.yml"
SKILL = HERE / "skills/cicd-sheriff/SKILL.md"


def job_body(workflow: str, name: str) -> str:
    """Extract one top-level job from the workflow text."""
    match = re.search(
        rf"^  {re.escape(name)}:\n(?P<body>.*?)(?=^  [a-zA-Z0-9_-]+:\n|\Z)",
        workflow,
        re.MULTILINE | re.DOTALL,
    )
    if not match:
        raise AssertionError(f"{name} job not found")
    return match.group("body")


class CicdSheriffWorkflowTests(unittest.TestCase):
    """Lock the workflow's scheduling and side-effect boundaries."""

    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text()

    def test_runs_three_times_on_weekdays_and_supports_manual_detection(self):
        """The cron covers the requested hours and manual runs default to detection."""
        self.assertIn('cron: "0 7,11,15 * * 1-5"', self.workflow)
        self.assertRegex(
            self.workflow,
            r"workflow_dispatch:\n(?:.*\n)*?      repair:\n"
            r"(?:.*\n)*?        type: boolean\n(?:.*\n)*?        default: false",
        )
        self.assertIn("pull_request:", self.workflow)
        self.assertIn("github.event.pull_request.number || 'repair'", self.workflow)
        self.assertIn(
            "cancel-in-progress: ${{ github.event_name == 'pull_request' }}",
            self.workflow,
        )

    def test_detector_exercises_the_checker_without_repair_permissions(self):
        """Pull requests must test detection without exposing repair capabilities."""
        detector = job_body(self.workflow, "detect")
        self.assertIn("python -m unittest discover -s ci/tests", detector)
        self.assertIn("python3 ci/check_readme_workflows.py --json", detector)
        self.assertNotIn("contents: write", detector)
        self.assertNotIn("pull-requests: write", detector)

    def test_repair_runs_only_for_scheduled_or_explicit_manual_requests(self):
        """A pull request must never launch the autonomous repair agent."""
        repair = job_body(self.workflow, "repair")
        self.assertIn("needs.detect.outputs.red == 'true'", repair)
        self.assertIn("github.event_name == 'schedule'", repair)
        self.assertIn("github.event_name == 'workflow_dispatch'", repair)
        self.assertIn("inputs.repair == true &&", repair)
        self.assertIn("github.ref == 'refs/heads/master'", repair)
        self.assertNotIn("github.event_name == 'pull_request'", repair)
        self.assertIn(
            "CICD_SHERIFF_HANDOFF: ${{ github.workspace }}/.cicd-sheriff-handoff.txt",
            repair,
        )
        self.assertIn(".git/info/exclude", repair)

    def test_repair_agent_authenticates_as_the_agent_app(self):
        """GitHub forbids the Actions token from opening PRs, so the agent needs the app token."""
        repair = job_body(self.workflow, "repair")
        self.assertIn("id-token: write", repair)
        self.assertIn("additional_permissions", repair)
        self.assertNotIn("github_token: ${{ github.token }}", repair)
        agent_step = repair.split("- name: Diagnose and repair red workflows", 1)[1].split(
            "- name: Post intervention", 1
        )[0]
        self.assertNotIn("GH_TOKEN:", agent_step)
        # The skill's one re-run command reads this name; an empty value fails silently.
        self.assertIn("GH_RERUN_TOKEN:", agent_step)
        # The skill requests this reviewer; without it the PR has no human owner.
        self.assertIn("CICD_SHERIFF_REVIEWER:", agent_step)

    def test_prompt_and_chat_handoff_have_single_sources(self):
        """The agent reads the committed prompt and never receives the chat secret."""
        repair = job_body(self.workflow, "repair")
        agent_step, chat_step = repair.split("- name: Post intervention", 1)
        self.assertIn("routines/cicd-sheriff/PROMPT.md", agent_step)
        self.assertNotIn("CHAT_BOT_TOKEN", agent_step)
        self.assertIn("secrets.CHAT_BOT_TOKEN", chat_step)
        self.assertIn("if: always()", chat_step)

    def test_third_party_actions_are_pinned_to_commits(self):
        """Repair credentials must never reach code behind a mutable action tag."""
        mutable_uses = re.findall(
            r"^\s*uses: [^@\n]+@(?![0-9a-f]{40}(?:\s|$))",
            self.workflow,
            re.MULTILINE,
        )
        self.assertEqual(mutable_uses, [])

    def test_fix_prs_request_the_designated_reviewer_after_autoreview(self):
        """Every completed repair PR must request the team's human reviewer."""
        self.assertIn("$CICD_SHERIFF_REVIEWER", SKILL.read_text())


if __name__ == "__main__":
    unittest.main()
