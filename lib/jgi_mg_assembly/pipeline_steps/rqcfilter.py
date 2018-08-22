import os
import json
from time import time
from BBTools.BBToolsClient import BBTools
from DataFileUtil.DataFileUtilClient import DataFileUtil
from jgi_mg_assembly.utils.util import mkdir
from step import Step

class RQCFilterRunner(Step):
    """
    Acts as a runner for RQCFilter.
    This has two functions.
    run: does the job of invoking BBTools to run RQCFilter. This calls out to the
         KBase BBTools module and runs the app there, returning the results (see
         the run docstring for details).
    run_skip: does a "fake" run of RQCFilter. This returns the same result structure
              but does not run RQCFilter. Instead, it just compresses the given
              reads file (as the results of RQCFilter are done) and creates an
              empty log file.
              This way if the user (or a testing developer) wants to skip that step,
              the rest of the pipeline doesn't fork.
    """

    def __init__(self, callback_url, scratch_dir, output_dir, options):
        super(RQCFilterRunner, self).__init__("RQCFilter", "BBTools", None, scratch_dir, output_dir, False)
        self.callback_url = callback_url
        self.skip = options.get("skip_rqcfilter")
        self.debug = options.get("debug")

    def get_parameters(self):
        return {
            "rna": 0,
            "trimfragadapter": 1,
            "qtrim": "r",
            "trimq": 0,
            "maxns": 3,
            "minavgquality": 3,
            "minlength": 51,
            "mlf": 0.333,
            "phix": 1,
            "removehuman": 1,
            "removedog": 1,
            "removecat": 1,
            "removemouse": 1,
            "khist": 1,
            "removemicrobes": 1,
            "clumpify": 1
        }

    def run(self, reads_file):
        """
        Runs RQCFilter.
        This just calls out to BBTools.run_RQCFilter_local and returns the result.
        reads_file: string, the path to the FASTQ file to be filtered.
        result = dictionary with three keys -
            output_directory = path to the output directory
            filtered_fastq_file = as it says, gzipped
            run_log = path to the stderr log from RQCFilter
        """
        if (self.skip):
            return self.run_skip(reads_file)

        print("Running RQCFilter remotely using the KBase-wrapped BBTools module...")
        bbtools = BBTools(self.callback_url, service_ver='beta')
        result = bbtools.run_RQCFilter_local({ "reads_file": reads_file }, self.get_parameters())
        print("Done running RQCFilter")
        result.update({
            "command": "BBTools.run_RQCFilter_local {}".format(json.dumps(self.get_parameters())),
            "version_string": "KBase BBTools module"
        })
        return result

    def run_skip(self, reads_file):
        """
        Doesn't run RQCFilter, but a dummy skip version. It returns the same
        result structure, so it doesn't derail the other pipeline steps. However, the
        "filtered_fastq_file" is the unchanged fastq file, other than gzipping it.
        run_log is just an empty (but existing!) file.
        """
        print("NOT running RQCFilter, just dummying up some results.")
        # make the dummy output dir
        outdir = os.path.join(self.scratch_dir, "dummy_rqcfilter_output_{}".format(int(time() * 1000)))
        mkdir(outdir)
        # mock up a log file
        dummy_log = os.path.join(outdir, "dummy_rqcfilter_log.txt")
        open(dummy_log, 'w').close()
        # just compress the reads and move them into that output dir (probably don't need to
        # move them, but let's be consistent)
        dfu = DataFileUtil(self.callback_url)
        compressed_reads = dfu.pack_file({
            "file_path": reads_file,
            "pack": "gzip"
        })["file_path"]
        base_name = os.path.basename(compressed_reads)
        not_filtered_reads = os.path.join(outdir, base_name)
        os.rename(compressed_reads, not_filtered_reads)
        return {
            "output_directory": outdir,
            "filtered_fastq_file": not_filtered_reads,
            "run_log": dummy_log,
            "command": "BBTools.run_RQCFilter_local -- skipped. No command run.",
            "version_string": "KBase BBTools module"
        }
