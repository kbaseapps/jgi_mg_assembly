import unittest
import util
import os

from jgi_mg_assembly.utils.report import ReportUtil


class report_util_test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # * bbmap_stats - the generated stats from BBMap, that's usually sent to stderr
        # * covstats - the coverage stats from BBMap
        # * assembly_stats - stats from the assembly (made with BBTools stats.sh)
        # * assembly_tsv - a TSV version of most of those stats (with some funky headers)
        #
        # reads_counts is another dict, with reads counted at different points in the pipeline
        # * pre_filter - number of reads before any filtering, as uploaded by the user
        # * filtered - number of reads after running RQCFilter
        # * corrected - number of reads after running BFC
        cls.config = util.get_config()
        cls.callback_url = os.environ['SDK_CALLBACK_URL']
        cls.scratch_dir = cls.config['scratch']
        cls.assembly_stats_tsv = util.file_to_scratch(os.path.join("data", "assembly.scaffolds.fasta.stats.tsv"), overwrite=True)
        cls.assembly_stats_file = util.file_to_scratch(os.path.join("data", "assembly.scaffolds.fasta.stats.txt"), overwrite=True)
        cls.cov_stats = util.file_to_scratch(os.path.join("data", "covstats.txt"), overwrite=True)
        cls.bbmap_stats_file = util.file_to_scratch(os.path.join("data", "bbmap_stats.txt"), overwrite=True)
        cls.rqcfilter_log = util.file_to_scratch(os.path.join("data", "rqcfilter_log.txt"), overwrite=True)

    @classmethod
    def tearDownClass(cls):
        util.tear_down_workspace()

    def _get_report_util(self):
        return ReportUtil(self.callback_url, self.scratch_dir)

    def test_make_report_ok(self):
        # stats_file, coverage_file, workspace_name, saved_objects
        stats_files = {
            "bbmap_stats": self.bbmap_stats_file,
            "covstats": self.cov_stats,
            "assembly_stats": self.assembly_stats_file,
            "assembly_tsv": self.assembly_stats_tsv,
            "rqcfilter_log": self.rqcfilter_log
        }
        reads_counts = {
            "pre_filter": {
                "count": 10000
            },
            "filtered": {
                "count": 8000
            },
            "corrected": {
                "count": 7000
            }
        }
        report_info = self._get_report_util().make_report(
            stats_files, reads_counts, util.get_ws_name(), []
        )
        self.assertIn('report_ref', report_info)
        self.assertIn('report_name', report_info)

    def test_make_report_bad_inputs(self):
        reads_counts = {
            "pre_filter": {
                "count": 10000
            },
            "filtered": {
                "count": 8000
            },
            "corrected": {
                "count": 7000
            }
        }
        stats_files = {
            "bbmap_stats": self.bbmap_stats_file,
            "covstats": self.cov_stats,
            "assembly_stats": self.assembly_stats_file,
            "assembly_tsv": self.assembly_stats_tsv,
            "rqcfilter_log": self.rqcfilter_log
        }

        ru = self._get_report_util()
        with self.assertRaises(ValueError) as cm:
            ru.make_report(None, reads_counts, util.get_ws_name(), [])
        self.assertIn("A dictionary of stats_files is required", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            ru.make_report("not_a_file", reads_counts, util.get_ws_name(), [])
        self.assertIn("A dictionary of stats_files is required", str(cm.exception))

        for key in stats_files:
            stats_copy = stats_files.copy()
            del stats_copy[key]
            with self.assertRaises(ValueError) as cm:
                ru.make_report(stats_copy, reads_counts, util.get_ws_name(), [])
            self.assertIn("Required stats file '{}' is not present!".format(key), str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            ru.make_report(stats_files, None, util.get_ws_name(), [])
        self.assertIn("A dictionary of reads_info is required", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            ru.make_report(stats_files, "not a file", util.get_ws_name(), [])
        self.assertIn("A dictionary of reads_info is required", str(cm.exception))

        for key in reads_counts:
            reads_copy = reads_counts.copy()
            del reads_copy[key]
            with self.assertRaises(ValueError) as cm:
                ru.make_report(stats_files, reads_copy, util.get_ws_name(), [])
            self.assertIn("Required reads info '{}' is not present!".format(key), str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            ru.make_report(stats_files, reads_counts, None, [])
        self.assertIn("A workspace name is required", str(cm.exception))
