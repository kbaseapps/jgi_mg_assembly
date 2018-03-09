"""
Used for making and uploading a KBaseReport for the MG assembly pipeline results.
"""
import os
import uuid
import shutil
import zipfile
from DataFileUtil.DataFileUtilClient import DataFileUtil
from KBaseReport.KBaseReportClient import KBaseReport
from util import mkdir


class ReportUtil(object):
    def __init__(self, callback_url, scratch_dir):
        self.callback_url = callback_url
        self.scratch_dir = scratch_dir

    def make_report(self, stats_file, coverage_file, workspace_name, saved_objects):
        """
        First version - make something from the stats file and coverage file.
        Expects saved_objects to be in the correct format for KBaseReports. So, a list of dicts:
        {
            "ref": upa,
            "description": some string
        }
        Returns a dict with "report_ref" and "report_name" keys.
        """
        if not stats_file:
            raise ValueError("A stats file is required")
        if not os.path.exists(stats_file):
            raise ValueError("The stats file '{}' does not appear to exist".format(stats_file))
        if not coverage_file:
            raise ValueError("A coverage file is required")
        if not os.path.exists(coverage_file):
            raise ValueError("The coverage file '{}' does not appear to exist"
                             .format(coverage_file))
        if not workspace_name:
            raise ValueError("A workspace name is required")
        if not saved_objects:
            saved_objects = list()

        html_report_dir = os.path.join(self.scratch_dir, "report")
        mkdir(html_report_dir)

        stats_file_name = os.path.basename(stats_file)
        coverage_file_name = os.path.basename(coverage_file)
        result_file = os.path.join(html_report_dir, 'assembly_report.zip')
        with zipfile.ZipFile(result_file, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as report_zip:
            report_zip.write(stats_file, stats_file_name)
            report_zip.write(coverage_file, coverage_file_name)
        file_links = [{
            'path': result_file,
            'name': os.path.basename(result_file),
            'label': 'assembly_report',
            'description': 'JGI Metagenome Assembly Report'
        }]
        shutil.copy(stats_file, os.path.join(html_report_dir, stats_file_name))
        shutil.copy(coverage_file, os.path.join(html_report_dir, coverage_file_name))

        html_file_name = os.path.join(html_report_dir, "index.html")
        self._write_html_file(html_file_name, stats_file, coverage_file)
        return self._upload_report(html_report_dir, file_links, workspace_name, saved_objects)

    def _write_html_file(self, html_file_name, stats_file, coverage_file):
        html_head = """
        <head>
            <style>
                td,th {
                  border: 1px solid black;
                  padding: 0.5em;
                  text-align: left;
                }

                table {
                  border-collapse: collapse;
                }
            </style>
        </head>
        """
        table = ""
        stats_data = list()
        with open(stats_file, "r") as f:
            lines = f.readlines()
            header = lines.pop(0)
            headers = header.strip().split("\t")
            num_headers = len(headers)
            for line in lines:
                stats_data.append(line.strip().split("\t"))
            for i in range(num_headers):
                l = "<tr><th>{}</th><td>{}</td></tr>\n".format(
                        headers[i],
                        "</td><td>".join(stats_data[j][i] for j in range(len(stats_data)))
                    )
                table = table + l
        table = "<table>\n{}</table>".format(table)
        html_content = "<html>\n{}<body>\n{}\n</body></html>".format(html_head, table)
        with open(html_file_name, "w") as outfile:
            outfile.write(html_content)

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
