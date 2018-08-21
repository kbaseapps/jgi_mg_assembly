"""
Handles running SPAdes from command line, using the command and parameters provided
by the JGI Metagenome Assembly Pipeline.
"""
from step import Step
import os
import subprocess
from jgi_mg_assembly.utils.util import (
    mkdir,
    file_to_log
)

SPADES = "/opt/SPAdes-3.12.0-Linux/bin/spades.py"

class SpadesRunner(Step):
    def __init__(self, scratch_dir, output_dir):
        super(SpadesRunner, self).__init__('SPAdes', SPADES, scratch_dir, False)
        self.output_dir = output_dir

    def run(self, input_file, reads_info, options):
        """
        Runs spades, returns the generated output directory name. It's full of standard files.
        This will use (by default) k=33,55,77,99,127.
        However, if the max read length < any of those k, that'll be omitted.
        For example, if your input reads are such that the longest one is 100 bases, this'll
        omit k=127.
        """
        spades_output_dir = os.path.join(self.output_dir, "spades", "spades3")
        mkdir(spades_output_dir)

        spades_kmers = [33, 55, 77, 99, 127]
        used_kmers = [k for k in spades_kmers if k <= reads_info["avg"]]

        spades_params = ["--only-assembler",
                         "-k", ",".join(map(str, used_kmers)),
                         "--meta",
                         "-t", "32",
                         "-m", "2000",
                         "-o", spades_output_dir,
                         "--12", input_file]

        print("SPAdes input reads info:\n{}\n".format("="*24))
        file_to_log(reads_info["output_file"])
        print("{}\nEnd SPAdes input reads info\n".format("="*27))

        (exit_code, command) = super(SpadesRunner, self).run(*spades_params)

        # get the SPAdes logs and cat them to stdout
        print("Done running SPAdes")
        print("See log transcripts below for details")

        log_files = ["warnings.log", "params.txt", "spades.log"]
        for f in log_files:
            log_file = os.path.join(spades_output_dir, f)
            if os.path.exists(log_file):
                print("SPAdes log file {}:\n{}\n".format(f, "="*(17 + len(f))))
                file_to_log(log_file)
                print("{}\nEnd SPAdes log file {}\n".format("="*(20 + len(f)), f))

        if exit_code != 0:
            raise RuntimeError("Errors occurred while running spades. Check the logs for details. Unable to continue pipeline.")

        return_dict = {
            "command": command,
            "output_dir": spades_output_dir,
            "run_log": os.path.join(spades_output_dir, "spades.log"),
            "params_log": os.path.join(spades_output_dir, "params.txt")
        }
        warnings_log = os.path.join(spades_output_dir, "warnings.log")
        if os.path.exists(warnings_log):
            return_dict["warnings_log"] = warnings_log
        scaffolds = os.path.join(spades_output_dir, "scaffolds.fasta")
        if os.path.exists(scaffolds):
            return_dict["scaffolds_file"] = scaffolds
        contigs = os.path.join(spades_output_dir, "contigs.fasta")
        if os.path.exists(contigs):
            return_dict["contigs_file"] = contigs
        return return_dict