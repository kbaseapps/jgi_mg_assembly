import unittest
import util
import os
from copy import deepcopy
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
        pipeline_output = {
            "bbmap": {
                "stats_file": self.bbmap_stats_file,
                "coverage_file": self.cov_stats,
                "command": "bbmap cmd",
                "version_string": "bbmap version"
            },
            "stats": {
                "stats_txt": self.assembly_stats_file,
                "stats_tsv": self.assembly_stats_tsv,
                "command": "stats command",
                "version_string": "stats version"
            },
            "rqcfilter": {
                "run_log": self.rqcfilter_log,
                "command": "rqcfilter command",
                "version_string": "rqcfilter version"
            },
            "reads_info_prefiltered": {
                "count": 10000,
                "command": "reads_info_prefiltered command",
                "version_string": "reads info version"
            },
            "reads_info_filtered": {
                "count": 8000,
                "command": "reads_info_filtered command",
                "version_string": "reads info version"
            },
            "reads_info_corrected": {
                "count": 7000,
                "command": "reads_info_corrected command",
                "version_string": "reads info version"
            },
            "bfc": {
                "command": "bfc command",
                "version_string": "bfc version"
            },
            "seqtk": {
                "command": "seqtk command",
                "version_string": "seqtk verseion"
            },
            "spades": {
                "command": "spades command",
                "version_string": "spades version"
            },
            "agp": {
                "command": "agp command",
                "version_string": "agp version"
            },
        }
        report_info = self._get_report_util().make_report(
            pipeline_output, util.get_ws_name(), []
        )
        self.assertIn('report_ref', report_info)
        self.assertIn('report_name', report_info)

    def test_make_report_bad_inputs(self):
        pipeline_output = {
            "bbmap": {
                "stats_file": self.bbmap_stats_file,
                "coverage_file": self.cov_stats,
                "command": "bbmap cmd",
                "version_string": "bbmap version"
            },
            "stats": {
                "stats_txt": self.assembly_stats_file,
                "stats_tsv": self.assembly_stats_tsv,
                "command": "stats command",
                "version_string": "stats version"
            },
            "rqcfilter": {
                "run_log": self.rqcfilter_log,
                "command": "rqcfilter command",
                "version_string": "rqcfilter version"
            },
            "reads_info_prefiltered": {
                "count": 10000,
                "command": "reads_info_prefiltered command",
                "version_string": "reads info version"
            },
            "reads_info_filtered": {
                "count": 8000,
                "command": "reads_info_filtered command",
                "version_string": "reads info version"
            },
            "reads_info_corrected": {
                "count": 7000,
                "command": "reads_info_corrected command",
                "version_string": "reads info version"
            },
            "bfc": {
                "command": "bfc command",
                "version_string": "bfc version"
            },
            "seqtk": {
                "command": "seqtk command",
                "version_string": "seqtk verseion"
            },
            "spades": {
                "command": "spades command",
                "version_string": "spades version"
            },
            "agp": {
                "command": "agp command",
                "version_string": "agp version"
            },
        }
        ru = self._get_report_util()
        with self.assertRaises(AssertionError) as err:
            ru.make_report(None, util.get_ws_name(), [])
        self.assertIn("Pipeline output not found!", str(err.exception))

        for key in ["reads_info_prefiltered", "reads_info_filtered", "reads_info_corrected"]:
            output_copy = deepcopy(pipeline_output)
            del output_copy[key]
            with self.assertRaises(AssertionError) as err:
                ru.make_report(output_copy, util.get_ws_name(), [])
            self.assertIn("Required reads info '{}' is not present!".format(key), str(err.exception))

        with self.assertRaises(AssertionError) as err:
            ru.make_report(pipeline_output, None, [])
        self.assertIn("A workspace name is required", str(err.exception))
