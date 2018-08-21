from step import Step
import os

SEQTK = "/kb/module/bin/seqtk"
PIGZ = "pigz"

class SeqtkRunner(Step):
    def __init__(self, scratch_dir, output_dir):
        super(SeqtkRunner, self).__init__("SeqTK", SEQTK, scratch_dir, True)
        self.output_dir = output_dir

    def run(self, corrected_reads):
        zipped_output = os.path.join(self.output_dir, "bfc", "input.corr.fastq.gz")
        seqtk_params = [
            "dropse",
            corrected_reads,
            "|",
            PIGZ,
            "-c",
            "-",
            "-p",
            "4",
            "-2",
            ">",
            zipped_output
        ]
        (exit_code, command) = super(SeqtkRunner, self).run(*seqtk_params)
        if exit_code != 0:
            raise RuntimeError("Error while running seqtk!")

        return {
            "command": command,
            "cleaned_reads": zipped_output
        }
