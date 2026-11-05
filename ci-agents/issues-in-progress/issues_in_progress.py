#!/usr/bin/env python3
"""Move the issues a pull request declares to In progress on the project board.

Run by `.github/workflows/issues-in-progress.yml` on a pull request's opening and edits. The
issues are the ones a line of its description declares ("Fixes #N", "Part of #N"; the parser in
`rest.py`, which ships in tools/github-rest/ and is installed next to this script). An issue moves
only from a status before work starts: one already In progress or Done, or closed, stays where it
is. GitHub's workflow token cannot edit an organization's boards, so GH_TOKEN is a token with
organization Projects read and write, and the repository's Issues and Pull requests read. A number
that resolves to nothing is reported, and the others still move.

Usage: python3 github/issues_in_progress.py <event.json>   (GITHUB_EVENT_PATH)
"""
import json
import os
import subprocess
import sys

from rest import gh, linked_issue_numbers

# The organization that owns the project board, and the board's number.
PROJECT_OWNER = os.environ["PROJECT_OWNER"]
PROJECT_NUMBER = int(os.environ["PROJECT_NUMBER"])
IN_PROGRESS = "In progress"
LATER_STATUSES = {IN_PROGRESS, "Done"}

PROJECT_QUERY = """
query($owner: String!, $number: Int!) {
  organization(login: $owner) {
    projectV2(number: $number) {
      id
      field(name: "Status") {
        ... on ProjectV2SingleSelectField { id options { id name } }
      }
    }
  }
}
"""

ISSUE_QUERY = """
query($owner: String!, $name: String!, $number: Int!) {
  repository(owner: $owner, name: $name) {
    issueOrPullRequest(number: $number) {
      ... on Issue {
        state
        projectItems(first: 20) {
          nodes {
            id
            project { id }
            fieldValueByName(name: "Status") {
              ... on ProjectV2ItemFieldSingleSelectValue { name }
            }
          }
        }
      }
    }
  }
}
"""

SET_STATUS = """
mutation($project: ID!, $item: ID!, $field: ID!, $option: String!) {
  updateProjectV2ItemFieldValue(input: {
    projectId: $project, itemId: $item, fieldId: $field,
    value: { singleSelectOptionId: $option }
  }) { projectV2Item { id } }
}
"""


def graphql(query, **variables):
    arguments = ["api", "graphql", "-f", f"query={query}"]
    for name, value in variables.items():
        arguments += ["-F" if isinstance(value, int) else "-f", f"{name}={value}"]
    return json.loads(gh(arguments))["data"]


def main():
    with open(sys.argv[1], encoding="utf-8") as event_file:
        event = json.load(event_file)
    numbers = linked_issue_numbers(event["pull_request"]["body"])
    if not numbers:
        print("The description declares no issue.")
        return
    owner, name = event["repository"]["full_name"].split("/")
    project = graphql(PROJECT_QUERY, owner=PROJECT_OWNER, number=PROJECT_NUMBER)[
        "organization"]["projectV2"]
    option = next(o["id"] for o in project["field"]["options"] if o["name"] == IN_PROGRESS)
    unresolved = []
    for number in numbers:
        lookup = subprocess.run(
            ["gh", "api", "graphql", "-f", f"query={ISSUE_QUERY}", "-f", f"owner={owner}",
             "-f", f"name={name}", "-F", f"number={number}"],
            capture_output=True, text=True, check=False)
        if lookup.returncode != 0:
            print(f"#{number}: {lookup.stderr.strip() or lookup.stdout.strip()}")
            unresolved.append(number)
            continue
        issue = json.loads(lookup.stdout)["data"]["repository"]["issueOrPullRequest"]
        if issue is None:
            print(f"#{number}: no such issue")
            unresolved.append(number)
            continue
        if issue.get("state") != "OPEN":
            print(f"#{number}: not an open issue")
            continue
        item = next(
            (i for i in issue["projectItems"]["nodes"] if i["project"]["id"] == project["id"]),
            None)
        if item is None:
            print(f"#{number}: not on the board")
            continue
        status = (item["fieldValueByName"] or {}).get("name")
        if status in LATER_STATUSES:
            print(f"#{number}: stays in {status}")
            continue
        graphql(SET_STATUS, project=project["id"], item=item["id"],
                field=project["field"]["id"], option=option)
        print(f"#{number}: {status} -> {IN_PROGRESS}")
    if unresolved:
        sys.exit(f"Could not read {', '.join(f'#{n}' for n in unresolved)}.")


if __name__ == "__main__":
    main()
