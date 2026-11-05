import unittest
from pathlib import Path

import yaml

SKILL = Path(__file__).parents[1] / 'SKILL.md'


class SkillFileTest(unittest.TestCase):
    """The skill's own files load as the harness reads them."""

    def test_frontmatter_is_valid_yaml(self):
        """The frontmatter parses, so the harness can load the skill and match its description."""
        frontmatter = SKILL.read_text().split('---')[1]
        parsed = yaml.safe_load(frontmatter)
        self.assertEqual(parsed['name'], 'state-of-the-art-research')
        self.assertLess(len(parsed['description']), 1024)


if __name__ == '__main__':
    unittest.main()
