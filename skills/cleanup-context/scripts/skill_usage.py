#!/usr/bin/env python3
"""Mine local Claude Code session transcripts for context-load frequency.

Usage: python3 skill_usage.py [session_limit] [repo_name]

Prints, over the newest N session files of every project dir whose slug names the repository:
- Skill tool invocations per skill (total calls / sessions containing one).
- Slash commands the user typed.
- AGENTS.md / handbook / design-doc files opened with the Read tool or attached by Claude Code
  itself, per session: the root rules at session start (an `instructions` attachment), and a
  directory's `CLAUDE.md` shim with its `AGENTS.md` when a file there is read (a `nested_memory`
  attachment; this is how most per-service rules arrive). Shell reads (cat, sed) are not counted.

An event copied into a resumed or forked session's file counts once. Frequent skills are
practically always-on (their bodies are trim targets); never-loaded skills have a description
problem or are deletion candidates.
"""
import collections
import glob
import json
import os
import re
import sys
import time

SESSION_LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 100
REPO_NAME = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(os.getcwd())
# Claude Code's transcript store: one folder per project, named after the checkout path with '/',
# '.' and '_' replaced by '-', holding one JSONL file per session.
PROJECTS_ROOT = os.path.expanduser('~/.claude/projects')


def is_repo_project(slug):
    """A project slug encodes the checkout path, so a checkout of the repository ends in
    '-<repo>' (the main checkout) or contains '-<repo>-' (a checkout named <repo>-<name>, or a
    worktree under a '<repo>_worktrees' or '<repo>-worktrees' directory)."""
    name = REPO_NAME.replace('_', '-').replace('.', '-')
    return slug.endswith(f'-{name}') or f'-{name}-' in slug


files = []
for d in glob.glob(os.path.join(PROJECTS_ROOT, '*')):
    if is_repo_project(os.path.basename(d)):
        files += glob.glob(os.path.join(d, '*.jsonl'))
files = [f for f in files if re.match(r'^[0-9a-f-]{36}\.jsonl$', os.path.basename(f))]
files.sort(key=os.path.getmtime, reverse=True)
sessions = files[:SESSION_LIMIT]
if not sessions:
    sys.exit(f'no {REPO_NAME} session files under {PROJECTS_ROOT}')
print(f'session files found: {len(files)}, analyzing newest: {len(sessions)}')
print(f'oldest analyzed session: {time.ctime(os.path.getmtime(sessions[-1]))}')

skill_calls = collections.Counter()
skill_sessions = collections.Counter()
cmd_calls = collections.Counter()
cmd_sessions = collections.Counter()
read_sessions = collections.Counter()
CONTEXT_FILE = re.compile(r'(AGENTS\.md|docs/handbook/|docs/design/)')
# A file inside a checkout of the repository: a worktree under a '<repo>_worktrees' directory or
# Claude Code's own worktree folder (.claude/worktrees), or a checkout named <repo> or
# <repo>-<name> anywhere.
REPO = re.escape(REPO_NAME)
WORKTREE = re.compile(rf'^.*?/(?:{REPO}[_-]worktrees/[^/]+|\.[a-z]+/worktrees/[^/]+)/(.+)$')
CHECKOUT = re.compile(rf'^.*?/(?:{REPO}|{REPO}-[^/]+)/(.+)$')
# A resumed or forked session's file repeats the history it was copied from; each event keeps
# its uuid, so an event already seen in a newer file is not counted again.
seen_events = set()


def repo_relative(file_path):
    """The path inside its checkout, or None for a file outside every checkout."""
    match = WORKTREE.match(file_path) or CHECKOUT.match(file_path)
    return match.group(1) if match else None


def attached_files(attachment):
    """The files an attachment put in context: a nested CLAUDE.md shim and its AGENTS.md, or the
    instruction files (root CLAUDE.md, its AGENTS.md import) loaded at session start."""
    if attachment.get('type') == 'nested_memory':
        return [attachment.get('path', '')]
    if attachment.get('type') == 'instructions':
        return [entry.get('path', '') for entry in attachment.get('files') or []]
    return []


contributing_sessions = 0
for f in sessions:
    per_skill, per_cmd, per_read = set(), set(), set()
    contributed = False
    with open(f, errors='replace') as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            uuid = rec.get('uuid')
            if uuid in seen_events:
                continue
            if uuid:
                seen_events.add(uuid)
                contributed = True
            for attached in attached_files(rec.get('attachment') or {}):
                relative = repo_relative(attached)
                if relative and CONTEXT_FILE.search(relative):
                    per_read.add(relative)
            content = (rec.get('message') or {}).get('content')
            blocks = content if isinstance(content, list) else []
            texts = [content] if isinstance(content, str) else []
            for c in blocks:
                if not isinstance(c, dict):
                    continue
                if c.get('type') == 'tool_use' and c.get('name') == 'Skill':
                    s = (c.get('input') or {}).get('skill', '?')
                    skill_calls[s] += 1
                    per_skill.add(s)
                elif c.get('type') == 'tool_use' and c.get('name') == 'Read':
                    relative = repo_relative((c.get('input') or {}).get('file_path', ''))
                    if relative and CONTEXT_FILE.search(relative):
                        per_read.add(relative)
                elif c.get('type') == 'text':
                    texts.append(c.get('text', ''))
            for text in texts:
                for m in re.findall(r'<command-name>/?([\w:-]+)</command-name>', text):
                    cmd_calls[m] += 1
                    per_cmd.add(m)
    contributing_sessions += contributed
    for s in per_skill:
        skill_sessions[s] += 1
    for c in per_cmd:
        cmd_sessions[c] += 1
    for p in per_read:
        read_sessions[p] += 1

print('\n=== Skill invocations (calls / sessions-with-use) ===')
for s, n in skill_calls.most_common():
    print(f'{n:4d}  {skill_sessions[s]:3d}  {s}')
print('\n=== Slash commands typed by user (calls / sessions) ===')
for s, n in cmd_calls.most_common():
    print(f'{n:4d}  {cmd_sessions[s]:3d}  {s}')
# Files that add no new event (empty transcripts, originals of resumed sessions) are left out.
print(f'\n=== Context files opened with Read or attached by Claude Code '
      f'(sessions of {contributing_sessions}) ===')
for p, n in read_sessions.most_common(40):
    print(f'{n:3d}  {p}')
