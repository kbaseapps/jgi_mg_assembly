import time
import os
import subprocess
from jgi_mg_assembly.utils.report import ReportUtil
from jgi_mg_assembly.utils.util import mkdir
from jgi_mg_assembly.utils.file import FileUtil
from jgi_mg_assembly.pipeline_steps.readlength import ReadLengthRunner
from jgi_mg_assembly.pipeline_steps.rqcfilter import RQCFilterRunner
from jgi_mg_assembly.pipeline_steps.bfc import BFCRunner
from jgi_mg_assembly.pipeline_steps.seqtk import SeqtkRunner
from jgi_mg_assembly.pipeline_steps.spades import SpadesRunner
from jgi_mg_assembly.pipeline_steps.agp import AgpRunner
from jgi_mg_assembly.pipeline_steps.assemblystats import StatsRunner
from jgi_mg_assembly.pipeline_steps.bbmap import BBMapRunner
from BBTools.BBToolsClient import BBTools

PIGZ = "pigz"
MAX_MEMORY = 1500        # GB memory
MAX_READS_SIZE = 200     # GB disk

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
            "skip_rqcfilter": bool(params.get("skip_rqcfilter")),
            "debug": bool(params.get("debug"))
        }

        # Fetch reads files
        files = self.file_util.fetch_reads_files([params["reads_upa"]])
        reads_files = list(files.values())

        # run the pipeline.
        pipeline_output = self._run_assembly_pipeline(reads_files[0], options)

        upload_kwargs = {
            "cleaned_reads_name": params.get("cleaned_reads_name"),
            "filtered_reads_name": params.get("filtered_reads_name"),
            "skip_rqcfilter": params.get("skip_rqcfilter"),
            "input_reads": params.get("reads_upa")
        }

        stored_objects = self._upload_pipeline_result(
            pipeline_output,
            params["workspace_name"],
            params["output_assembly_name"],
            **upload_kwargs
        )
        print("upload complete")
        print(stored_objects)
        report_info = self._build_and_upload_report(pipeline_output,
                                                    stored_objects,
                                                    params["workspace_name"])
        return_objects = {
            "report_name": report_info["report_name"],
            "report_ref": report_info["report_ref"]
        }
        return_objects.update(stored_objects)
        return return_objects

    def _check_memory_use(self, reads_file):
        bbtools = BBTools(self.callback_url, service_ver="beta")
        mem_estimate = bbtools.run_mem_estimator({
            "reads_file": reads_file
        })
        errors = list()
        if mem_estimate["estimate"] > MAX_MEMORY:
            errors.append("Your reads are estimated to require {} GB "
                "of memory to assemble, which is over the limit of {} "
                "GB available.".format(round(mem_estimate["estimate"], 2), MAX_MEMORY))
        if mem_estimate["size"] > MAX_READS_SIZE:
            errors.append("This size of your reads is approximately {} GB, which exceeds the "
                "maximum of {} GB.".format(round(mem_estimate["size"], 2), MAX_READS_SIZE))
        if len(errors) > 0:
            raise RuntimeError("Unable to run the Metagenome Assembly "
                "Pipeline on your reads: {}".format("\n".join(errors)))

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
        if params.get("skip_rqcfilter") and params.get("filtered_reads_name"):
            errors.append("Filtered reads are not created when skipping the RQCFilter step, so do not set filtered_reads_name (Filtered Reads Output).")
        if len(errors):
            for error in errors:
                print(error)
            raise ValueError("; ".join(errors))

    def _run_assembly_pipeline(self, files, options):
        """
        :param files: (currently) a single paired-end file for input to the pipeline.
        :param options: a dict, with possible keys:
            debug - boolean, generally set to True when tests are running.
            skip_rqcfilter - boolean, if True, will not run RQCFilter.

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
        readlength = ReadLengthRunner(self.scratch_dir, self.output_dir)
        # get reads info on the base input.
        reads_info_initial = readlength.run(files, "pre_filter_readlen.txt")

        # run RQCFilter
        # keys: output_directory, filtered_fastq_file, run_log
        rqcfilter = RQCFilterRunner(self.callback_url, self.scratch_dir, self.output_dir, options)
        rqc_output = rqcfilter.run(files)

        # get info on the filtered reads
        reads_info_filtered = readlength.run(rqc_output["filtered_fastq_file"], "filtered_readlen.txt")

        # run BFC on the filtered reads
        # keys: corrected_reads, command
        bfc = BFCRunner(self.scratch_dir, self.output_dir)
        bfc_output = bfc.run(rqc_output["filtered_fastq_file"], debug=options.get("debug"))

        # run SeqTK on the corrected reads to remove the stray single ended ones
        # keys: cleaned_reads (note that they're zipped!), command
        seqtk = SeqtkRunner(self.scratch_dir, self.output_dir)
        seqtk_output = seqtk.run(bfc_output["corrected_reads"])

        # Check that RAM requirements for metaSpades.py won't be exceded.
        # We need to count unique kmers of filtered reads
        self._check_memory_use(seqtk_output["cleaned_reads"])

        # get info on the filtered/corrected reads
        reads_info_corrected = readlength.run(seqtk_output["cleaned_reads"], "corrected_readlen.txt")

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
        spades_output = spades.run(
            seqtk_output["cleaned_reads"],
            reads_info_corrected,
            {"max_memory": MAX_MEMORY}
        )

        # Polish the scaffolds and get an agp file (and legend)
        # keys: scaffolds, contigs, agp, legend (all file paths)
        agp = AgpRunner(self.scratch_dir, self.output_dir)
        agp_output = agp.run(spades_output.get("scaffolds_file"), spades_output.get("contigs_file"))

        # Use BBMap to build up the assembly stats
        # keys: stats_tsv, stats_txt, stats_err
        stats_runner = StatsRunner(self.scratch_dir, self.output_dir)
        stats_output = stats_runner.run(agp_output["scaffolds_file"])

        # Map the filtered (not corrected / cleaned) reads to the assembled contigs with BBMap
        # keys: map_file, coverage_file, stats_file
        bbmap_runner = BBMapRunner(self.scratch_dir, self.output_dir)
        bbmap_output = bbmap_runner.run(rqc_output["filtered_fastq_file"], spades_output["contigs_file"])

        return_dict = {
            "reads_info_prefiltered": reads_info_initial,
            "reads_info_filtered": reads_info_filtered,
            "reads_info_corrected": reads_info_corrected,
            "rqcfilter": rqc_output,
            "bfc": bfc_output,
            "seqtk": seqtk_output,
            "spades": spades_output,
            "agp": agp_output,
            "stats": stats_output,
            "bbmap": bbmap_output
        }
        return return_dict

    def _upload_pipeline_result(self, pipeline_result, workspace_name, assembly_name,
                                filtered_reads_name=None,
                                cleaned_reads_name=None,
                                skip_rqcfilter=False,
                                input_reads=None):
        """
        This is very tricky and uploads (optionally!) a few things under different cases.
        1. Uploads assembly
            - this always happens after a successful run.
        2. Cleaned reads - passed RQCFilter / BFC / SeqTK
            - optional, if cleaned_reads_name isn't None
        3. Filtered reads - passed RQCFilter
            - optional, if filtered_reads_name isn't None AND skip_rqcfilter is False
        returns a dict of UPAs with the following keys:
        - assembly_upa - the assembly (always)
        - filtered_reads_upa - the RQCFiltered reads (optionally)
        - cleaned_reads_upa - the RQCFiltered -> BFC -> SeqTK cleaned reads (optional)
        """

        # upload the assembly
        uploaded_assy_upa = self.file_util.upload_assembly(
            pipeline_result["spades"]["contigs_file"], workspace_name, assembly_name
        )
        upload_result = {
            "assembly_upa": uploaded_assy_upa
        }
        # upload filtered reads if we didn't skip RQCFilter (otherwise it's just a copy)
        if filtered_reads_name and not skip_rqcfilter:
            # unzip the cleaned reads because ReadsUtils won't do it for us.
            decompressed_reads = os.path.join(self.output_dir, "filtered_reads.fastq")
            pigz_command = "{} -d -c {} > {}".format(PIGZ, pipeline_result["rqcfilter"]["filtered_fastq_file"], decompressed_reads)
            p = subprocess.Popen(pigz_command, cwd=self.scratch_dir, shell=True)
            exit_code = p.wait()
            if exit_code != 0:
                raise RuntimeError("Unable to decompress filtered reads for validation! Can't upload them, either!")
            filtered_reads_upa = self.file_util.upload_reads(
                decompressed_reads, workspace_name, filtered_reads_name, input_reads
            )
            upload_result["filtered_reads_upa"] = filtered_reads_upa
        # upload the cleaned reads
        if cleaned_reads_name:
            # unzip the cleaned reads because ReadsUtils won't do it for us.
            decompressed_reads = os.path.join(self.output_dir, "cleaned_reads.fastq")
            pigz_command = "{} -d -c {} > {}".format(PIGZ, pipeline_result["seqtk"]["cleaned_reads"], decompressed_reads)
            p = subprocess.Popen(pigz_command, cwd=self.scratch_dir, shell=True)
            exit_code = p.wait()
            if exit_code != 0:
                raise RuntimeError("Unable to decompress cleaned reads for validation! Can't upload them, either!")
            cleaned_reads_upa = self.file_util.upload_reads(
                decompressed_reads, workspace_name, cleaned_reads_name, input_reads
            )
            upload_result["cleaned_reads_upa"] = cleaned_reads_upa
        return upload_result

    def _build_and_upload_report(self, pipeline_output, output_objects, workspace_name):
        """
        Builds and uploads a report. This contains both an HTML report for display as well
        as a list of report files with various outputs from the pipeline.

        pipeline_output - dict, expects the following keys, from each of the different steps
        * reads_info_prefiltered
        * reads_info_filtered
        * reads_info_corrected
        * rqcfilter
        * bfc
        * seqtk
        * spades
        * agp
        * stats
        * bbmap

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
        if "cleaned_reads_upa" in output_objects:
            stored_objects.append({
                "ref": output_objects["cleaned_reads_upa"],
                "description": "Reads processed by the JGI metagenome pipeline before assembly."
            })
        if "filtered_reads_upa" in output_objects:
            stored_objects.append({
                "ref": output_objects["filtered_reads_upa"],
                "description": "Reads filtered by RQCFilter, and used to align against the assembled contigs."
            })

        return report_util.make_report(pipeline_output, workspace_name, stored_objects)
