from jgi_mg_assembly.utils.file import FileUtil
from BBTools.BBToolsClient import BBTools
from pprint import pprint


class Pipeline(object):
    def __init__(self, callback_url, scratch_dir):
        """
        Initialize a few things. Starting points, paths, etc.
        """
        self.callback_url = callback_url
        self.scratch_dir = scratch_dir
        self.file_util = FileUtil(callback_url)

    def run(self, params):
        """
        Run the pipeline!
        1. Validate parameters and param combinations.
        2. Run RQC filtering (might be external app or local method - see kbaseapps/BBTools repo)
        3. Run the Pipeline script as provided by JGI.
        """
        self._validate_params(params)

        # Fetch reads files
        files = self.file_util.fetch_reads_files([params["reads_upa"]])

        rqc_output = self._run_rqcfilter(files[params["reads_upa"]])
        pipeline_output = self._run_assembly_pipeline(rqc_output)
        stored_objects = self._upload_pipeline_result(pipeline_output)
        report_info = self._build_and_upload_report(rqc_output, pipeline_output, stored_objects)

        return {
            "report_name": report_info["name"],
            "report_ref": report_info["ref"],
            "assembly_upa": stored_objects["assembly_upa"]
        }

    def _validate_params(self, params):
        """
        Takes in params as passed to the main pipeline runner function and validates that
        all the pieces are there correctly.
        If anything tragic is missing, raises a ValueError with  a list of error strings.
        If not, just returns happily.
        """
        errors = []
        if "reads_upa" not in params:
            errors.append("Missing a Reads object!")
        if "output_assembly_name" not in params:
            errors.append("Missing the output assembly name!")

        if len(errors):
            for error in errors:
                print(error)
            raise ValueError("Errors found in app parameters! See above for details.")

    def _run_rqcfilter(self, reads_file):
        """
        Runs RQCFilter as a first pass.
        This just calls out to BBTools.run_RQCFilter_local and returns the result.
        result = dictionary with two keys -
            output_directory = path to the output directory
            filtered_fastq_file = as it says, gzipped
        """
        bbtools = BBTools(self.callback_url)
        result = bbtools.run_RQCFilter_local({
            'reads_file': reads_file
        })
        return result

    def _run_assembly_pipeline(self, rqc_output):
        """
        Takes in the output from RQCFilter (the output directory and reads file as a dict) and
        runs the remaining steps in the JGI assembly pipeline.
        steps:
        1. run bfc on output file from rqc filter with params -1 -s 10g -k 21 -t 10
        2. use seqtk to remove singleton reads
        3. run spades on that output with params -m 2000 --only-assembler -k 33,55,77,99,127 --meta -t 32
        4. run bbmap to map the reads onto the assembly with params ambiguous=random

        return the resulting file paths (just care about contigs file in v0, might use others for reporting)
        """
        return {
            "scaffolds": "some_file",
            "contigs": "some_file",
            "mapping": "some_file",
            "coverage": "some_file"
        }

    def _upload_pipeline_result(self, pipeline_result):
        return {
            "assembly_upa": "3/4/5"
        }

    def _build_and_upload_report(self, rqc_output, pipeline_output, saved_objects):
        return {
            "name": "MyNewReport",
            "ref": "9/8/7"
        }
