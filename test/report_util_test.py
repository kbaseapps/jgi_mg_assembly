import unittest
import util
import os

from jgi_mg_assembly.utils.report import ReportUtil


class report_util_test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = util.get_config()
        cls.callback_url = os.environ['SDK_CALLBACK_URL']
        cls.scratch_dir = cls.config['scratch']
        cls.stats_file = util.file_to_scratch(os.path.join("data", "stats.tsv"), overwrite=True)
        cls.cov_file = util.file_to_scratch(os.path.join("data", "coverage.tsv"), overwrite=True)

    @classmethod
    def tearDownClass(cls):
        util.tear_down_workspace()

    def _get_report_util(self):
        return ReportUtil(self.callback_url, self.scratch_dir)

    def test_make_report_ok(self):
        # stats_file, coverage_file, workspace_name, saved_objects
        report_info = self._get_report_util().make_report(
            self.stats_file, self.cov_file, util.get_ws_name(), []
        )
        self.assertIn('report_ref', report_info)
        self.assertIn('report_name', report_info)

    def test_make_report_bad_inputs(self):
        ru = self._get_report_util()
        with self.assertRaises(ValueError) as cm:
            ru.make_report(None, self.cov_file, util.get_ws_name(), [])
        self.assertIn("A stats file is required", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            ru.make_report("not_a_file", self.cov_file, util.get_ws_name(), [])
        self.assertIn("does not appear to exist", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            ru.make_report(self.stats_file, None, util.get_ws_name(), [])
        self.assertIn("A coverage file is required", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            ru.make_report(self.stats_file, "not a file", util.get_ws_name(), [])
        self.assertIn("does not appear to exist", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            ru.make_report(self.stats_file, self.cov_file, None, [])
        self.assertIn("A workspace name is required", str(cm.exception))

    def test_mkdir_ok(self):
        some_path = os.path.join("a_dir", "another_dir", "a_deep_dir")
        self.assertFalse(os.path.exists(some_path))
        self._get_report_util()._mkdir_p(some_path)
        self.assertTrue(os.path.exists(some_path))

    def test_mkdir_fail(self):
        ru = self._get_report_util()
        # try to make an empty path
        with self.assertRaises(ValueError) as cm:
            ru._mkdir_p(None)
        self.assertIn("A path is required", str(cm.exception))

        # try to make a path that already exists (should fail silently)
        self.assertTrue(os.path.exists("data"))
        ru._mkdir_p("data")

        # try to make a path without permission, like something under /usr
        # note - this works fine in kb-sdk test, as that runs as root.
        # not sure how to trigger the final exception, so ignoring this step.
        # with self.assertRaises(Exception):
        #     ru._mkdir_p(os.path.join(os.sep, "usr", "bin", "foo"))
