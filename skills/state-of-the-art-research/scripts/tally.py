"""Count the papers and articles a research read in full, out of those found or glimpsed.

Usage: python3 tally.py <research dir>/notes/*.md

Each notes file ends with a `## Reading tally` section holding two lists, one source per line:

    ### Read in full
    - paper: https://arxiv.org/abs/2601.00001
    - article: https://example.org/engineering/demystifying-evals-for-ai-agents
    ### Glimpsed
    - paper: https://arxiv.org/abs/2610.19113

A source is counted once across all files, however many readers saw it, and a source read in full
by anyone counts as read. Found is everything listed, read in full or only glimpsed. The abstract,
HTML and PDF pages of an arXiv paper, in any version, and its Hugging Face Papers page are one
source, and a URL's scheme, www, host case and anchor are ignored; its query is kept, since it can
name the page (OpenReview, Hacker News). A line or heading in the tally that does not fit this
format stops the script, so nothing is dropped from the count.
"""
import re
import sys
from pathlib import Path

ENTRY = re.compile(r'^- (paper|article): (https?://\S+)$')
SECTIONS = ('read in full', 'glimpsed')
# Every page of one paper: its arXiv abstract, HTML and PDF in any version, and its Hugging Face
# Papers page.
PAPER_PAGE = re.compile(r'^(?:(?:export\.)?arxiv\.org/(?:abs|html|pdf)|huggingface\.co/papers)/'
                        r'(\d{4}\.\d{4,5})(?:v\d+)?(?:\.pdf)?$')


def source_id(url):
    # Scheme, www, host case, anchors and a trailing slash do not make a different source. A query
    # does (OpenReview's forum?id=, Hacker News's item?id=), except on a paper's own pages.
    address = re.sub(r'^https?://(?:www\.)?', '', url.split('#')[0])
    host, _, rest = address.partition('/')
    address = f'{host.lower()}/{rest}'.rstrip('/')
    paper = PAPER_PAGE.match(address.split('?', maxsplit=1)[0].rstrip('/'))
    if paper:
        return 'arxiv:' + paper.group(1)
    # A paper's OpenReview forum and PDF, and its ACL Anthology page and PDF.
    venue = (re.match(r'^openreview\.net/(?:forum|pdf)\?id=([^&]+)', address)
             or re.match(r'^aclanthology\.org/([^/?]+?)(?:\.pdf)?$', address))
    return f'{address.split(".", maxsplit=1)[0]}:{venue.group(1)}' if venue else address

def read_tally(paths):
    """Return the sources read in full and the sources found, each mapped to its kind."""
    read, found = {}, {}
    for path in paths:
        text = Path(path).read_text()
        if '## Reading tally' not in text:
            sys.exit(f'{path} has no "## Reading tally" section')
        section = None
        for line in text.split('## Reading tally', 1)[1].splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith('## '):
                break
            if line.startswith('### '):
                section = line[4:].strip().lower()
                if section not in SECTIONS:
                    sys.exit(f'{path}: tally heading "{line}" is neither Read in full nor Glimpsed')
                continue
            match = ENTRY.match(line)
            if not match or section is None:
                sys.exit(f'{path}: tally line "{line}" is not "- paper: URL" or "- article: URL"'
                         ' under a Read in full or Glimpsed heading')
            kind, url = match.groups()
            source = source_id(url)
            if found.get(source, kind) != kind:
                sys.exit(f'{path}: {url} is listed as both a paper and an article; pick one')
            found[source] = kind
            if section == 'read in full':
                read[source] = kind
    return read, found


def main(paths):
    read, found = read_tally(paths)
    for kind in ('paper', 'article'):
        total = sum(1 for k in found.values() if k == kind)
        done = sum(1 for k in read.values() if k == kind)
        print(f'{kind}s: {done} read in full of {total} found')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
