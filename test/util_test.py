import os
import unittest
from jgi_mg_assembly.utils.util import mkdir


class report_util_test(unittest.TestCase):

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

        # try to make a path that already exists (should fail silently)
        self.assertTrue(os.path.exists("data"))
        mkdir("data")
