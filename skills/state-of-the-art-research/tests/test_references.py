import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'scripts' / 'references.py'
spec = importlib.util.spec_from_file_location('references', SCRIPT)
references = importlib.util.module_from_spec(spec)
spec.loader.exec_module(references)


def paper(key, authors, title='A title', date='2026-05-01', **extra):
    return {'key': key, 'authors': authors, 'date': date, 'title': title,
            'url': f'https://example.org/{key}', **extra}


class RenderTest(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """Rendering a draft with refs.json into a report."""

    def render(self, draft, entries, tally='### Glimpsed\n', **config):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / 'refs.json').write_text(json.dumps({'references': entries, **config}))
            (folder / 'draft.md').write_text(draft)
            (folder / 'notes.md').write_text('## Reading tally\n\n' + tally)
            references.main(folder / 'refs.json', folder / 'draft.md', folder / 'report.md',
                            folder / 'notes.md')
            return (folder / 'report.md').read_text()

    def test_link_text_with_a_handle_is_not_a_citation(self):
        """A Markdown link whose text is an @handle stays a link, not a citation."""
        report = self.render('Posts by [@janedoe](https://x.com/janedoe) and [@one].',
                             [paper('one', 'Acme'), paper('janedoe', ['Jane Doe'])])
        self.assertIn('[@janedoe](https://x.com/janedoe)', report)
        self.assertIn('([Acme, 2026](https://example.org/one))', report)

    def test_different_et_al_author_lists_expand_authors_instead_of_suffixes(self):
        """Two author lists led by one author in one year are told apart by names, not a/b (APA 8.18)."""
        report = self.render('[@first] and [@second].', [
            paper('first', ['Jane Smith', 'Ana Li', 'Bo Zhang'], 'Alpha'),
            paper('second', ['Jane Smith', 'Carl Chen', 'Dan Liu'], 'Zeta'),
        ])
        self.assertIn('[Smith, Li, & Zhang, 2026]', report)
        self.assertIn('[Smith, Chen, & Liu, 2026]', report)
        self.assertNotIn('2026a', report)

    def test_same_authors_same_year_get_suffixes_in_title_order(self):
        """Identical author lists in one year get a, b by title, matching the list order."""
        team = ['Jane Smith', 'Ana Li', 'Bo Zhang']
        report = self.render('[@zeta; @alpha].', [paper('zeta', team, 'Zeta'),
                                                  paper('alpha', team, 'Alpha')])
        self.assertIn('Smith et al., [2026a](https://example.org/alpha), '
                      '[2026b](https://example.org/zeta)', report)
        listed = report.split('## References')[1]
        self.assertLess(listed.index('(2026a'), listed.index('(2026b'))

    def test_more_than_ten_same_year_works_get_suffixes(self):
        """An eleventh work by one author in one year still gets a letter."""
        entries = [paper(f'a{i}', 'Example Lab', f'T{i:02d}') for i in range(12)]
        report = self.render('[' + '; '.join(f'@a{i}' for i in range(12)) + ']', entries)
        self.assertIn('[2026l](https://example.org/a11)', report)

    def test_more_than_twenty_six_same_year_works_get_suffixes_in_order(self):
        """Suffixes go on past z (aa, ab) and keep their order in the text and the list."""
        entries = [paper(f'a{i}', 'Example Lab', f'T{i:02d}') for i in range(28)]
        report = self.render('[' + '; '.join(f'@a{i}' for i in range(28)) + ']', entries)
        self.assertIn('[2026ab](https://example.org/a27)', report)
        listed = report.split('## References')[1]
        self.assertLess(listed.index('(2026z,'), listed.index('(2026aa,'))
        self.assertLess(report.index('[2026z]'), report.index('[2026aa]'))

    def test_citation_keys_inside_code_are_left_alone(self):
        """Inline code and fenced blocks keep their @ text: a package scope is not a citation."""
        draft = ('Install `npm install @acme/agents` as @acme suggests.\n\n'
                 '```json\n{"types": ["@types/node"]}\n```\n')
        report = self.render(draft, [paper('acme', 'Acme')])
        self.assertIn('`npm install @acme/agents`', report)
        self.assertIn('{"types": ["@types/node"]}', report)
        self.assertIn('as [Acme (2026)](https://example.org/acme) suggests', report)

    def test_preprints_are_dated_by_year_only(self):
        """An arXiv preprint shows its year alone, while a web page keeps its month and day."""
        entry = paper('sem', ['Mara Quillfeather'], arxiv='2601.00001')
        del entry['url']
        post = paper('post', 'Example Lab', date='2026-01-09')
        report = self.render('[@sem; @post]', [entry, post])
        self.assertIn('Quillfeather, M. (2026). *A title* [Preprint]', report)
        self.assertIn('Example Lab. (2026, January 9).', report)

    def test_pronoun_i_keeps_its_capital_in_titles(self):
        """Sentence case keeps "I" and "I've" capitalized in a title."""
        title = "What I Learned and I've Kept"
        report = self.render('[@post]', [paper('post', ['Rafe Lindqvist'], title)])
        self.assertIn("*What I learned and I've kept*", report)

    def test_title_ending_in_a_question_mark_gets_no_extra_period(self):
        """A title that ends in "?" or "!" is not followed by an added period."""
        entry = paper('post', ['Tess Okonkwo'], 'Are Toy Datasets Worth It?')
        report = self.render('[@post]', [entry])
        self.assertIn('*Are toy datasets worth it?* ', report)
        self.assertNotIn('worth it?*.', report)

    def test_references_heading_inside_code_is_not_the_bibliography(self):
        """A '## References' line in a code example is kept, and the report after it survives."""
        draft = 'Text [@one].\n\n```markdown\n## References\n```\n\nConclusion stays.\n'
        report = self.render(draft, [paper('one', 'Acme')])
        self.assertIn('```markdown\n## References\n```', report)
        self.assertIn('Conclusion stays.', report)

    def test_read_marks_come_from_the_reading_tally(self):
        """A reference gets its read-in-full mark when any notes file lists it as read in full."""
        entry = paper('sem', ['Mara Quillfeather'], arxiv='2601.00001')
        del entry['url']
        notes = ('### Read in full\n- paper: https://arxiv.org/html/2601.00001v2\n'
                 '### Glimpsed\n- article: https://example.org/post\n')
        report = self.render('[@sem; @post]', [entry, paper('post', 'Example Lab')], tally=notes)
        self.assertIn('https://arxiv.org/abs/2601.00001 ✓', report)
        self.assertNotIn('https://example.org/post ✓', report)

    def test_tilde_and_long_fences_keep_their_contents(self):
        """A References heading in a ~~~ or four-backtick fence does not cut the report."""
        draft = ('Text [@one].\n\n~~~\n## References\n~~~\n\n'
                 '````markdown\n```\n## References\n```\n````\n\nConclusion stays.\n')
        report = self.render(draft, [paper('one', 'Acme')])
        self.assertIn('Conclusion stays.', report)
        self.assertEqual(report.count('## References'), 3)

    def test_parenthetical_citations_are_alphabetical(self):
        """Several works in one parenthesis are ordered by first author (APA 8.12)."""
        report = self.render('[@yang; @examplelab]', [paper('yang', ['Ming Yang']),
                                                     paper('examplelab', 'Example Lab')])
        self.assertLess(report.index('Example Lab, 2026'), report.index('Yang, 2026'))

    def test_citation_with_a_locator_stops_the_script(self):
        """A bracketed citation the script cannot render fails instead of shipping raw."""
        with self.assertRaises(SystemExit):
            self.render('As shown [@one, p. 3].', [paper('one', 'Acme')])

    def test_numbered_references_heading_is_replaced(self):
        """A draft's '## 9. References' section is replaced, not followed by a second list."""
        report = self.render('Text [@one].\n\n## 9. References\n\nold list\n',
                             [paper('one', 'Acme')])
        self.assertNotIn('old list', report)
        self.assertEqual(report.count('References'), 1)

    def test_versioned_arxiv_id_finds_the_cached_unversioned_entry(self):
        """A versioned arXiv id is looked up without its version, so the cached entry is used."""
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / 'refs.cache.json').write_text(json.dumps({'2601.00001': {
                'title': 'Synthetic benchmarks', 'authors': ['Mara Quillfeather'], 'date': '2026-01-05'}}))
            (folder / 'refs.json').write_text(json.dumps(
                {'references': [{'key': 'sem', 'arxiv': '2601.00001v2'}]}))
            (folder / 'draft.md').write_text('[@sem]')
            references.main(folder / 'refs.json', folder / 'draft.md', folder / 'report.md')
            report = (folder / 'report.md').read_text()
        self.assertIn('*Synthetic benchmarks*', report)
        self.assertIn('https://arxiv.org/abs/2601.00001)', report)

    def test_et_al_never_stands_for_a_single_name(self):
        """When telling author lists apart leaves one author unnamed, that author is named (APA 8.18)."""
        report = self.render('[@first] and [@second].', [
            paper('first', ['Jane Smith', 'Ana Li', 'Bo Zhang'], 'Alpha'),
            paper('second', ['Jane Smith', 'Ana Li', 'Dan Liu', 'Eva Ruiz'], 'Zeta'),
        ])
        self.assertIn('[Smith, Li, & Zhang, 2026]', report)
        self.assertIn('[Smith, Li, Liu, & Ruiz, 2026]', report)

    def test_author_lists_differing_only_in_given_names_are_told_apart(self):
        """Author lists whose printed surnames match get a, b rather than two identical citations."""
        report = self.render('[@first; @second]', [
            paper('first', ['Jane Smith', 'Ana Li', 'Bo Zhang'], 'Alpha'),
            paper('second', ['Jane Smith', 'Wei Li', 'Bo Zhang'], 'Zeta'),
        ])
        self.assertIn('2026a', report)
        self.assertIn('2026b', report)

    def test_single_author_work_is_listed_before_the_same_authors_group(self):
        """A one-author work comes before that author's multi-author works (APA 9.46)."""
        report = self.render('[@team; @solo]', [
            paper('team', ['Jane Smith', 'Ana Li'], date='2025-01-01'),
            paper('solo', ['Jane Smith'], date='2026-01-01'),
        ])
        listed = report.split('## References')[1]
        self.assertLess(listed.index('Smith, J. (2026'), listed.index('Smith, J., & Li'))

    def test_rendering_onto_the_draft_itself_is_refused(self):
        """Rendering into the draft's own file would destroy its citation keys, so it stops."""
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / 'refs.json').write_text(json.dumps({'references': [paper('one', 'Acme')]}))
            (folder / 'report.md').write_text('Text [@one].')
            with self.assertRaises(SystemExit):
                references.main(folder / 'refs.json', folder / 'report.md', folder / 'report.md')
            self.assertEqual((folder / 'report.md').read_text(), 'Text [@one].')


if __name__ == '__main__':
    unittest.main()
