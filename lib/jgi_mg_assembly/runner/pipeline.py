from jgi_mg_assembly.utils.file import FileUtil


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

        rqc_output = self._run_rqc(files)
        pipeline_output = self._run_assembly_pipeline(rqc_output)
        report_info = self._build_and_upload_report(rqc_output, pipeline_output)

        return {
            "report_name": report_info["name"],
            "report_ref": report_info["ref"],
            "assembly_upa": pipeline_output["assembly_upa"]
        }

    def _validate_params(self, params):
        """
        Takes in params as passed to the main pipeline runner function and validates that
        all the pieces are there correctly.
        If anything tragic is missing, returns a list of error strings. If not, returns None.
        """
        errors = []

        if len(errors):
            for error in errors:
                print(error)
            raise ValueError("Errors found in app parameters! See above for details.")


    def _run_rqc(self, files):
        pass

    def _run_assembly_pipeline(rqc_output):
        pass

    def _build_and_upload_report(rqc_output, pipeline_output):
        pass
