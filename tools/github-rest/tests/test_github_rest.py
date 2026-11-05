#!/usr/bin/env python3
"""Tests for the shape normalization of rest.py.

The original suite runs on trimmed live REST and GraphQL responses; these use small synthetic
payloads of the same shape, including the proxy's `review_threads` response as a cloud probe
observed it, with one thread listing a reply before its root.
"""
import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "rest.py"
SPEC = importlib.util.spec_from_file_location("github_rest", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def pull(**overrides):
    """A REST pull request with the fields normalize_pull reads."""
    return {
        "number": 7, "html_url": "https://github.com/o/r/pull/7", "title": "Fix the export",
        "body": "Fixes #3\nPart of #5\n", "state": "closed", "merged": True,
        "merged_at": "2026-01-01T00:00:00Z", "draft": False, "mergeable": None,
        "head": {"ref": "fix-export", "sha": "abc123"}, "base": {"ref": "master"},
        "user": {"login": "a-developer"}, **overrides,
    }


def comment(comment_id, reply_to=None, login="a-reviewer", user_type="User"):
    """A REST review comment."""
    return {
        "id": comment_id, "in_reply_to_id": reply_to,
        "user": {"login": login, "type": user_type}, "body": f"comment {comment_id}",
        "created_at": "2026-01-01T00:00:00Z", "updated_at": "2026-01-01T00:00:00Z",
        "html_url": f"https://github.com/o/r/pull/7#discussion_r{comment_id}",
    }


REVIEW_COMMENTS = [comment(10, login="review-bot[bot]", user_type="Bot"), comment(11, reply_to=10),
                   comment(20)]
PROXY_THREADS = [
    {"resolved": False, "outdated": True, "path": "a.py", "line": None, "comment_ids": [11, 10]},
    {"resolved": True, "outdated": False, "path": "b.py", "line": 4, "comment_ids": [20]},
]
GRAPHQL_NODES = [
    {"id": "T1", "isResolved": False, "isOutdated": True, "path": "a.py", "line": None,
     "comments": {"nodes": [{"databaseId": 10}]}},
    {"id": "T2", "isResolved": True, "isOutdated": False, "path": "b.py", "line": 4,
     "comments": {"nodes": [{"databaseId": 20}]}},
]


class PullRequestShapeTests(unittest.TestCase):
    """REST pull requests read like `gh pr view --json`, which the PR skills were written for."""

    def test_merged_pull_reads_as_merged_with_unknown_mergeability(self):
        """REST says `closed` + merged and `mergeable: null`; gh says MERGED and UNKNOWN."""
        normalized = MODULE.normalize_pull(pull(), [])
        self.assertEqual(normalized["state"], "MERGED")
        self.assertEqual(normalized["mergeable"], "UNKNOWN")
        self.assertEqual(normalized["headRefOid"], "abc123")

    def test_mergeable_maps_to_gh_vocabulary(self):
        """/autoreview polls UNKNOWN and merges base on CONFLICTING."""
        self.assertEqual(MODULE.mergeable_state(True), "MERGEABLE")
        self.assertEqual(MODULE.mergeable_state(False), "CONFLICTING")

    def test_linked_issues_follow_the_pr_reference_convention(self):
        """`Fixes #N` and `Part of #N` both feed the PR intent, once each."""
        self.assertEqual(MODULE.linked_issue_numbers(pull()["body"] + "Fixes #3\n"), [3, 5])

    def test_plain_issue_mentions_are_not_linked(self):
        """A bare `#N` in prose is context, not the issue the PR works on."""
        self.assertEqual(MODULE.linked_issue_numbers("See #12 and PR #45."), [])

    def test_only_a_line_that_declares_the_link_links_the_issue(self):
        """A line declares the link, list marker, bold or colon included; the same words inside
        a sentence, a quote or a parenthesis do not, so a follow-up note links nothing."""
        body = ("closes: #56\n- **Resolves #90**\n- This does not fix #91; a follow-up.\n"
                "> Fixes #92\n(Fixes #93 in a later PR)\nNegation is tracked as part of #94.")
        self.assertEqual(MODULE.linked_issue_numbers(body), [56, 90])


class ChecksShapeTests(unittest.TestCase):
    """Check runs and statuses carry the states `gh pr checks` reports."""

    def test_check_run_state_is_conclusion_once_completed_else_status(self):
        """/autoreview treats PENDING/QUEUED/IN_PROGRESS as active and reads conclusions after."""
        runs = [
            {"name": "lint", "status": "completed", "conclusion": "failure", "details_url": "x"},
            {"name": "review-bot", "status": "completed", "conclusion": "neutral",
             "details_url": "x"},
            {"name": "tests", "status": "in_progress", "conclusion": None, "details_url": "x"},
        ]
        checks = {check["name"]: check["state"] for check in MODULE.normalize_checks(runs, [])}
        self.assertEqual(checks, {"lint": "FAILURE", "review-bot": "NEUTRAL",
                                  "tests": "IN_PROGRESS"})

    def test_commit_statuses_join_the_check_list(self):
        """Statuses posted by external services count as checks, as in `gh pr checks`."""
        status = {"context": "deploy/preview", "state": "pending", "target_url": "https://x"}
        checks = MODULE.normalize_checks([], [status])
        self.assertEqual(
            checks, [{"name": "deploy/preview", "state": "PENDING", "link": "https://x"}]
        )

    def test_in_progress_run_has_an_empty_conclusion(self):
        """An in-progress run has no conclusion; gh prints it as an empty string."""
        run = MODULE.normalize_run({"id": 1, "name": "CI", "status": "in_progress",
                                    "conclusion": None, "html_url": "x", "head_sha": "abc"})
        self.assertEqual(run["conclusion"], "")


class ReviewThreadShapeTests(unittest.TestCase):
    """Cloud (proxy route) and local (GraphQL) threads come out in one shape."""

    def test_proxy_and_graphql_give_the_same_threads(self):
        """Same PR, same state: the skills cannot tell which route served the threads."""
        from_proxy = MODULE.attach_comments(
            MODULE.threads_from_proxy(PROXY_THREADS, REVIEW_COMMENTS), REVIEW_COMMENTS)
        from_graphql = MODULE.attach_comments(
            MODULE.threads_from_graphql(GRAPHQL_NODES), REVIEW_COMMENTS)
        self.assertEqual(from_proxy, from_graphql)

    def test_root_comment_is_found_when_a_reply_is_listed_first(self):
        """resolve-thread takes the root comment ID; the proxy's comment_ids order is unobserved."""
        threads = MODULE.threads_from_proxy(PROXY_THREADS, REVIEW_COMMENTS)
        self.assertEqual(threads[0]["rootCommentId"], 10)

    def test_thread_comments_are_root_then_replies_with_author_type(self):
        """Triage reads the ask from the root, sees replies, and tells bots by authorType."""
        threads = MODULE.attach_comments(
            MODULE.threads_from_graphql(GRAPHQL_NODES), REVIEW_COMMENTS)
        thread = threads[0]
        self.assertEqual([c["databaseId"] for c in thread["comments"]], [10, 11])
        self.assertEqual(thread["comments"][0]["authorType"], "Bot")
        self.assertTrue(thread["isOutdated"])


class RepositoryTests(unittest.TestCase):
    """The repository comes from the remote, whatever host the session clones through."""

    def test_remote_url_forms(self):
        """SSH, HTTPS, and a proxy-style path all name owner/name last."""
        for url in [
            "git@github.com:example-org/example-repo.git",
            "https://github.com/example-org/example-repo.git",
            "http://local_proxy@127.0.0.1:41234/git/example-org/example-repo\n",
        ]:
            self.assertEqual(MODULE.parse_repository(url), "example-org/example-repo")


if __name__ == "__main__":
    unittest.main()
