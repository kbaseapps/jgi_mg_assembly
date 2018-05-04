"""
Used for making and uploading a KBaseReport for the MG assembly pipeline results.
"""
import os
import uuid
import shutil
import zipfile
import subprocess
import re
from DataFileUtil.DataFileUtilClient import DataFileUtil
from KBaseReport.KBaseReportClient import KBaseReport
from util import mkdir


class ReportUtil(object):
    def __init__(self, callback_url, output_dir):
        self.callback_url = callback_url
        self.output_dir = output_dir

    def make_report(self, stats_files, reads_counts, workspace_name, saved_objects):
        """
        From the various stats files, this produces an HTML report containing most of the
        information. It also assembles those various stats files into a report object.
        stats_files is expected to be a dict with the following keys:
        * bbmap_stats - the generated stats from BBMap, that's usually sent to stderr
        * covstats - the coverage stats from BBMap
        * assembly_stats - stats from the assembly (made with BBTools stats.sh)
        * assembly_tsv - a TSV version of most of those stats (with some funky headers)
        * rqcfilter_log - a text file with the run log from RQCFilter

        reads_counts is another dict, with reads counted at different points in the pipeline
        * pre_filter - number of reads before any filtering, as uploaded by the user
        * filtered - number of reads after running RQCFilter
        * corrected - number of reads after running BFC

        Expects saved_objects to be in the correct format for KBaseReports. So, a list of dicts:
        {
            "ref": upa,
            "description": some string
        }

        After assembling the report, it uses the KBaseReports module to upload, and returns a dict
        with "report_ref" and "report_name" keys.
        """
        if not stats_files or not isinstance(stats_files, dict):
            raise ValueError("A dictionary of stats_files is required")
        required_files = ["bbmap_stats", "covstats", "assembly_stats", "assembly_tsv", "rqcfilter_log"]
        for req in required_files:
            if req not in stats_files:
                raise ValueError("Required stats file '{}' is not present!".format(req))
        for key in stats_files:
            if not os.path.exists(stats_files[key]):
                raise ValueError("Stats file '{}' with path '{}' doesn't appear to exist!".format(key, stats_files[key]))
        if not reads_counts or not isinstance(reads_counts, dict):
            raise ValueError("A dictionary of reads_counts is required")
        required_counts = ["pre_filter", "filtered", "corrected"]
        for req in required_counts:
            if req not in reads_counts:
                raise ValueError("Required reads count '{}' is not present!".format(req))
        if not workspace_name:
            raise ValueError("A workspace name is required")
        if not saved_objects:
            saved_objects = list()

        html_report_dir = os.path.join(self.output_dir, "report")
        mkdir(html_report_dir)

        result_file = os.path.join(html_report_dir, 'assembly_report.zip')
        with zipfile.ZipFile(result_file, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as report_zip:
            for file_name in stats_files.values():
                zipped_file_name = os.path.basename(file_name)
                report_zip.write(file_name, zipped_file_name)
                shutil.copy(file_name, os.path.join(html_report_dir, zipped_file_name))
        file_links = [{
            'path': result_file,
            'name': os.path.basename(result_file),
            'label': 'assembly_report',
            'description': 'JGI Metagenome Assembly Report'
        }]

        html_file_name = os.path.join(html_report_dir, "index.html")
        self._write_html_file(html_file_name, stats_files, reads_counts)
        return self._upload_report(html_report_dir, file_links, workspace_name, saved_objects)

    def _write_html_file(self, html_file_name, stats_files, reads_counts):
        """
        Assembles and writes out an HTML report file, following the idoms developed by JGI.
        Right now, this just cobbles together text into a single <pre> formatted HTML file.
        """
        header = "Assembly using the JGI metagenome assembly pipeline, interpreted by KBase\n\n"

        filter_percent = self._percent_reads(reads_counts["filtered"], reads_counts["pre_filter"])
        corrected_percent = self._percent_reads(reads_counts["corrected"],
                                                reads_counts["pre_filter"])
        read_processing = (
            "Read Pre-processing\n"
            "The number of raw input reads is: {}\n"
            "The number of reads remaining after quality filter: {} ({}% of raw)\n"
            "The final number of reads remaining "
            "after read correction: {} ({}% of raw)\n\n"
        ).format(reads_counts["pre_filter"], reads_counts["filtered"], filter_percent,
                 reads_counts["corrected"], corrected_percent)

        with open(stats_files["assembly_stats"]) as stats:
            assembly_stats_file = "".join(stats.readlines())
        assembly_stats = "Assembly stats:\n{}".format(assembly_stats_file)

        counts = self._calc_alignment_counts(stats_files, reads_counts)
        m50, m90 = self._calc_m50_m90(stats_files, counts["input_reads"])
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

        protocol = self._protocol_text()

        html_content = "<html><pre>{}{}{}{}{}</pre></html>".format(
            header,
            read_processing,
            assembly_stats,
            alignment_stats,
            protocol
        )

        with open(html_file_name, "w") as outfile:
            outfile.write(html_content)

    def _protocol_text(self):
        text = """Assembly Methods:
    Trimmed, screened, paired-end Illumina reads (see documentation for bbtools(1) filtered reads)
were read corrected using bfc (version r181) with "-1 -s 10g -k 21 -t 10" (2). Reads with no mate pair
were removed.

    The resulting reads were then assembled using SPAdes assembler (SPAdes version: 3.11.1) (3) using
a range of Kmers with the following options: "-m 2000 --only-assembler -k 33,55,77,99,127 --meta -t 32"

    The entire filtered read set was mapped to the final assembly and coverage information
generated using bbmap (version 37.75) (4) using default parameters exept ambiguous=random.

    This processing pipeline is the KBase App "Run JGI Metagenome Assembly Pipeline",
version 1.0.0 (5). It is based on the JGI pipeline: jgi_mg_meta_rqc.py (version 2.1.0).

If you have any questions, please contact the JGI project manager.


  (1) B. Bushnell: BBTools software package, http://bbtools.jgi.doe.gov
  (2) BFC: correcting Illumina sequencing errors. - Bioinformatics. 2015 Sep 1;31(17):2885-7. doi:
10.1093/bioinformatics/btv290. Epub 2015 May 6.
  (3) metaSPAdes: a new versatile metagenomic assembler - Genome Res. 2017. 27: 824-834.  doi:
10.1101/gr.213959.116
  (4) bbmap.sh https://bbtools.jgi.doe.gov
  (5) KBase jgi_mg_assembly https://github.com/kbaseapps/jgi_mg_assembly"""
        return text

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

    def _calc_alignment_counts(self, stats_files, reads_counts):
        """
        Adapted from jgi_mga_create_metadata_dot_json.metagenome_alignment_metadata

        This calculates the number of reads used as input to the BBMap alignment tool and the
        number of reads aligned by reading and interpreting the output to stderr from BBMap
        (captured in stats_files["bbmap_stats"]).
        """
        # fetch the number of mapped reads
        counts = dict()
        bbmapfile = stats_files["bbmap_stats"]
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
            result = re.search(r'^(\d+).*$', lines[0])
            if hasattr(result, 'group'):
                if result.group(1):
                    num_input_reads = result.group(1)
            counts["input_reads"] = int(num_input_reads)
        counts["aligned_percent"] = self._percent_reads(counts["aligned"], counts["input_reads"])
        return counts

    def _calc_m50_m90(self, stats_files, input_reads_count):
        """
        Calculates the m50 and m90 values from the covstats.txt file generated from BBMap (in
        stats_files["covstats"]). So it needs a file in that format, and doesn't do too much
        format checking. It also requires the number of reads used to generate the mapping.
        """
        m50 = "NA"
        m90 = "NA"
        total = 0
        with open(stats_files["covstats"], "r") as f:
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
