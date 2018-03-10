"""
A wrapper around BBTools readlength.sh. This assumes (well, for now) that BBTools is installed
locally.

It's pretty simple. This just provides a single function that takes in a single input FASTQ file,
and an output file path. It then writes the generated readlength output to the given file path
and returns the number of reads. If there's any problems, this just raises a ValueError.
"""
import os
import subprocess

BBTOOLS_READLEN = "/kb/module/bbmap/readlength.sh"


def readlength(input_file, output_file):
    """
    Runs readlength.sh on input_file to generate output_file. It then skims that file for the
    '#Reads:' line, and returns the numeric value given there.

    The path to the output file's directory is expected to exist. If not, this might cause an
    error. If the output file exists, it will be overwritten.
    """
    if not os.path.exists(input_file):
        raise ValueError("The input file '{}' can't be found!".format(input_file))

    readlength_cmd = [
        BBTOOLS_READLEN,
        "in={}".format(input_file),
        "1>|",
        output_file
    ]

    p = subprocess.Popen(" ".join(readlength_cmd), shell=True)
    retcode = p.wait()
    if retcode != 0:
        raise ValueError("An error occurred while running readlength.sh!")

    if not os.path.exists(output_file):
        raise RuntimeError("The output file '{}' appears not to have been made!")
    with open(output_file, "r") as read_len_file:
        for line in read_len_file:
            if line.startswith("#Reads:"):
                num_reads = line.split()[-1]

    return num_reads
