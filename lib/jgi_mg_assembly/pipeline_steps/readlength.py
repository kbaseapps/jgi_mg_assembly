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
    Runs readlength.sh on input_file to generate output_file. It then skims that file for several
    values and returns them as a dictionary. The keys to this are:
    count - the number of reads
    bases - the total number of bases
    max - the length of the longest read
    min - the length of the shortest read
    avg - the average read length
    median - the median read length
    mode - the mode of the mean lengths
    std_dev - the standard deviation of read lengths
    output_file - the output file from readlength, containing a histogram of reads info

    This also calculates the histogram, but it left out for now. (Unless it's needed later)

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
    ret_value = dict()
    with open(output_file, "r") as read_len_file:
        line_mapping = {
            "#Reads:": ("count", int),
            "#Bases:": ("bases", int),
            "#Max:" : ("max", int),
            "#Min:": ("min", int),
            "#Avg:": ("avg", float),
            "#Median:": ("median", int),
            "#Mode:": ("mode", int),
            "#Std_Dev:": ("std_dev", float),
        }
        for line in read_len_file:
            chopped = line.split()
            if chopped[0] in line_mapping:
                key, map_fn = line_mapping[chopped[0]]
                ret_value[key] = map_fn(chopped[1])
    ret_value["output_file"] = output_file
    return ret_value
