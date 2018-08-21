from step import Step
from jgi_mg_assembly.utils.util import mkdir
import os

BFC = "/kb/module/bin/bfc"
class BFCRunner(Step):
    def __init__(self, scratch_dir, output_dir):
        super(BFCRunner, self).__init__("BFC", BFC, scratch_dir, True)
        self.output_dir = output_dir

    def run(self, filtered_reads_file, debug=False):
        """
        Takes in a (filtered) reads file, returns a dict with the keys:
        command - the command that was run
        corrected_reads - the corrected fastq file
        """
        # command:
        # bfc <flag params> filtered_fastq_file
        mkdir(os.path.join(self.output_dir, "bfc"))
        bfc_output_file = os.path.join(self.output_dir, "bfc", "bfc_output.fastq")
        bfc_params = ["-1", "-k", "21", "-t", "10"]

        if not debug:
            bfc_params = bfc_params + ["-s", "10g"]
        bfc_params = bfc_params + [filtered_reads_file, ">", bfc_output_file]

        (exit_code, command) = super(BFCRunner, self).run(*bfc_params)

        if exit_code != 0:
            raise RuntimeError("An error occurred while running BFC!")
        return {
            "command": command,
            "corrected_reads": bfc_output_file
        }