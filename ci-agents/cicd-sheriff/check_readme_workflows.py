#!/usr/bin/env python3
"""Report the latest master run for every GitHub Actions badge in README.md."""
import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

# Installed as ci/check_readme_workflows.py, one level below the repository root.
REPO_ROOT = Path(__file__).resolve().parents[1]
BADGE_PATTERN = re.compile(
    r"\[!\[(?P<name>[^\]]+)\]\("
    r"https://github\.com/[^/]+/[^/]+/actions/workflows/"
    r"(?P<workflow>[^/)]+)/badge\.svg(?:\?[^)]*)?\)"
)


@dataclass(frozen=True)
class WorkflowBadge:
    """One status badge from the README inventory."""

    section: str
    name: str
    workflow: str


@dataclass(frozen=True)
class WorkflowStatus:
    """Latest run state for one monitored workflow."""

    section: str
    name: str
    workflow: str
    state: str
    status: str
    conclusion: str
    url: str
    created_at: str
    head_sha: str
    display_title: str
    error: str


def read_workflow_badges(readme_path: Path) -> list[WorkflowBadge]:
    """Read the badge block above the README body divider."""
    section = ""
    badges = []
    for line in readme_path.read_text().splitlines():
        if line.startswith("-----------------------------"):
            break
        if line.startswith("### "):
            section = line.removeprefix("### ").strip()
            continue
        match = BADGE_PATTERN.search(line)
        if match:
            badges.append(
                WorkflowBadge(
                    section=section,
                    name=match.group("name"),
                    workflow=match.group("workflow"),
                )
            )
    return badges


def classify_run(badge: WorkflowBadge, run: dict[str, Any] | None) -> WorkflowStatus:
    """Map a GitHub run to the green/red/pending state shown to the sheriff."""
    if run is None:
        return WorkflowStatus(
            section=badge.section,
            name=badge.name,
            workflow=badge.workflow,
            state="red",
            status="completed",
            conclusion="no_runs",
            url="",
            created_at="",
            head_sha="",
            display_title="",
            error="",
        )

    status = run.get("status") or "unknown"
    conclusion = run.get("conclusion") or ""
    if status != "completed":
        state = "pending"
    elif conclusion == "success":
        state = "green"
    else:
        state = "red"

    return WorkflowStatus(
        section=badge.section,
        name=badge.name,
        workflow=badge.workflow,
        state=state,
        status=status,
        conclusion=conclusion,
        url=run.get("html_url") or "",
        created_at=run.get("created_at") or "",
        head_sha=run.get("head_sha") or "",
        display_title=run.get("display_title") or "",
        error="",
    )


def unreadable_status(badge: WorkflowBadge, error: str) -> WorkflowStatus:
    """Represent a monitor failure without mislabeling the workflow red."""
    return WorkflowStatus(
        section=badge.section,
        name=badge.name,
        workflow=badge.workflow,
        state="unknown",
        status="unknown",
        conclusion="",
        url="",
        created_at="",
        head_sha="",
        display_title="",
        error=error,
    )


def awaiting_first_run(badge: WorkflowBadge) -> WorkflowStatus:
    """A badge whose workflow has not run yet: pending, not a red workflow."""
    return WorkflowStatus(
        section=badge.section,
        name=badge.name,
        workflow=badge.workflow,
        state="pending",
        status="awaiting_first_run",
        conclusion="",
        url="",
        created_at="",
        head_sha="",
        display_title="",
        error="",
    )


def query_latest_run(
    repository: str, branch: str, badge: WorkflowBadge
) -> WorkflowStatus:
    """Query the newest run for one workflow and branch."""
    command = [
        "gh",
        "api",
        "-X",
        "GET",
        f"repos/{repository}/actions/workflows/{badge.workflow}/runs",
        "-f",
        f"branch={branch}",
        "-f",
        "per_page=1",
    ]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
    except OSError as error:
        return unreadable_status(badge, str(error))
    if completed.returncode != 0:
        stderr = completed.stderr.strip()
        # GitHub registers a workflow only once it reaches the default branch or first runs,
        # so a 404 while the file exists in this checkout is a badge merged alongside a
        # brand-new workflow — awaiting its first run, not a monitor failure.
        workflow_file = REPO_ROOT / ".github" / "workflows" / badge.workflow
        if "HTTP 404" in stderr and workflow_file.is_file():
            return awaiting_first_run(badge)
        return unreadable_status(badge, stderr or "GitHub API request failed")

    try:
        payload = json.loads(completed.stdout)
        runs = payload["workflow_runs"]
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        return unreadable_status(badge, f"Invalid GitHub API response: {error}")
    if runs:
        return classify_run(badge, runs[0])
    # Registered when it reached master, a workflow runs only once its trigger fires (the deploy
    # job after the next deploy), so never having run on any branch is the same wait as the
    # 404 above. One that ran elsewhere but never on master is red.
    anywhere = subprocess.run(
        [
            "gh", "api", "-X", "GET",
            f"repos/{repository}/actions/workflows/{badge.workflow}/runs",
            "-f", "per_page=1",
        ],
        capture_output=True, text=True, check=False,
    )
    if anywhere.returncode != 0:
        return unreadable_status(badge, anywhere.stderr.strip() or "GitHub API request failed")
    try:
        ran_anywhere = json.loads(anywhere.stdout)["total_count"] > 0
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        return unreadable_status(badge, f"Invalid GitHub API response: {error}")
    return classify_run(badge, None) if ran_anywhere else awaiting_first_run(badge)


def exit_code(statuses: list[WorkflowStatus]) -> int:
    """Use a distinct code for monitor failures and red workflows."""
    if any(status.state == "unknown" for status in statuses):
        return 2
    if any(status.state == "red" for status in statuses):
        return 1
    return 0


def render_table(statuses: list[WorkflowStatus]) -> str:
    """Render compact output for interactive checks."""
    rows = ["STATE\tSECTION\tWORKFLOW\tCONCLUSION\tRUN"]
    for status in statuses:
        conclusion = status.conclusion or status.status
        run = status.url or status.error
        rows.append(
            f"{status.state.upper()}\t{status.section}\t{status.name}\t{conclusion}\t{run}"
        )
    return "\n".join(rows)


def main() -> int:
    """Check the README workflow inventory."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--readme", type=Path, default=REPO_ROOT / "README.md")
    # owner/name; GitHub Actions sets GITHUB_REPOSITORY.
    repository = os.environ.get("GITHUB_REPOSITORY")
    parser.add_argument("--repo", default=repository, required=not repository)
    parser.add_argument("--branch", default="master")
    parser.add_argument("--json", action="store_true")
    arguments = parser.parse_args()

    badges = read_workflow_badges(arguments.readme)
    if not badges:
        print(f"No workflow badges found in {arguments.readme}", file=sys.stderr)
        return 2

    statuses = [
        query_latest_run(arguments.repo, arguments.branch, badge) for badge in badges
    ]
    if arguments.json:
        print(json.dumps([asdict(status) for status in statuses], indent=2))
    else:
        print(render_table(statuses))
    return exit_code(statuses)


if __name__ == "__main__":
    sys.exit(main())
