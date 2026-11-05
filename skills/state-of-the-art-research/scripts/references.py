"""Render author–date (APA 7) citations and the reference list of a research report.

Usage: python3 references.py <refs.json> <draft.md> <report.md> <research dir>/notes/*.md

The draft cites with pandoc-style keys: `[@doe-agents; @examplelab-evals]` becomes a parenthetical
`(Doe et al., 2026; Example Lab, 2026)`, and a bare `@doe-agents` becomes the narrative
`Doe et al. (2026)`. Each citation is a Markdown link to its source's URL. A bare `@word` that
is not a reference key is left untouched; a bracketed `@` citation in any other form (a locator
such as `[@key, p. 3]`) stops the script. The report is the draft with every key rendered and a
`## References` section appended, replacing the draft's last `## References` (or numbered
`## 9. References`) section and anything after it.

refs.json:
{
  "retrieved": "2026-02-03",              # retrieval date, required when an entry is undated
  "keep_case": ["GitHub", "JSON"],        # title words sentence case must not lowercase
  "references": [
    {"key": "doe-agents", "arxiv": "2601.00001"},
    {"key": "examplelab-evals", "authors": "Example Lab", "date": "2026-01-09",
     "title": "Demystifying evals for AI agents", "site": "Example Lab Engineering",
     "url": "https://example.org/engineering/demystifying-evals-for-ai-agents"}
  ]
}
An arXiv entry needs only its id (a version suffix such as v2 is dropped); title, authors and
posting date come from the arXiv API and are cached in `<refs>.cache.json`. Any field given in
refs.json wins over the fetched one, which is how to fix a name the API spells oddly. Other entries
give `authors` (an organization string or a list of "First Last" names), `date` (YYYY-MM-DD, YYYY,
or "n.d."), `title`, `url` and optionally `site` or `venue`. A reference whose URL any notes file's
reading tally lists under Read in full gets ✓, so the marks always match the tally.
"""
import json
import re
import string
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import tally  # pylint: disable=wrong-import-position

MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
          'October', 'November', 'December']
SURNAME_PARTICLES = {'van', 'von', 'de', 'der', 'den', 'del', 'della', 'di', 'da', 'du', 'la', 'le'}
ATOM = '{http://www.w3.org/2005/Atom}'
ARXIV_ID = re.compile(r'^(?:\d{4}\.\d{4,5}|[a-z-]+(?:\.[A-Z]{2})?/\d{7})$')
# Fenced blocks of any fence (``` or ~~~, any length, closed by the same fence) and inline code.
CODE = re.compile(r'^(`{3,}|~{3,})[^\n]*\n.*?^\1[ \t]*$|`[^`\n]+`', re.S | re.M)
REFERENCES_HEADING = re.compile(r'^## (?:\d+\.\s*)?References\s*$', re.M)
# Not followed by '(': [@handle](url) is a link, not a citation.
GROUP_PATTERN = re.compile(r'\[(@[\w.:-]+(?:\s*;\s*@[\w.:-]+)*)\](?!\()')
# A bare @key not glued to a word, an email, a code span or a path.
NARRATIVE_PATTERN = re.compile(r'(?<![\w@\[`/.])@([\w.:-]*\w)')


def fetch_arxiv(ids, cache_path):
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    missing = [i for i in ids if i not in cache]
    if missing:
        url = ('https://export.arxiv.org/api/query'
               f'?max_results={len(missing)}&id_list={",".join(missing)}')
        with urllib.request.urlopen(url, timeout=60) as response:
            feed = ET.fromstring(response.read())
        for entry in feed.findall(ATOM + 'entry'):
            arxiv_id = re.sub(r'v\d+$', '', entry.findtext(ATOM + 'id').rsplit('/abs/', 1)[1])
            cache[arxiv_id] = {
                'title': ' '.join(entry.findtext(ATOM + 'title').split()),
                'authors': [a.findtext(ATOM + 'name') for a in entry.findall(ATOM + 'author')],
                'date': entry.findtext(ATOM + 'published')[:10],
            }
        cache_path.write_text(json.dumps(cache, indent=1, ensure_ascii=False))
    not_found = [i for i in ids if i not in cache]
    if not_found:
        sys.exit(f'arXiv returned no entry for: {", ".join(not_found)}')
    return cache


def split_name(name):
    """'Jean-Pierre van der Berg' -> ('van der Berg', 'J.-P.')."""
    tokens = name.split()
    surname_start = len(tokens) - 1
    while surname_start > 1 and tokens[surname_start - 1].lower() in SURNAME_PARTICLES:
        surname_start -= 1
    initials = ' '.join('-'.join(part[0] + '.' for part in token.split('-') if part)
                        for token in tokens[:surname_start])
    return ' '.join(tokens[surname_start:]), initials


def first_surname(ref):
    authors = ref['authors']
    return authors if isinstance(authors, str) else split_name(authors[0])[0]


def text_authors(ref, narrative):
    authors = ref['authors']
    if isinstance(authors, str):
        return authors
    surnames = [split_name(a)[0] for a in authors]
    if ref['with_initials']:
        surnames[0] = f'{split_name(authors[0])[1]} {surnames[0]}'
    if len(surnames) == 1:
        return surnames[0]
    conjunction = 'and' if narrative else '&'
    if len(surnames) == 2:
        return f'{surnames[0]} {conjunction} {surnames[1]}'
    if ref['named'] >= len(surnames):
        return f'{", ".join(surnames[:-1])}, {conjunction} {surnames[-1]}'
    if ref['named'] == 1:
        return f'{surnames[0]} et al.'
    return f'{", ".join(surnames[:ref["named"]])}, et al.'


def year_of(ref):
    return 'n.d.' if ref['date'] == 'n.d.' else ref['date'][:4]


def year_label(ref):
    return year_of(ref) + ref['suffix']


def chronological(ref):
    # Undated works come before dated ones by the same author (APA 9.47); a longer suffix (aa)
    # comes after every shorter one (z).
    suffix = ref['suffix'].lstrip('-')
    return ('0000' if year_of(ref) == 'n.d.' else year_of(ref), len(suffix), suffix)


def suffix_letters(index):
    # a ... z, then aa, ab, ...
    letters = ''
    index += 1
    while index:
        index, remainder = divmod(index - 1, 26)
        letters = string.ascii_lowercase[remainder] + letters
    return letters


def alphabetical(ref):
    # A tuple, so a one-author work sorts before the same author's multi-author works (APA 9.46).
    authors = ref['authors']
    names = ((authors, ''),) if isinstance(authors, str) else tuple(map(split_name, authors))
    return (tuple((surname.lower(), initials.lower()) for surname, initials in names),
            chronological(ref))


def sentence_case(title, keep_case):
    words, start_of_sentence = [], True
    for word in title.split(' '):
        parts = []
        for index, part in enumerate(word.split('-')):
            core = part.strip(':?!,;.()"\'')
            keep = ((start_of_sentence and index == 0) or core in keep_case
                    or core == 'I' or core.startswith("I'")
                    or any(c.isupper() for c in core[1:]) or any(c.isdigit() for c in core))
            parts.append(part if keep else part.lower())
        words.append('-'.join(parts))
        start_of_sentence = word.endswith((':', '?', '!'))
    return ' '.join(words)


def reference_authors(authors):
    if isinstance(authors, str):
        return authors + '.'
    names = [', '.join(part for part in split_name(a) if part) for a in authors]
    if len(names) > 20:
        listed = ', '.join(names[:19]) + ', … ' + names[-1]
    elif len(names) == 1:
        listed = names[0]
    else:
        listed = ', '.join(names[:-1]) + ', & ' + names[-1]
    return listed if listed.endswith('.') else listed + '.'


def long_date(date):
    year, month, day = date.split('-')
    return f'{MONTHS[int(month) - 1]} {int(day)}, {year}'


def reference_entry(ref, keep_case, retrieved, read):
    date = ref['date']
    when = year_label(ref)
    # A preprint is dated by its year alone (APA 10.8); a web page keeps its month and day.
    if date != 'n.d.' and len(date) > 4 and 'arxiv' not in ref:
        when += ', ' + long_date(date).rsplit(',', 1)[0]
    title = sentence_case(ref['title'], keep_case)
    # APA: a title ending in its own question or exclamation mark takes no added period.
    closing = '' if title.endswith(('?', '!')) else '.'
    parts = [f'{reference_authors(ref["authors"])} ({when}).',
             f'*{title}*' + (' [Preprint]. arXiv.' if 'arxiv' in ref else closing)]
    parts += [ref[field] + '.' for field in ('venue', 'site') if ref.get(field)]
    if date == 'n.d.':
        if not retrieved:
            sys.exit(f'{ref["key"]} is undated, so refs.json needs a "retrieved" date')
        parts.append(f'Retrieved {long_date(retrieved)}, from')
    parts.append(ref['url'] + (' ✓' if tally.source_id(ref['url']) in read else ''))
    return ' '.join(parts)


def load_references(refs_path):
    config = json.loads(refs_path.read_text())
    refs = {}
    for ref in config['references']:
        if ref['key'] in refs:
            sys.exit('duplicate key: ' + ref['key'])
        if 'arxiv' in ref:
            # The API returns unversioned ids, so the cache is keyed on them.
            ref['arxiv'] = re.sub(r'v\d+$', '', ref['arxiv'])
            if not ARXIV_ID.match(ref['arxiv']):
                sys.exit(f'{ref["key"]}: "{ref["arxiv"]}" is not an arXiv id')
        refs[ref['key']] = ref
    # An entry that already gives its metadata needs no fetch, so the script also runs offline.
    arxiv_ids = [r['arxiv'] for r in refs.values()
                 if 'arxiv' in r and not {'title', 'authors', 'date'} <= r.keys()]
    if arxiv_ids:
        fetched = fetch_arxiv(arxiv_ids, refs_path.with_suffix('.cache.json'))
        for key, ref in refs.items():
            if ref.get('arxiv') in arxiv_ids:
                refs[key] = {**fetched[ref['arxiv']], **ref}
    for key, ref in refs.items():
        if 'arxiv' in ref:
            refs[key] = {'url': 'https://arxiv.org/abs/' + ref['arxiv'], **ref}
    return config, refs


def title_order(ref):
    return ref['title'].lower()


def label_cited(cited):
    # Initials go in the text when two different first authors share a surname (APA 8.20).
    people_by_surname = {}
    for ref in cited:
        if not isinstance(ref['authors'], str):
            people_by_surname.setdefault(first_surname(ref), set()).add(ref['authors'][0])
    for ref in cited:
        ref['with_initials'] = len(people_by_surname.get(first_surname(ref), ())) > 1
    # Different author lists of three or more that would shorten to the same "X et al." in one year
    # name as many authors as it takes to tell them apart (APA 8.18).
    # Names compare as printed, so author lists differing only in a given name stay rivals.
    long_lists = [r for r in cited if not isinstance(r['authors'], str) and len(r['authors']) > 2]
    printed = {id(r): [split_name(a)[0] for a in r['authors']] for r in long_lists}
    for ref in cited:
        ref['named'] = 1
        if ref not in long_lists:
            continue
        mine = printed[id(ref)]
        rivals = [printed[id(r)] for r in long_lists if r is not ref and year_of(r) == year_of(ref)
                  and r['authors'] != ref['authors']]
        while ref['named'] < len(mine) and any(
                rival[:ref['named']] == mine[:ref['named']] for rival in rivals):
            ref['named'] += 1
        # "et al." never stands for a single name: name the last author instead.
        if ref['named'] == len(mine) - 1 and ref['named'] > 1:
            ref['named'] = len(mine)
    # Works whose citations still print the same in one year: suffix a, b, ... in title order
    # (APA 8.19). This covers the same authors, and author lists no names can tell apart.
    by_label = {}
    for ref in cited:
        by_label.setdefault((text_authors(ref, False), year_of(ref)), []).append(ref)
    for same in by_label.values():
        same.sort(key=title_order)
        for index, ref in enumerate(same):
            dash = '-' if year_of(ref) == 'n.d.' else ''
            ref['suffix'] = '' if len(same) == 1 else dash + suffix_letters(index)


def main(refs_path, draft_path, report_path, *notes_paths):
    refs_path = Path(refs_path)
    if Path(draft_path).resolve() == Path(report_path).resolve():
        sys.exit('render into a separate report file: rendering replaces the citation keys')
    config, refs = load_references(refs_path)
    read, _ = tally.read_tally(notes_paths)
    # Code is set aside first, so an @ in it (an npm scope, a decorator) is never read as a
    # citation and a '## References' line in an example is not taken for the bibliography.
    body = Path(draft_path).read_text()
    code = [match.group(0) for match in CODE.finditer(body)]
    def stash(match):
        return f'\x00{code.index(match.group(0))}\x00'

    def restore(match):
        return code[int(match.group(1))]

    body = CODE.sub(stash, body)
    headings = list(REFERENCES_HEADING.finditer(body))
    if headings:
        body = body[:headings[-1].start()]
    body = body.rstrip('\n')

    cited_keys = [k.strip()[1:] for g in GROUP_PATTERN.findall(body) for k in g.split(';')]
    cited_keys += [k for k in NARRATIVE_PATTERN.findall(GROUP_PATTERN.sub('', body)) if k in refs]
    unknown = sorted({k for k in cited_keys if k not in refs})
    if unknown:
        sys.exit(f'cited but not in {refs_path.name}: {", ".join(unknown)}')
    cited = [refs[k] for k in dict.fromkeys(cited_keys)]
    label_cited(cited)

    def link(text, ref):
        # Parentheses in a URL would end the Markdown link early.
        return f'[{text}]({ref["url"].replace("(", "%28").replace(")", "%29")})'

    def parenthetical(match):
        # Works are alphabetical (APA 8.12), and works by the same authors share one name:
        # (Example Lab, n.d., 2026a).
        groups = []
        for ref in sorted((refs[k.strip()[1:]] for k in match.group(1).split(';')),
                          key=alphabetical):
            if groups and groups[-1][0] == text_authors(ref, False):
                groups[-1][1].append(ref)
            else:
                groups.append((text_authors(ref, False), [ref]))
        cites = []
        for label, works in groups:
            if len(works) == 1:
                cites.append(link(f'{label}, {year_label(works[0])}', works[0]))
            else:
                years = ', '.join(link(year_label(r), r) for r in works)
                cites.append(f'{label}, {years}')
        return '(' + '; '.join(cites) + ')'

    def narrative(match):
        ref = refs.get(match.group(1))
        if ref is None:
            return match.group(0)
        return link(f'{text_authors(ref, True)} ({year_label(ref)})', ref)

    body = NARRATIVE_PATTERN.sub(narrative, GROUP_PATTERN.sub(parenthetical, body))
    # A bracketed @key the patterns above did not take, outside links and email addresses.
    leftover = re.findall(r'\[[^\]]*(?<![\w.])@\w[^\]]*\](?!\()', body)
    if leftover:
        sys.exit('citations not in the [@key; @key] form: ' + ', '.join(leftover))
    uncited = [k for k in refs if k not in set(cited_keys)]
    if uncited:
        print('not cited, left out of the list: ' + ', '.join(uncited))

    keep_case = set(config.get('keep_case', []))
    entries = [reference_entry(r, keep_case, config.get('retrieved'), read)
               for r in sorted(cited, key=alphabetical)]
    body = re.sub('\x00(\\d+)\x00', restore, body)
    Path(report_path).write_text(body + '\n\n## References\n\n' + '\n\n'.join(entries) + '\n')
    print(f'{len(entries)} references, {len(cited_keys)} citations')


if __name__ == '__main__':
    if len(sys.argv) < 5:
        sys.exit(__doc__)
    main(*sys.argv[1:])
