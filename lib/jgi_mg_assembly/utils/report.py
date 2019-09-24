"""
Used for making and uploading a KBaseReport for the MG assembly pipeline results.
"""
import os
import uuid
import shutil
import zipfile
import subprocess
import re
import json
from pprint import pprint
from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.KBaseReportClient import KBaseReport
from .util import mkdir
from .graphics import generate_graphics

class ReportUtil(object):
    def __init__(self, callback_url, output_dir):
        self.callback_url = callback_url
        self.output_dir = output_dir

    def make_report(self, pipeline_output, workspace_name, saved_objects):
        """
        Uses the pipeline output structure to produce an HTML report containing most of
        the relevant information. It also assembles many of the various output files into a
        report object that can tbe downloaded by the user. Expects to see (at a minimum)
        the following structure for the pipeline_output. ? = optional file

        "reads_info_prefiltered": {
            "output_file": file,
            "command": string,
            "version_string": string,
            "count": int,
            bases": int,
            "max": int,
            "min": int,
            "avg": float,
            "median": int,
            "mode": int,
            "std_dev": float,
        },
        "reads_info_filtered": as above,
        "reads_info_corrected": one more time,
        "rqcfilter": {
            "output_directory": file path,
            "filtered_fastq_file": file,
            "run_log": file
        },
        "bfc": {
            "command": string,
            "corrected_reads": file
            "version_string": string
        },
        "seqtk": {
            "command": string,
            "cleaned_reads": file,
            "version_string": string
        },
        "spades": {
            "command": string,
            "version_string": string,
            "output_dir": file,
            "run_log": file,
            "params_log": file,
            "warnings_log": file?,
            "contigs_file": file?,
            "scaffolds_file": file?
        },
        "agp": {
            "scaffolds_file": file,
            "contigs_file": file,
            "agp_file": file,
            "legend_file": file,
            "command": string,
            "version_string": string
        },
        "stats": {
            "stats_tsv": file,
            "stats_txt": file,
            "stats_err": file,
            "version_string": string,
            "command": string
        },
        "bbmap": {
            "map_file": file (bam file),
            "coverage_file": file,
            "stats_file": file,
            "command": string,
            "version_string": string
        }

        saved_objects should be in the correct format for KBaseReports. So, a list of dicts:
        {
            "ref": upa,
            "description": some string
        }

        After assembling the report, it uses the KBaseReports module to upload, and returns a dict
        with "report_ref" and "report_name" keys.
        """
        # We're gonna assume that all files exist. The only ones that are maybes are from spades.
        assert pipeline_output, "Pipeline output not found!"
        assert workspace_name, "A workspace name is required!"

        required_counts = ["reads_info_prefiltered", "reads_info_filtered", "reads_info_corrected"]
        for req in required_counts:
            assert req in pipeline_output, "Required reads info '{}' is not present!".format(req)
        if not saved_objects:
            saved_objects = list()

        pipeline_output["report_graphics"] = generate_graphics(pipeline_output["bbmap"]["coverage_file"], self.output_dir)

        # Make the html report
        html_report_dir = os.path.join(self.output_dir, "report")
        mkdir(html_report_dir)
        html_file_name = os.path.join(html_report_dir, "index.html")
        self._write_html_file(html_file_name, pipeline_output)

        # Write the command info file
        pipeline_info_file = os.path.join(html_report_dir, "pipeline_info.json")
        self._write_pipeline_info_file(pipeline_output, pipeline_info_file)

        result_file = os.path.join(self.output_dir, "assembly_report.zip")
        report_files = {
            "reads_info_prefiltered": ["output_file"],
            "reads_info_filtered": ["output_file"],
            "reads_info_corrected": ["output_file"],
            "rqcfilter": ["run_log"],
            "spades": ["run_log", "params_log", "warnings_log"],
            "stats": ["stats_tsv", "stats_txt", "stats_err"],
            "bbmap": ["coverage_file", "stats_file"],
            "report_graphics": pipeline_output["report_graphics"].keys()
        }
        with zipfile.ZipFile(result_file, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as report_zip:
            # add reads info report
            for step, file_list in report_files.items():
                for f in file_list:
                    if f in pipeline_output[step] and os.path.exists(pipeline_output[step][f]):
                        zip_path = os.path.join(step, os.path.basename(pipeline_output[step][f]))
                        report_zip.write(pipeline_output[step][f], zip_path)
            report_zip.write(pipeline_info_file, "pipeline_info.json")
            report_zip.write(html_file_name, "report.html")

        file_links = [{
            'path': result_file,
            'name': os.path.basename(result_file),
            'label': 'assembly_report',
            'description': 'JGI Metagenome Assembly Report'
        }]
        return self._upload_report(html_report_dir, file_links, workspace_name, saved_objects)

    def _write_pipeline_info_file(self, pipeline_output, info_file):
        pipeline_steps = []
        for step in ["reads_info_prefiltered", "rqcfilter", "reads_info_filtered", "bfc", "seqtk", "reads_info_corrected", "spades", "agp", "stats", "bbmap"]:
            pipeline_steps.append({
                "step": step,
                "command": pipeline_output[step]["command"],
                "version": pipeline_output[step]["version_string"]
            })
        with open(info_file, "w") as f:
            f.write(json.dumps(pipeline_steps, indent=4))

    def _write_html_file(self, html_file_name, pipeline_output):
        """
        Assembles and writes out an HTML report file, following the idoms developed by JGI.
        Right now, this just cobbles together text into a single <pre> formatted HTML file.
        """
        header = "Assembly using the JGI metagenome assembly pipeline, interpreted by KBase\n\n"

        filter_percent = self._percent_reads(pipeline_output["reads_info_filtered"]["count"], pipeline_output["reads_info_prefiltered"]["count"])
        corrected_percent = self._percent_reads(pipeline_output["reads_info_corrected"]["count"],
                                                pipeline_output["reads_info_prefiltered"]["count"])
        read_processing = (
            "Read Pre-processing\n"
            "The number of raw input reads is: {}\n"
            "The number of reads remaining after quality filter: {} ({}% of raw)\n"
            "The final number of reads remaining "
            "after read correction: {} ({}% of raw)\n\n"
        ).format(pipeline_output["reads_info_prefiltered"]["count"],
                 pipeline_output["reads_info_filtered"]["count"],
                 filter_percent,
                 pipeline_output["reads_info_corrected"]["count"],
                 corrected_percent)

        with open(pipeline_output["stats"]["stats_txt"], "r") as stats:
            assembly_stats_file = "".join(stats.readlines())
        assembly_stats = "Assembly stats:\n{}".format(assembly_stats_file)

        counts = self._calc_alignment_counts(pipeline_output["bbmap"]["stats_file"])
        m50, m90 = self._calc_m50_m90(pipeline_output["bbmap"]["coverage_file"], counts["input_reads"])
        alignment_stats = "Alignment of reads to final assembly:\n"
        if "error" in counts:
            alignment_stats = alignment_stats + "An error occurred! Unable to calculate alignment stats: {}".format(counts["error"])
        else:
            alignment_stats = alignment_stats + (
                "The number of reads used as input to aligner is: {}\n"
                "The number of aligned reads is: {} ({})\n"
                "m50/m90 (length where 50% or 90% of reads align to "
                "contigs of this length or larger) is: {}/{}\n\n"
            ).format(counts["input_reads"], counts["aligned"], counts["aligned_percent"], m50, m90)

        protocol = self._protocol_text(pipeline_output)

        html_content = "<html><pre>{}{}{}{}{}</pre></html>".format(
            header,
            read_processing,
            assembly_stats,
            alignment_stats,
            protocol
        )

        with open(html_file_name, "w") as outfile:
            outfile.write(html_content)

    def _protocol_text(self, pipeline_output):
        # if rqcfilter is run, its command looks like this:
        #
        # and if not, it looks like this:
        # "BBTools.run_RQCFilter_local -- skipped. No command run."
        rqcfilter_version = pipeline_output["rqcfilter"]["version_string"]
        rqcfilter_command = pipeline_output["rqcfilter"]["command"]
        if "skipped" in rqcfilter_command:
            rqcfilter_command = None
            rqcfilter_version = None

        bfc_version = pipeline_output["bfc"]["version_string"]
        # the full bfc command str looks like this:
        # /kb/module/bin/bfc -1 -k 21 -t 10 input_file_path > output_file_path
        # trim down the first token, and the last 3 (infile > outfile)
        bfc_command = " ".join(pipeline_output["bfc"]["command"].split(" ")[1:-3])

        # for spades, we see the following: want the following cmd string:
        # /opt/SPAdes-3.12.0-Linux/bin/spades.py --only-assembler -k 33,55,77 --meta -t 32 -m 2000 -o output_directory --12 input_reads_file"
        # so we want to skip the first, and the last 4
        spades_command = " ".join(pipeline_output["spades"]["command"].split(" ")[1:-4])
        spades_version = pipeline_output["spades"]["version_string"]

        bbmap_version = pipeline_output["bbmap"]["version_string"]

        rqcfilter_section = ""
        if rqcfilter_command is not None:
            rqcfilter_section = "\n    Reads were filtered using RQCFilter ({}), with the following options: \"{}\"\n\n".format(
                rqcfilter_version,
                rqcfilter_command
            )

        text = """Assembly Methods:{}
    Trimmed, screened, paired-end Illumina reads (see documentation for bbtools(1) filtered reads)
were read corrected using bfc ({}) with parameters "{}" (2). Reads with no mate pair
were removed.

    The resulting reads were then assembled using SPAdes assembler ({}) (3) using
a range of Kmers with the following options: "{}"

    The entire filtered read set was mapped to the final assembly and coverage information
generated using bbmap ({}) (4) using default parameters exept ambiguous=random.

    This processing pipeline is the KBase App "Run JGI Metagenome Assembly Pipeline",
version 1.0.0 (5). It is based on the JGI pipeline: jgi_mg_meta_rqc.py (version 2.1.0).


  (1) B. Bushnell: BBTools software package, http://bbtools.jgi.doe.gov
  (2) BFC: correcting Illumina sequencing errors. - Bioinformatics. 2015 Sep 1;31(17):2885-7. doi:
10.1093/bioinformatics/btv290. Epub 2015 May 6.
  (3) metaSPAdes: a new versatile metagenomic assembler - Genome Res. 2017. 27: 824-834. doi:
10.1101/gr.213959.116
  (4) bbmap.sh https://bbtools.jgi.doe.gov
  (5) KBase jgi_mg_assembly https://github.com/kbaseapps/jgi_mg_assembly"""
        return text.format(rqcfilter_section, bfc_version, bfc_command, spades_version, spades_command, bbmap_version)

    def _percent_reads(self, x, y):
        """
        A little utility for calculating the percent of total reads for a few places in the report
        file. This assumes that x is some smaller percentage of y, and that y should be > 0.
        For example, x is expected to be a filtered reads value, and y would be the total reads
        entered into the filter. For simplicity, if y is 0, then the input reads was 0, so the
        number filtered (and this percentage) has no meaning - to keep it simple, this just returns
        0 in that case.
        """
        if y == 0:
            return 0  # special case here - if y = 0, and x > 0, something's funky. ignore.
        return int(float(x) / float(y) * 100)

    def _calc_alignment_counts(self, bbmapfile):
        """
        Adapted from jgi_mga_create_metadata_dot_json.metagenome_alignment_metadata

        This calculates the number of reads used as input to the BBMap alignment tool and the
        number of reads aligned by reading and interpreting the output to stderr from BBMap.

        Returns a dict with the following keys:
        * error - string, returned if there's an error while reading files.
        * aligned - number of aligned reads
        * input_reads - number of input reads sent to BBMap
        * aligned_percent - percent of reads aligned to the assembly
        """
        # fetch the number of mapped reads
        counts = dict()
        # bbmapfile = pipeline_output["bbmap"]["stats_file"]
        cmd = "grep \"^mapped:\" " + bbmapfile + r' |  cut -f 3 |  sed "s/\s//g"'
        lines = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.readlines()
        if len(lines) != 2:
            counts["error"] = "Can't calculate number of mapped reads!"
            counts["aligned"] = 0
        else:
            num_aligned_reads = int(lines[0]) + int(lines[1])
            counts["aligned"] = int(num_aligned_reads)

        # fetch the number of input reads
        num_input_reads = ""
        cmd = "grep \"^Reads Used:\" " + bbmapfile + " | cut -f 2"
        lines = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.readlines()
        if len(lines) != 1:
            if not counts["error"]:
                counts["error"] = ""
            counts["error"] = counts["error"] + "Can't calculate number of input reads!"
            counts["input_reads"] = 0
        else:
            result = re.search(r'^(\d+).*$', lines[0].decode('utf-8'))
            if hasattr(result, 'group'):
                if result.group(1):
                    num_input_reads = result.group(1)
            counts["input_reads"] = int(num_input_reads)
        counts["aligned_percent"] = self._percent_reads(counts["aligned"], counts["input_reads"])
        return counts

    def _calc_m50_m90(self, covstats_file, input_reads_count):
        """
        Calculates the m50 and m90 values from the covstats.txt file generated from BBMap (in
        stats_files["covstats"]). So it needs a file in that format, and doesn't do too much
        format checking. It also requires the number of reads used to generate the mapping.
        """
        m50 = "NA"
        m90 = "NA"
        total = 0
        with open(covstats_file, "r") as f:
            for line in f:
                vals = line.split()
                if not vals[6].isdigit():
                    continue
                total = total + int(vals[6]) + int(vals[7])
                if total / input_reads_count > 0.5 and m50 == "NA":
                    m50 = vals[2]
                if total / input_reads_count > 0.9 and m90 == "NA":
                    m90 = vals[2]
        return m50, m90

    def _upload_report(self, report_dir, file_links, workspace_name, saved_objects):
        dfu = DataFileUtil(self.callback_url)
        upload_info = dfu.file_to_shock({
            'file_path': report_dir,
            'pack': 'zip'
        })
        shock_id = upload_info['shock_id']

        report_params = {
            'message': 'JGI metagenome assembly report',
            'direct_html_link_index': 0,
            'html_links': [{
                'shock_id': shock_id,
                'name': 'index.html',
                'description': 'assembly report'
            }],
            'file_links': file_links,
            'report_object_name': 'JGI_assembly_pipeline.' + str(uuid.uuid4()),
            'workspace_name': workspace_name,
            'objects_created': saved_objects
        }

        report_client = KBaseReport(self.callback_url)
        report = report_client.create_extended_report(report_params)
        return {
            'report_ref': report['ref'],
            'report_name': report['name']
        }
