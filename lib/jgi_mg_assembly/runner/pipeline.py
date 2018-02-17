from jgi_mg_assembly.utils.file import FileUtil
from BBTools.BBToolsClient import BBTools
from pprint import pprint
import subprocess
import uuid
import os

BFC = "bin/bfc"
SEQTK = "bin/seqtk"
SPADES = "/opt/SPAdes-3.11.1-Linux/bin/spades.py"
BBTOOLS_STATS = "bbmap/stats.sh"
BBMAP = "bbmap/bbmap.sh"


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
        pipeline_output = self._run_assembly_pipeline(files)

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
        bbmap_output = self._run_bbmap(spades_output)

        return_dict = self._format_outputs(rqc_output, bfc_output, spades_output, bbmap_output)
        return return_dict

    def _run_bfc_seqtk(self, input_file):
        """
        Takes in an input file, returns path to output file.
        """
        # command:
        # bfc <flag params> input_file['filtered_fastq_file']
        bfc_output_file = os.path.join(self.scratch_dir, 'bfc_output.fastq')
        zipped_output = os.path.join(self.scratch_dir, 'input.corr.fastq.gz')
        bfc_cmd = [BFC, '-1', '-k 21']
        if True:  # we're somewhere that can handle it...
            bfc_cmd.append('-t 10 -s 10g')
        bfc_cmd = bfc_cmd + [input_file['filtered_fastq_file'], '>', bfc_output_file]

        p = subprocess.Popen(bfc_cmd, cwd=self.scratch_dir, shell=False)
        retcode = p.wait()
        if retcode != 0:
            raise RuntimeError('Error while running BFC!')

        # # next, pipe the output to seqtk and gzip
        # seqtk_cmd = [SEQTK, 'dropse', bfc_output_file, '|', PIGZ, '-c', '-', '-p', '4', '-2' '>' zipped_output]
        # p = subprocess.Popen(seqtk_cmd, cwd=self.scratch_dir, shell=False)
        # retcode = p.wait()
        # if p.returncode != 0:
        #     raise RuntimeError('Error while running seqtk!')
        #
        return zipped_output

    def _run_spades(self, input_file):
        spades_output_dir = os.path.join(self.scratch_dir, 'spades_output_{}'.format(uuid.uuid4()))
        spades_cmd = [SPADES, '--only-assembler', '-k', '33,55,77,99,127', '--meta', '-t', '32',
                      '-m', '2000', '-o', spades_output_dir, '--12', input_file]
        p = subprocess.Popen(spades_cmd, cwd=self.scratch_dir, shell=False)
        retcode = p.wait()
        if retcode != 0:
            raise RuntimeError('Error while running SPAdes!')
        return spades_output_dir

    def _run_bbmap(self, scaffold_file, corrected_reads_file, contigs_file):
        # 1. pre-step fungalrelease.sh (do we need this?)
        # (see createAGPfile in jgi-mga templates)
        #
        # 2. make assembly stats.
        stats_output = os.path.join(self.scratch_dir, 'stats.tsv')
        sam_output = os.path.join(self.scratch_dir, 'pairedMapped.sam.gz')
        coverage_stats_output = os.path.join(self.scratch_dir, 'covstats.txt')
        stats_cmd = [BBTOOLS_STATS, 'format=6', 'in={}'.format(scaffold_file), '>', stats_output]
        p = subprocess.Popen(stats_cmd, cwd=self.scratch_dir, shell=False)
        retcode = p.wait()
        if retcode != 0:
            raise RuntimeError('Error while running BBTools stats.sh!')

        # 3. do the mapping, make SAM file
        bbmap_cmd = [
            BBMAP,
            'nodisk=true',
            'interleaved=true',
            'ambiguous=random',
            'in={}'.format(corrected_reads_file),
            'ref={}'.format(contigs_file),
            'out={}'.format(sam_output),
            'covstats={}'.format(coverage_stats_output)
        ]
        p = subprocess.Popen(bbmap_cmd, cwd=self.scratch_dir, shell=False)
        retcode = p.wait()
        if retcode != 0:
            raise RuntimeError('Error while running BBMap!')
        return {
            'stats_file': stats_output,
            'map_file': sam_output,
            'coverage': coverage_stats_output
        }

    def _format_outputs(self, rqc_output, bfc_output, spades_output, bbmap_output):
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
