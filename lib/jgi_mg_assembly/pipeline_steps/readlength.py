"""
A wrapper around BBTools readlength.sh. This assumes (well, for now) that BBTools is installed
locally.

It's pretty simple. This just provides a single function that takes in a single input FASTQ file,
and an output file path. It then writes the generated readlength output to the given file path
and returns the number of reads. If there's any problems, this just raises a ValueError.
"""
from __future__ import print_function
import os
from jgi_mg_assembly.pipeline_steps.step import Step
from jgi_mg_assembly.utils.util import mkdir

BBTOOLS_READLEN = "/kb/module/bbmap/readlength.sh"

class ReadLengthRunner(Step):
    def __init__(self, scratch_dir, output_dir):
        super(ReadLengthRunner, self).__init__("readlength", "BBTools", BBTOOLS_READLEN, scratch_dir, output_dir, True)

    def run(self, input_file, output_file_name):
        """
        Runs readlength.sh on input_file to generate a file named output_file under the output_dir.
        It then skims that file for several values and returns them as a dictionary. The keys to this return dict are:
        count - the number of reads
        bases - the total number of bases
        max - the length of the longest read
        min - the length of the shortest read
        avg - the average read length
        median - the median read length
        mode - the mode of the mean lengths
        std_dev - the standard deviation of read lengths
        output_file - the output file from readlength, containing a histogram of reads info

        This also calculates the histogram, but it's left out for now. (Unless it's needed later)
        If the output file exists, it will be overwritten.
        """
        if not os.path.exists(input_file):
            raise ValueError("The input file '{}' can't be found!".format(input_file))
        mkdir(os.path.join(self.output_dir, "readlength"))
        output_file_path = os.path.join(self.output_dir, "readlength", output_file_name)
        readlength_params = [
            "in={}".format(input_file),
            "1>|",
            output_file_path
        ]

        (exit_code, command) = super(ReadLengthRunner, self).run(*readlength_params)
        if exit_code != 0:
            raise RuntimeError("An error occurred while running readlength!")
        if not os.path.exists(output_file_path):
            raise RuntimeError("The output file '{}' appears not to have been made!".format(output_file_path))
        ret_value = dict()
        # This file will have some standard lines, all of which start with a '#'
        # like this:
        #    #Reads:	358
        #    #Bases:	35279
        #    #Max:	100
        #    #Min:	89
        #    #Avg:	98.5
        #    #Median:	100
        #    #Mode:	100
        #    #Std_Dev:	4.9
        #    #Read Length Histogram: (a table follows that we're not using)
        # These get parsed based on their name. #Reads is an int, so parse it that way. #Avg is a float, etc.
        # The parsed numerical values get returned in the output dictionary.
        with open(output_file_path, "r") as read_len_file:
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
        ret_value.update({
            "output_file": output_file_path,
            "command": command,
            "version_string": self.version_string()
        })
        return ret_value
