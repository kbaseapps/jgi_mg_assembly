"""
Handles running SPAdes from command line, using the command and parameters provided
by the JGI Metagenome Assembly Pipeline.
"""
import os
import subprocess
from jgi_mg_assembly.utils.util import (
    mkdir,
    file_to_log
)

SPADES = "/opt/SPAdes-3.12.0-Linux/bin/spades.py"

class SpadesRunner(object):
    def __init__(self, output_dir, scratch_dir):
        self.output_dir = output_dir
        self.scratch_dir = scratch_dir

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

        spades_cmd = [SPADES, "--only-assembler",
                      "-k", ",".join(map(str, used_kmers)),
                      "--meta",
                      "-t", "32",
                      "-m", "2000",
                      "-o", spades_output_dir,
                      "--12", input_file]

        print("SPAdes input reads info:\n{}\n".format("="*24))
        file_to_log(reads_info["output_file"])
        print("{}\nEnd SPAdes input reads info\n".format("="*27))
        print("Running SPAdes with command:")
        print(" ".join(spades_cmd))
        p = subprocess.Popen(spades_cmd, cwd=self.scratch_dir, shell=False)
        retcode = p.wait()

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

        if retcode != 0:
            raise RuntimeError("Errors occurred while running spades. Check the logs for details. Unable to continue pipeline.")

        return spades_output_dir
