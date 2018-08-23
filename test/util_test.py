import os
import unittest
from jgi_mg_assembly.utils.util import (
    mkdir,
    file_to_log
)
import util

class util_test(unittest.TestCase):

    def test_mkdir_ok(self):
        some_path = os.path.join("a_dir", "another_dir", "a_deep_dir")
        self.assertFalse(os.path.exists(some_path))
        mkdir(some_path)
        self.assertTrue(os.path.exists(some_path))

    def test_mkdir_fail(self):
        # try to make an empty path
        with self.assertRaises(ValueError) as cm:
            mkdir(None)
        self.assertIn("A path is required", str(cm.exception))

        # try to make a path that already exists (should fail silently, but not crash
        self.assertTrue(os.path.exists("data"))
        mkdir("data")

    def test_file_to_log_ok(self):
        log_file_path = util.file_to_scratch(os.path.join("data", "dummy_log.txt"), overwrite=True)
        with util.captured_stdout() as (out, err):
            file_to_log(log_file_path)
        outtxt = out.getvalue().strip()
        self.assertEqual(outtxt, "I am a log.")

    def test_file_to_log_fail(self):
        # try to read a file that doesn't exist
        with self.assertRaises(ValueError) as e:
            file_to_log("not_a_path")
        self.assertIn("File path does not exist", str(e.exception))
