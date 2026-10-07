"""Tests for config_file_locator.core.

Run with: PYTHONPATH=src python -m unittest discover -s tests
"""

import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from config_file_locator import (
    ConfigNotFoundError,
    find_config,
    locate_config,
)


class FindConfigTests(unittest.TestCase):
    def test_finds_file_in_start_directory(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "app.conf").write_text("ok")
            result = find_config("app.conf", tmp_path)
            self.assertIsNotNone(result)
            self.assertEqual(result, tmp_path / "app.conf")

    def test_finds_file_in_ancestor_directory(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "settings.toml").write_text("ok")
            deep = root / "a" / "b" / "c"
            deep.mkdir(parents=True)
            result = find_config("settings.toml", deep)
            self.assertEqual(result, root / "settings.toml")

    def test_returns_none_when_not_found(self):
        with TemporaryDirectory() as tmp:
            # Use an unlikely name so we don't collide with anything in tmp.
            self.assertIsNone(find_config("__nope__.cfg", tmp))

    def test_skips_directory_with_same_name(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "config").mkdir()
            deeper = tmp_path / "sub"
            deeper.mkdir()
            # A regular file named "config" exists in `deeper`'s parent chain only
            # as a directory at tmp_path. The search should return None.
            self.assertIsNone(find_config("config", deeper))

    def test_empty_filename_returns_none(self):
        with TemporaryDirectory() as tmp:
            self.assertIsNone(find_config("", tmp))

    def test_follows_symlink_to_file(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            real = tmp_path / "real.cfg"
            real.write_text("ok")
            link = tmp_path / "link.cfg"
            link.symlink_to(real)
            result = find_config("link.cfg", tmp_path)
            self.assertEqual(result, link)

    def test_returns_pathlike_object(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "f.json").write_text("{}")
            result = find_config("f.json", tmp_path)
            self.assertIsInstance(result, Path)

    def test_start_as_string_works(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "x.ini").write_text("ok")
            result = find_config("x.ini", str(tmp_path))
            self.assertIsNotNone(result)


class LocateConfigTests(unittest.TestCase):
    def test_raises_when_not_found(self):
        with TemporaryDirectory() as tmp:
            with self.assertRaises(ConfigNotFoundError):
                locate_config("__missing__.conf", tmp)

    def test_raises_subclass_of_filenotfounderror(self):
        with TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                locate_config("__missing__.conf", tmp)

    def test_returns_path_when_found(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "present.yml").write_text("ok")
            result = locate_config("present.yml", tmp_path)
            self.assertEqual(result, tmp_path / "present.yml")


if __name__ == "__main__":
    unittest.main()
