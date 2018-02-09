from jgi_mg_assembly.utils.file import (
    fetch_reads_files
)


class Pipeline(object):
    def __init__(self, callback_url, scratch_dir):
        """
        Initialize a few things. Starting points, paths, etc.
        """
        self.callback_url = callback_url
        self.scratch_dir = scratch_dir

    def run(self, params):
        """
        Run the pipeline!
        1. Validate parameters and param combinations.
        2. Run RQC filtering (might be external app or local method - see kbaseapps/BBTools repo)
        3. Run the Pipeline script as provided by JGI.
        """
        errors = self._validate_params(params)
        if errors is not None:
            for error in errors:
                print(error)
            raise ValueError("Errors found in app parameters! See above for details.")

        # Fetch reads files
        files = fetch_reads_files([params["reads_upa"]])

        rqc_output = self._run_rqc(files)
        pipeline_output = self._run_assembly_pipeline(rqc_output)
        report_info = self._build_and_upload_report(rqc_output, pipeline_output)

        return {
            "report_name": report_info["name"],
            "report_ref": report_info["ref"],
            "assembly_upa": pipeline_output["assembly_upa"]
        }

    def _validate_params(self, params):
        pass

    def _run_rqc(self, files):
        pass

    def _run_assembly_pipeline(rqc_output):
        pass

    def _build_and_upload_report(rqc_output, pipeline_output):
        pass
