"""
Used for making and uploading a KBaseReport for the MG assembly pipeline results.
"""
import os
import errno
import uuid
import shutil
import zipfile
from DataFileUtil.DataFileUtilClient import DataFileUtil
from KBaseReport.KBaseReportClient import KBaseReport


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
        """
        html_report_dir = os.path.join(self.scratch_dir, "report_{}".format(uuid.uuid4()))
        self._mkdir_p(html_report_dir)

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
        table = ""
        with open(stats_file, "r") as stats:
            lines = stats.readlines()
            head = lines.pop(0).strip().split("\t")
            table = "<tr><th>{}</th></tr>".format("</th><th>".join(head))
            for line in lines:
                elems = "</td><td>".join(line.strip().split("\t"))
                elems = "<tr><td>{}</td></tr>\n".format(elems)
                table = table + elems
        table = "<table>\n{}</table>".format(table)
        html_content = "<html>\n<body>\n{}\n</body></html>".format(table)
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

    def _mkdir_p(self, path):
        if not path:
            return
        try:
            os.makedirs(path)
        except OSError as ex:
            if ex.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise
