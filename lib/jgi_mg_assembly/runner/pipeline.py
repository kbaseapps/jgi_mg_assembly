import subprocess
import time
import os
from BBTools.BBToolsClient import BBTools
from jgi_mg_assembly.utils.file import FileUtil
from jgi_mg_assembly.utils.report import ReportUtil
from jgi_mg_assembly.utils.util import mkdir


BFC = "/kb/module/bin/bfc"
SEQTK = "/kb/module/bin/seqtk"
SPADES = "/opt/SPAdes-3.11.1-Linux/bin/spades.py"
BBTOOLS_STATS = "/kb/module/bbmap/stats.sh"
BBMAP = "/kb/module/bbmap/bbmap.sh"
PIGZ = "pigz"
AGP_FILE_TOOL = "/kb/module/bbmap/fungalrelease.sh"


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

        # Fetch reads files
        files = self.file_util.fetch_reads_files([params["reads_upa"]])
        reads_files = list(files.values())
        pipeline_output = self._run_assembly_pipeline(reads_files[0])

        stored_objects = self._upload_pipeline_result(
            pipeline_output, params["workspace_name"], params["output_assembly_name"]
        )
        print("upload complete")
        print(stored_objects)
        report_info = self._build_and_upload_report(pipeline_output, stored_objects,
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
        If anything tragic is missing, raises a ValueError with  a list of error strings.
        If not, just returns happily.
        """
        errors = []
        if params.get("reads_upa", None) is None:
            errors.append("Missing a Reads object!")
        if params.get("output_assembly_name", None) is None:
            errors.append("Missing the output assembly name!")
        if params.get("workspace_name", None) is None:
            errors.append("Missing workspace name for the output data!")

        if len(errors):
            for error in errors:
                print(error)
            raise ValueError("Errors found in app parameters! See above for details.")

    def _run_assembly_pipeline(self, files):
        """
        Takes in the output from RQCFilter (the output directory and reads file as a dict) and
        runs the remaining steps in the JGI assembly pipeline.
        steps:
        0. run RQCfilter
        1. run bfc on output file from rqc filter with params
            -1 -s 10g -k 21 -t 10
        2. use seqtk to remove singleton reads
        3. run spades on that output with params
            -m 2000 --only-assembler -k 33,55,77,99,127 --meta -t 32
        4. run bbmap to map the reads onto the assembly with params ambiguous=random

        return the resulting file paths (just care about contigs file in v0, might use others for
        reporting)
        """
        rqc_output = self._run_rqcfilter(files)
        bfc_output = self._run_bfc_seqtk(rqc_output)
        spades_output = self._run_spades(bfc_output)
        agp_output = self._create_agp_file(spades_output)
        bbmap_output = self._run_bbmap(
            agp_output["scaffolds"],
            bfc_output,
            agp_output["contigs"]
        )

        return_dict = self._format_outputs(
            rqc_output, bfc_output, spades_output, agp_output, bbmap_output
        )
        return return_dict

    def _run_rqcfilter(self, reads_file):
        """
        Runs RQCFilter as a first pass.
        This just calls out to BBTools.run_RQCFilter_local and returns the result.
        result = dictionary with two keys -
            output_directory = path to the output directory
            filtered_fastq_file = as it says, gzipped
        """
        print("Running RQCFilter remotely using the KBase-wrapped BBTools module...")
        bbtools = BBTools(self.callback_url)
        result = bbtools.run_RQCFilter_local({
            "reads_file": reads_file
        })
        print("Done running RQCFilter")
        return result

    def _run_bfc_seqtk(self, input_file):
        """
        Takes in an input file, returns path to output file.
        """
        # command:
        # bfc <flag params> input_file["filtered_fastq_file"]
        mkdir(os.path.join(self.output_dir, "bfc"))
        bfc_output_file = os.path.join(self.output_dir, "bfc", "bfc_output.fastq")
        zipped_output = os.path.join(self.output_dir, "bfc", "input.corr.fastq.gz")
        bfc_cmd = [BFC, "-1", "-k", "21", "-t", "10"]

        on_hpc = False
        if on_hpc:  # we're somewhere that can handle it...
            bfc_cmd = bfc_cmd + ["-s", "10g"]
        bfc_cmd = bfc_cmd + [input_file["filtered_fastq_file"], ">", bfc_output_file]

        print("Running BFC with command:")
        print(" ".join(bfc_cmd))
        p = subprocess.Popen(" ".join(bfc_cmd), cwd=self.scratch_dir, shell=True)
        retcode = p.wait()
        if retcode != 0:
            raise RuntimeError("Error while running BFC!")
        print("Done running BFC")

        # next, pipe the output to seqtk and pigz
        seqtk_cmd = [SEQTK, "dropse", bfc_output_file, "|", PIGZ,
                     "-c", "-", "-p", "4", "-2", ">", zipped_output]
        p = subprocess.Popen(" ".join(seqtk_cmd), cwd=self.scratch_dir, shell=True)
        retcode = p.wait()
        if p.returncode != 0:
            raise RuntimeError("Error while running seqtk!")

        return zipped_output

    def _run_spades(self, input_file):
        """
        Runs spades, returns the generated output directory name. It's full of standard files.
        """
        spades_output_dir = os.path.join(self.output_dir, "spades3")
        mkdir(spades_output_dir)
        spades_cmd = [SPADES, "--only-assembler", "-k", "33,55,77,99,127", "--meta", "-t", "32",
                      "-m", "2000", "-o", spades_output_dir, "--12", input_file]

        print("Running SPAdes with command:")
        print(" ".join(spades_cmd))
        p = subprocess.Popen(spades_cmd, cwd=self.scratch_dir, shell=False)
        retcode = p.wait()
        if retcode != 0:
            raise RuntimeError("Error while running SPAdes!")
        print("Done running SPAdes")
        return spades_output_dir

    def _create_agp_file(self, spades_dir):
        """
        Runs bbmap/fungalrelease.sh to build AGP files and do some mapping and cleanup.
        Returns a dictionary where values are paths to files and keys are the following:
        scaffolds - mapped scaffolds fasta file
        contigs - mapped contigs fasta file
        agp - AGP file
        legend - legend for generated scaffolds
        """
        agp_dir = os.path.join(self.output_dir, "createAGPfile")
        mkdir(agp_dir)
        out_scaffolds = os.path.join(agp_dir, "assembly.scaffolds.fasta")
        out_contigs = os.path.join(agp_dir, "assembly.contigs.fasta")
        out_agp = os.path.join(agp_dir, "assembly.agp")
        out_legend = os.path.join(agp_dir, "assembly.scaffolds.legend")
        agp_file_cmd = [
            AGP_FILE_TOOL,
            "-Xmx40g",
            "in={}".format(os.path.join(spades_dir, "scaffolds.fasta")),
            "out={}".format(out_scaffolds),
            "outc={}".format(out_contigs),
            "agp={}".format(out_agp),
            "legend={}".format(out_legend),
            "mincontig=200",
            "minscaf=200",
            "sortscaffolds=t",
            "sortcontigs=t",
            "overwrite=t"
        ]
        print("Creating AGP file with command:")
        print(" ".join(agp_file_cmd))
        p = subprocess.Popen(agp_file_cmd, cwd=self.scratch_dir, shell=False)
        retcode = p.wait()
        if retcode != 0:
            raise RuntimeError("Error while creating AGP file!")
        print("Done creating AGP file")
        return {
            "scaffolds": out_scaffolds,
            "contigs": out_contigs,
            "agp": out_agp,
            "legend": out_legend
        }

    def _run_bbmap(self, scaffold_file, corrected_reads_file, contigs_file):
        """
        scaffold_file = FASTA file produced by SPAdes
        corrected_reads_file = original fastq file corrected by BFC
        contigs_file = assembled contigs from SPAdes
        """
        # 1. pre-step fungalrelease.sh (do we need this?)
        # (see createAGPfile in jgi-mga templates)
        #
        # 2. make assembly stats.
        bbmap_output_dir = os.path.join(self.output_dir, "readMappingPairs")
        mkdir(bbmap_output_dir)
        stats_output = os.path.join(bbmap_output_dir, "stats.tsv")
        sam_output = os.path.join(bbmap_output_dir, "pairedMapped.sam.gz")
        coverage_stats_output = os.path.join(bbmap_output_dir, "covstats.txt")
        stats_cmd = [BBTOOLS_STATS, "format=6", "in={}".format(scaffold_file), ">", stats_output]
        print("Running BBTools stats.sh with command:")
        print(" ".join(stats_cmd))
        p = subprocess.Popen(stats_cmd, cwd=self.scratch_dir, shell=False)
        retcode = p.wait()
        if retcode != 0:
            raise RuntimeError("Error while running BBTools stats.sh!")
        print("Done running BBTools stats.sh")

        # 3. do the mapping, make SAM file
        bbmap_cmd = [
            BBMAP,
            "nodisk=true",
            "interleaved=true",
            "ambiguous=random",
            "in={}".format(corrected_reads_file),
            "ref={}".format(contigs_file),
            "out={}".format(sam_output),
            "covstats={}".format(coverage_stats_output)
        ]
        print("Running BBMap with command:")
        print(" ".join(bbmap_cmd))
        p = subprocess.Popen(bbmap_cmd, cwd=self.scratch_dir, shell=False)
        retcode = p.wait()
        if retcode != 0:
            raise RuntimeError("Error while running BBMap!")
        print("Done running BBMap")
        return {
            "stats_file": stats_output,
            "map_file": sam_output,
            "coverage": coverage_stats_output
        }

    def _format_outputs(self, rqc_output, bfc_output, spades_output, agp_output, bbmap_output):
        """
        rqc_output = single file, qc / filtered reads
        bfc_output = single file, gzipped filtered reads
        spades_output = directory, with (needed files) contigs.fasta, scaffolds.fasta
        agp_output = dict with keys->files for keys scaffolds, contigs, agp, and legend
        bbmap_output = dict with objects stats_file, map_file (SAM), and coverage.

        This reformats all of those into a single dict. Might do some other cleanup later.
        """
        return {
            "scaffolds": agp_output["scaffolds"],  # os.path.join(spades_output, "scaffolds.fasta"),
            "contigs": agp_output["contigs"],  # os.path.join(spades_output, "contigs.fasta"),
            "mapping": bbmap_output["map_file"],
            "coverage": bbmap_output["coverage"],
            "stats": bbmap_output["stats_file"]
        }

    def _upload_pipeline_result(self, pipeline_result, workspace_name, assembly_name):
        uploaded_upa = self.file_util.upload_assembly(
            pipeline_result["contigs"], workspace_name, assembly_name
        )
        return {
            "assembly_upa": uploaded_upa
        }

    def _build_and_upload_report(self, pipeline_output, output_objects, workspace_name):
        report_util = ReportUtil(self.callback_url, self.output_dir)
        stored_objects = list()
        stored_objects.append({
            "ref": output_objects["assembly_upa"],
            "description": "Assembled with the JGI metagenome pipeline."
        })
        return report_util.make_report(pipeline_output["stats"], pipeline_output["coverage"],
                                       workspace_name, stored_objects)
