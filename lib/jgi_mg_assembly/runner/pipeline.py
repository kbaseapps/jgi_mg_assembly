import subprocess
import time
import os
from BBTools.BBToolsClient import BBTools
from jgi_mg_assembly.utils.file import FileUtil
from jgi_mg_assembly.utils.report import ReportUtil
from jgi_mg_assembly.utils.util import mkdir
from jgi_mg_assembly.pipeline_steps.readlength import readlength
from jgi_mg_assembly.pipeline_steps.rqcfilter import RQCFilterRunner
from jgi_mg_assembly.pipeline_steps.bfc import BFCRunner
from jgi_mg_assembly.pipeline_steps.seqtk import SeqtkRunner
from jgi_mg_assembly.pipeline_steps.spades import SpadesRunner
from jgi_mg_assembly.pipeline_steps.agp import AgpRunner
from jgi_mg_assembly.pipeline_steps.assemblystats import StatsRunner
from jgi_mg_assembly.pipeline_steps.bbmap import BBMapRunner

PIGZ = "pigz"


class Pipeline(object):

    def __init__(self, callback_url, scratch_dir):
        """
        Initialize a few things. Starting points, paths, etc.
        """
        self.callback_url = callback_url
        self.scratch_dir = scratch_dir
        self.timestamp = int(time.time() * 1000)
        self.output_dir = os.path.join(self.scratch_dir, "jgi_mga_output_{}".format(self.timestamp))
        mkdir(self.output_dir)
        self.file_util = FileUtil(callback_url)

    def run(self, params):
        """
        Run the pipeline!
        1. Validate parameters and param combinations.
        2. Run RQC filtering (might be external app or local method - see kbaseapps/BBTools repo)
        3. Run the Pipeline script as provided by JGI.
        """
        self._validate_params(params)
        options = {
            "skip_rqcfilter": True if params.get("skip_rqcfilter") else False,
            "debug": True if params.get("debug") else False
        }

        # Fetch reads files
        files = self.file_util.fetch_reads_files([params["reads_upa"]])
        reads_files = list(files.values())
        pipeline_output = self._run_assembly_pipeline(reads_files[0], options)

        stored_objects = self._upload_pipeline_result(
            pipeline_output, params["workspace_name"], params["output_assembly_name"]
        )
        print("upload complete")
        print(stored_objects)
        report_info = self._build_and_upload_report(pipeline_output,
                                                    stored_objects,
                                                    params["workspace_name"])
        return {
            "report_name": report_info["report_name"],
            "report_ref": report_info["report_ref"],
            "assembly_upa": stored_objects["assembly_upa"]
        }

    def _validate_params(self, params):
        """
        Takes in params as passed to the main pipeline runner function and validates that
        all the pieces are there correctly.
        If anything tragic is missing, raises a ValueError with a list of error strings.
        If not, just returns happily.
        """
        errors = []
        if params.get("reads_upa") is None:
            errors.append("Missing a Reads object!")
        if params.get("output_assembly_name") is None:
            errors.append("Missing the output assembly name!")
        if params.get("workspace_name") is None:
            errors.append("Missing workspace name for the output data!")

        if len(errors):
            for error in errors:
                print(error)
            raise ValueError("Errors found in app parameters! See above for details.")

    def _run_assembly_pipeline(self, files, options):
        """
        Runs the complete JGI assembly pipeline and returns all the outputs from each step.
        1. Get initial reads info.
        2. RQCFilter.
        3. Get filtered reads info.
        4. BFC
        5. SeqTK
        6. Get corrected reads info.
        7. SPAdes
        8. AGP file / etc. with fungalrelease.sh
        9. Assembly stats.
        10. BBMap.
        11. Return structure with resulting files and objects.
        """
        # get reads info on the base input.
        reads_info_initial = readlength(files,
                                        os.path.join(self.output_dir, "pre_filter_readlen.txt"))

        # run RQCFilter
        # keys: output_directory, filtered_fastq_file, run_log
        rqcfilter = RQCFilterRunner(self.callback_url, self.scratch_dir, options)
        rqc_output = rqcfilter.run(files)

        # get info on the filtered reads
        reads_info_filtered = readlength(rqc_output["filtered_fastq_file"],
                                         os.path.join(self.output_dir, "filtered_readlen.txt"))

        # run BFC on the filtered reads
        # keys: corrected_reads, command
        bfc = BFCRunner(self.scratch_dir, self.output_dir)
        bfc_output = bfc.run(rqc_output["filtered_fastq_file"], debug=options.get("debug"))

        # run SeqTK on the corrected reads to remove the stray single ended ones
        # keys: cleaned_reads (note that they're zipped!), command
        seqtk = SeqtkRunner(self.scratch_dir, self.output_dir)
        seqtk_output = seqtk.run(bfc_output["corrected_reads"])

        # get info on the filtered/corrected reads
        reads_info_corrected = readlength(seqtk_output["cleaned_reads"],
                                          os.path.join(self.output_dir, "corrected_readlen.txt"))

        # assemble the filtered/corrected reads with spades
        # keys:
        # * output_dir
        # * command
        # * run_log
        # * params_log
        # * warnings_log -- if exists
        # * scaffolds_file -- if exists
        # * contigs_file -- if exists
        spades = SpadesRunner(self.scratch_dir, self.output_dir)
        spades_output = spades.run(seqtk_output["cleaned_reads"], reads_info_corrected, {})

        # Polish the scaffolds and get an agp file (and legend)
        # keys: scaffolds, contigs, agp, legend (all file paths)
        agp = AgpRunner(self.scratch_dir, self.output_dir)
        agp_output = agp.run(spades_output.get("scaffolds_file"))

        # Use BBMap to build up the assembly stats
        # keys: stats_tsv, stats_txt, stats_err
        stats_runner = StatsRunner(self.scratch_dir, self.output_dir)
        stats_output = stats_runner.run(agp_output["scaffolds_file"])

        # Map the filtered (not corrected / cleaned) reads to the assembled contigs with BBMap
        # keys: map_file, coverage_file, stats_file
        bbmap_runner = BBMapRunner(self.scratch_dir, self.output_dir)
        bbmap_output = bbmap_runner.run(rqc_output["filtered_fastq_file"], spades_output["contigs_file"])

        return_dict = {
            "reads_info": {
                "pre_filter": reads_info_initial,
                "filtered": reads_info_filtered,
                "corrected": reads_info_corrected
            },
            "rqcfilter": rqc_output,
            "bfc": bfc_output,
            "spades": spades_output,
            "agp": agp_output,
            "stats": stats_output,
            "bbmap": bbmap_output
        }
        return return_dict

    def _upload_pipeline_result(self, pipeline_result, workspace_name, assembly_name):
        """
        Uploads the new Assembly object to the user's workspace.
        pipeline_result - dict, needs to see
        * contigs - the generated contigs file at the end of the pipeline run.
        workspace_name - the name of the workspace to upload to
        assembly_name - the name of the new assembly object.

        returns a dict with key "assembly_upa" - the created UPA for the Assembly object.
        """
        uploaded_upa = self.file_util.upload_assembly(
            pipeline_result["contigs"], workspace_name, assembly_name
        )
        return {
            "assembly_upa": uploaded_upa
        }

    def _build_and_upload_report(self, pipeline_output, output_objects, workspace_name):
        """
        Builds and uploads a report. This contains both an HTML report for display as well
        as a list of report files with various outputs from the pipeline.

        pipeline_output - dict, expects the following keys:
        * bbmap_stats - the bbmap stats file
        * bbmap_coverage - the covstats.txt file
        * assembly_stats - the AGP assembly stats file
        * assembly_tsv - the AGP assembly stats tsv file (different contents)
        * rqcfilter_log - the output log from rqcfilter
        * reads_info - a dictionary containing info about the reads at each step (initial, filtered, and corrected)
        *   - should have keys: pre_filter, filtered, corrected,
        *   - contents are the results of readlength() for each case

        output_objects - dict, expects to see
        * assembly_upa - the UPA for the new assembly object

        workspace_name - string, the name of the workspace to upload the report to
        """
        report_util = ReportUtil(self.callback_url, self.output_dir)
        stored_objects = list()
        stored_objects.append({
            "ref": output_objects["assembly_upa"],
            "description": "Assembled with the JGI metagenome pipeline."
        })

        stats_files = {
            "bbmap_stats": pipeline_output["bbmap_stats"],
            "covstats": pipeline_output["bbmap_coverage"],
            "assembly_stats": pipeline_output["assembly_stats"],
            "assembly_tsv": pipeline_output["assembly_tsv"],
            "rqcfilter_log": pipeline_output["rqcfilter_log"]
        }
        for f in ["spades_log", "spades_warnings", "spades_params"]:
            if f in pipeline_output:
                stats_files[f] = pipeline_output[f]
        for f in ["pre_filter", "filtered", "corrected"]:
            if f in pipeline_output["reads_info"]:
                stats_files[f + "_reads"] = pipeline_output["reads_info"][f]["output_file"]
        return report_util.make_report(stats_files, pipeline_output["reads_info"],
                                       workspace_name, stored_objects)
