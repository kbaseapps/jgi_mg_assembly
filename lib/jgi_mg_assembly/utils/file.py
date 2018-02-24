"""
Some utility functions for mangling, er, managing files.
Specifically:
    - reads file pulling
    - assembly file pushing
    - KBaseReport assembly and uploading
"""
import os

from ReadsUtils.ReadsUtilsClient import ReadsUtils
from AssemblyUtil.AssemblyUtilClient import AssemblyUtil


class FileUtil(object):
    def __init__(self, callback_url):
        self.callback_url = callback_url

    def fetch_reads_files(self, reads_upas):
        """
        From a list of reads UPAs, uses ReadsUtils to fetch the reads as files.
        Returns them as a dictionary from reads_upa -> filename
        """
        if reads_upas is None:
            raise ValueError("reads_upas must be a list of UPAs")
        if len(reads_upas) == 0:
            raise ValueError("reads_upas must contain at least one UPA")
        ru = ReadsUtils(self.callback_url)
        reads_info = ru.download_reads(({
            'read_libraries': reads_upas,
            'interleaved': 'true',
            'gzipped': None
        }))['files']
        file_set = dict()
        for reads in reads_info:
            file_set[reads] = reads_info[reads]['files']['fwd']
        return file_set

    def upload_assembly(self, file_path, workspace_name, assembly_name):
        """
        From a list of file paths, uploads them to KBase, generates Assembly objects,
        then returns the generated UPAs.
        """
        if not file_path:
            raise ValueError("file_path must be defined")
        if not os.path.exists(file_path):
            raise ValueError("The given assembly file '{}' does not exist")
        if not workspace_name:
            raise ValueError("workspace_name must be defined")
        if not assembly_name:
            raise ValueError("assembly_name must be defined")

        au = AssemblyUtil(self.callback_url)
        assembly_upa = au.save_assembly_from_fasta({
            "file": {
                "path": file_path
            },
            "workspace_name": workspace_name,
            "assembly_name": assembly_name
        })
        return assembly_upa
