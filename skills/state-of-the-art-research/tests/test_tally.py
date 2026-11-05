import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'scripts' / 'tally.py'
spec = importlib.util.spec_from_file_location('tally', SCRIPT)
tally = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tally)


class TallyTest(unittest.TestCase):
    """Counting sources across researcher notes."""

    def count(self, *notes):
        with tempfile.TemporaryDirectory() as directory:
            paths = []
            for index, text in enumerate(notes):
                path = Path(directory) / f'notes{index}.md'
                path.write_text('# Notes\n\n## Reading tally\n\n' + text)
                paths.append(path)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                tally.main(paths)
            return output.getvalue()

    def test_every_page_of_one_arxiv_paper_is_one_source(self):
        """Abstract, HTML with an anchor, PDF with a query and Hugging Face pages are one paper."""
        output = self.count(
            '### Read in full\n- paper: https://arxiv.org/html/2601.00001v2#S4\n',
            '### Glimpsed\n- paper: https://arxiv.org/abs/2601.00001\n'
            '- paper: http://www.arxiv.org/pdf/2601.00001v1.pdf?download=1\n'
            '- paper: https://huggingface.co/papers/2601.00001\n'
            '- paper: https://ArXiv.org/abs/2601.00001\n')
        self.assertIn('papers: 1 read in full of 1 found', output)

    def test_a_source_read_by_anyone_counts_as_read(self):
        """A source glimpsed by one reader and read in full by another counts once, as read."""
        output = self.count('### Glimpsed\n- article: https://example.org/post/\n',
                            '### Read in full\n- article: https://example.org/post\n'
                            '### Glimpsed\n- article: https://example.org/other\n')
        self.assertIn('articles: 1 read in full of 2 found', output)

    def test_openreview_and_acl_pages_of_one_paper_are_one_source(self):
        """A paper's OpenReview forum and PDF, or its ACL Anthology page and PDF, are one source."""
        output = self.count('### Read in full\n- paper: https://openreview.net/pdf?id=X1\n'
                            '- paper: https://aclanthology.org/2026.acl-long.12.pdf\n'
                            '### Glimpsed\n- paper: https://openreview.net/forum?id=X1\n'
                            '- paper: https://aclanthology.org/2026.acl-long.12/\n')
        self.assertIn('papers: 2 read in full of 2 found', output)

    def test_pages_told_apart_by_their_query_stay_distinct(self):
        """OpenReview or Hacker News pages that differ only in their query are different sources."""
        output = self.count('### Read in full\n- paper: https://openreview.net/forum?id=paperA\n'
                            '### Glimpsed\n- paper: https://openreview.net/forum?id=paperB\n'
                            '- article: https://news.ycombinator.com/item?id=1\n'
                            '- article: https://news.ycombinator.com/item?id=2\n')
        self.assertIn('papers: 1 read in full of 2 found', output)
        self.assertIn('articles: 0 read in full of 2 found', output)

    def test_a_source_listed_under_two_kinds_stops_the_count(self):
        """A source one reader calls a paper and another an article is rejected, not miscounted."""
        with self.assertRaises(SystemExit):
            self.count('### Read in full\n- paper: https://www.example.org/research/x\n',
                       '### Glimpsed\n- article: https://www.example.org/research/x\n')

    def test_a_line_outside_the_format_stops_the_count(self):
        """A tally line in link form is rejected rather than silently dropped."""
        with self.assertRaises(SystemExit):
            self.count('### Read in full\n- paper: [Title](https://arxiv.org/abs/2601.00001)\n')

    def test_an_unknown_heading_stops_the_count(self):
        """A heading other than Read in full or Glimpsed is rejected, not read as glimpsed."""
        with self.assertRaises(SystemExit):
            self.count('### Read in full (end to end)\n- paper: https://example.org/a\n')


if __name__ == '__main__':
    unittest.main()
