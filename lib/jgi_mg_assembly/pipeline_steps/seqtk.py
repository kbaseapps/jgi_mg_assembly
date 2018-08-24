from step import Step
import os

SEQTK = "/kb/module/bin/seqtk"
PIGZ = "pigz"

class SeqtkRunner(Step):
    def __init__(self, scratch_dir, output_dir):
        super(SeqtkRunner, self).__init__("SeqTK", "SeqTK", SEQTK, scratch_dir, output_dir, True)

    def run(self, corrected_reads):
        """
        Returns the following dict:
        - command - string, the run command
        - version_string - string, the version tag
        - cleaned_reads - string, path to the zipped cleaned reads file
        """
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
            "cleaned_reads": zipped_output,
            "version_string": self.version_string()
        }
