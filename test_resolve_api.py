from __future__ import annotations

import unittest
from unittest.mock import MagicMock

import resolve_api


class TestNormalizeKeywords(unittest.TestCase):
    def test_comma_separated_string(self):
        self.assertEqual(resolve_api._normalize_keywords("a, b, c"), ["a", "b", "c"])

    def test_semicolon_separated_string(self):
        self.assertEqual(resolve_api._normalize_keywords("a; b; c"), ["a", "b", "c"])

    def test_single_value(self):
        self.assertEqual(resolve_api._normalize_keywords("tag"), ["tag"])

    def test_list_input(self):
        self.assertEqual(resolve_api._normalize_keywords(["a", "b"]), ["a", "b"])

    def test_none_returns_empty(self):
        self.assertEqual(resolve_api._normalize_keywords(None), [])

    def test_empty_string_returns_empty(self):
        self.assertEqual(resolve_api._normalize_keywords(""), [])

    def test_strips_whitespace(self):
        self.assertEqual(resolve_api._normalize_keywords("  tag  "), ["tag"])


class TestDedupePreserveOrder(unittest.TestCase):
    def test_removes_case_insensitive_duplicates(self):
        self.assertEqual(resolve_api._dedupe_preserve_order(["tag", "Tag", "TAG"]), ["tag"])

    def test_preserves_first_occurrence(self):
        self.assertEqual(resolve_api._dedupe_preserve_order(["Tag", "tag"]), ["Tag"])

    def test_preserves_order(self):
        self.assertEqual(resolve_api._dedupe_preserve_order(["b", "a", "c"]), ["b", "a", "c"])

    def test_empty_list(self):
        self.assertEqual(resolve_api._dedupe_preserve_order([]), [])


class TestMergeKeywords(unittest.TestCase):
    def test_set_replaces_existing(self):
        self.assertEqual(resolve_api.merge_keywords(["old"], ["new"], "set"), ["new"])

    def test_set_dedupes_incoming(self):
        self.assertEqual(resolve_api.merge_keywords([], ["a", "A"], "set"), ["a"])

    def test_replace_is_alias_for_set(self):
        self.assertEqual(resolve_api.merge_keywords(["old"], ["new"], "replace"), ["new"])

    def test_append_combines(self):
        self.assertEqual(resolve_api.merge_keywords(["a"], ["b"], "append"), ["a", "b"])

    def test_append_dedupes(self):
        self.assertEqual(resolve_api.merge_keywords(["a"], ["a", "b"], "append"), ["a", "b"])

    def test_append_case_insensitive_dedupe(self):
        self.assertEqual(resolve_api.merge_keywords(["Tag"], ["tag", "new"], "append"), ["Tag", "new"])

    def test_set_empty_clears(self):
        self.assertEqual(resolve_api.merge_keywords(["old"], [], "set"), [])

    def test_unknown_mode_raises(self):
        with self.assertRaises(ValueError):
            resolve_api.merge_keywords([], [], "unknown")


class TestGetKeywords(unittest.TestCase):
    def _make_item(self, metadata: dict, clip_property: str = "") -> MagicMock:
        item = MagicMock()
        item.GetMetadata.side_effect = lambda key=None: metadata if key is None else metadata.get(key)
        item.GetClipProperty.return_value = clip_property
        return item

    def test_reads_from_metadata_dict(self):
        item = self._make_item({"Keywords": "a, b"})
        self.assertEqual(resolve_api.get_keywords(item), ["a", "b"])

    def test_falls_back_to_explicit_key(self):
        item = MagicMock()
        item.GetMetadata.side_effect = lambda key=None: {} if key is None else ("a" if key == "Keywords" else None)
        item.GetClipProperty.return_value = ""
        self.assertEqual(resolve_api.get_keywords(item), ["a"])

    def test_falls_back_to_clip_property(self):
        item = MagicMock()
        item.GetMetadata.side_effect = lambda key=None: {} if key is None else None
        item.GetClipProperty.return_value = "x; y"
        self.assertEqual(resolve_api.get_keywords(item), ["x", "y"])

    def test_returns_empty_when_nothing(self):
        item = MagicMock()
        item.GetMetadata.side_effect = lambda key=None: {} if key is None else None
        item.GetClipProperty.return_value = ""
        self.assertEqual(resolve_api.get_keywords(item), [])


class TestSetKeywords(unittest.TestCase):
    def test_returns_true_on_success(self):
        item = MagicMock()
        item.SetMetadata.return_value = True
        self.assertTrue(resolve_api.set_keywords(item, ["a", "b"]))
        item.SetMetadata.assert_called_once_with("Keywords", "a, b")

    def test_returns_false_on_failure(self):
        item = MagicMock()
        item.SetMetadata.return_value = False
        self.assertFalse(resolve_api.set_keywords(item, ["a"]))

    def test_returns_false_on_none(self):
        item = MagicMock()
        item.SetMetadata.return_value = None
        self.assertFalse(resolve_api.set_keywords(item, ["a"]))

    def test_empty_keywords_writes_empty_string(self):
        item = MagicMock()
        item.SetMetadata.return_value = True
        resolve_api.set_keywords(item, [])
        item.SetMetadata.assert_called_once_with("Keywords", "")


if __name__ == "__main__":
    unittest.main()
