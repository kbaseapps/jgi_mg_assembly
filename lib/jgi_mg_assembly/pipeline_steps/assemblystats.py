from step import Step
import os
from jgi_mg_assembly.utils.util import mkdir


BBTOOLS_STATS = "/kb/module/bbmap/stats.sh"

class StatsRunner(Step):
    def __init__(self, scratch_dir, output_dir):
        super(StatsRunner, self).__init__("BBTools stats", BBTOOLS_STATS, scratch_dir, False)
        self.output_dir = output_dir

    def run(self, scaffold_file):
        stats_output_dir = os.path.join(self.output_dir, "assembly_stats")
        mkdir(stats_output_dir)
        stats_output = os.path.join(stats_output_dir, "assembly.scaffolds.fasta.stats.tsv")
        stats_stdout = os.path.join(stats_output_dir, "assembly.scaffolds.fasta.stats.txt")
        stats_stderr = os.path.join(stats_output_dir, "stderr.out")

        stats_first_params = [
            "format=6",
            "in={}".format(scaffold_file),
            "1>",
            stats_output,
            "2>",
            stats_stderr
        ]
        (exit_code, command) = super(StatsRunner, self).run(*stats_first_params)
        if exit_code != 0:
            raise RuntimeError("Unable to run first pass at stats to generate tab-delimited files!")

        stats_second_params = [
            "in={}".format(scaffold_file),
            "1>",
            stats_stdout,
            "2>>",
            stats_stderr
        ]
        (exit_code, command) = super(StatsRunner, self).run(*stats_second_params)
        if exit_code != 0:
            raise RuntimeError("Unable to run second pass at stats to generate standard text files!")

        return {
            "stats_tsv": stats_output,
            "stats_txt": stats_stdout,
            "stats_err": stats_stderr
        }