import json
import tempfile
import unittest
from pathlib import Path

import main


class DraftPlannerTests(unittest.TestCase):
    def test_hashtags_are_normalized_and_deduplicated(self):
        self.assertEqual(main.normalize_hashtags("#travel, food #travel"), ["travel", "food"])

    def test_hashtag_limit_is_enforced(self):
        with self.assertRaisesRegex(ValueError, "no more than 30"):
            main.normalize_hashtags(" ".join(f"tag{i}" for i in range(31)))

    def test_caption_limit_is_enforced(self):
        with self.assertRaisesRegex(ValueError, "limit is 2200"):
            main.create_draft("A title", "x" * 2_201, [])

    def test_draft_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "drafts.json"
            draft = main.create_draft("Launch", "Hello world", ["hello"], "Friday")
            main.save_drafts([draft], path)
            self.assertEqual(main.load_drafts(path), [draft])
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))[0]["title"], "Launch")

    def test_missing_file_is_an_empty_collection(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(main.load_drafts(Path(directory) / "missing.json"), [])


if __name__ == "__main__":
    unittest.main()
