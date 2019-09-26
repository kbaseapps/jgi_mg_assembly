from jgi_mg_assembly.pipeline_steps.step import Step
import os
from jgi_mg_assembly.utils.util import mkdir

BBMAP = "/kb/module/bbmap/bbmap.sh"

class BBMapRunner(Step):
    def __init__(self, scratch_dir, output_dir):
        super(BBMapRunner, self).__init__("BBMap", "BBTools", BBMAP, scratch_dir, output_dir, False)

    def run(self, reads_file, contigs_file):
        """
        Runs BBMap to map the given reads file (FASTQ) to the contigs file (FASTA).
        Returns the paths to the SAM file, coverage stats, and overall BBMap stats as
        map_file, coverage_file, and stats_file, respectively.
        """
        bbmap_output_dir = os.path.join(self.output_dir, "readMappingPairs")
        mkdir(bbmap_output_dir)

        sam_output = os.path.join(bbmap_output_dir, "pairedMapped.sam.gz")
        coverage_stats_output = os.path.join(bbmap_output_dir, "covstats.txt")
        bbmap_stats_output = os.path.join(bbmap_output_dir, "bbmap_stats.txt")

        bbmap_params = [
            "-Xmx100g",
            "nodisk=true",
            "interleaved=true",
            "ambiguous=random",
            "in={}".format(reads_file),
            "ref={}".format(contigs_file),
            "out={}".format(sam_output),
            "covstats={}".format(coverage_stats_output),
            "2>",
            bbmap_stats_output
        ]
        (exit_code, command) = super(BBMapRunner, self).run(*bbmap_params)
        if exit_code != 0:
            raise RuntimeError("An error occurred while running BBMap!")
        return {
            "map_file": sam_output,
            "coverage_file": coverage_stats_output,
            "stats_file": bbmap_stats_output,
            "command": command,
            "version_string": self.version_string()
        }
