from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

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


class TestThumbnailFromFilePath(unittest.TestCase):
    def _run(self, ffprobe_stdout=b"10.0", ffprobe_rc=0, ffmpeg_stdout=b"PNG", ffmpeg_rc=0):
        """Run thumbnail_from_file_path with mocked subprocesses."""
        with patch("resolve_api._ffmpeg_path", return_value="/usr/bin/ffmpeg"), \
             patch("resolve_api._ffprobe_path", return_value="/usr/bin/ffprobe"), \
             patch("resolve_api.subprocess") as mock_sub:

            probe_result = MagicMock()
            probe_result.returncode = ffprobe_rc
            probe_result.stdout = ffprobe_stdout

            ffmpeg_result = MagicMock()
            ffmpeg_result.returncode = ffmpeg_rc
            ffmpeg_result.stdout = ffmpeg_stdout

            mock_sub.run.side_effect = [probe_result, ffmpeg_result]

            return mock_sub, resolve_api.thumbnail_from_file_path("/fake/clip.mov")

    def test_returns_png_bytes_on_success(self):
        _, result = self._run()
        self.assertEqual(result, b"PNG")

    def test_returns_none_when_ffmpeg_fails(self):
        _, result = self._run(ffmpeg_rc=1, ffmpeg_stdout=b"")
        self.assertIsNone(result)

    def test_returns_none_when_ffmpeg_returns_empty_output(self):
        _, result = self._run(ffmpeg_stdout=b"")
        self.assertIsNone(result)

    def test_returns_none_when_file_path_is_empty(self):
        result = resolve_api.thumbnail_from_file_path("")
        self.assertIsNone(result)

    def test_returns_none_when_ffmpeg_not_found(self):
        with patch("resolve_api._ffmpeg_path", side_effect=FileNotFoundError):
            result = resolve_api.thumbnail_from_file_path("/fake/clip.mov")
        self.assertIsNone(result)

    def test_seeks_to_midpoint(self):
        mock_sub, _ = self._run(ffprobe_stdout=b"20.0")
        ffmpeg_call_args = mock_sub.run.call_args_list[1][0][0]
        self.assertIn("10.0", ffmpeg_call_args)

    def test_seeks_to_zero_when_probe_fails(self):
        mock_sub, _ = self._run(ffprobe_rc=1, ffprobe_stdout=b"")
        ffmpeg_call_args = mock_sub.run.call_args_list[1][0][0]
        self.assertIn("0.0", ffmpeg_call_args)

    def test_returns_none_when_subprocess_raises(self):
        with patch("resolve_api._ffmpeg_path", return_value="/usr/bin/ffmpeg"), \
             patch("resolve_api._ffprobe_path", return_value="/usr/bin/ffprobe"), \
             patch("resolve_api.subprocess") as mock_sub:
            mock_sub.run.side_effect = [MagicMock(returncode=0, stdout=b"5.0"),
                                        Exception("process error")]
            result = resolve_api.thumbnail_from_file_path("/fake/clip.mov")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
