import os
import tempfile
import unittest

from downloads import nombre_archivo, _ruta_segura


class DownloadSafetyTests(unittest.TestCase):
    def test_filename_removes_windows_path_and_invalid_characters(self):
        name = nombre_archivo("https://example.test/files/../../bad:name?.zip", 0)
        self.assertNotIn("/", name)
        self.assertNotIn("\\", name)
        self.assertNotIn(":", name)
        self.assertNotIn("?", name)
        self.assertTrue(name.endswith(".zip"))

    def test_safe_relative_path_stays_inside_destination(self):
        with tempfile.TemporaryDirectory() as folder:
            result = _ruta_segura(folder, "emulator/bin/app.exe")
            self.assertIsNotNone(result)
            self.assertTrue(os.path.commonpath((os.path.realpath(folder), result)) == os.path.realpath(folder))

    def test_parent_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertIsNone(_ruta_segura(folder, "../outside.exe"))
            self.assertIsNone(_ruta_segura(folder, "folder/../../outside.exe"))

    def test_absolute_and_drive_paths_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertIsNone(_ruta_segura(folder, "/tmp/outside.exe"))
            self.assertIsNone(_ruta_segura(folder, "C:/outside.exe"))


if __name__ == "__main__":
    unittest.main()
