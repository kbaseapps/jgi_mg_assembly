"""
Some utility functions for mangling, er, managing files.
Specifically:
    - reads file pulling
    - assembly file pushing
    - KBaseReport assembly and uploading
"""
from ReadsUtils.ReadsUtilsClient import ReadsUtils
from AssemblyUtil.AssemblyUtilClient import AssemblyUtil


class FileUtil(object):
    def __init__(self, callback_url):
        self.callback_url = callback_url

    def fetch_reads_files(self, reads_upas):
        """
        From a list of reads UPAs, uses ReadsUtils to fetch the reads as files.
        Returns them as a list of dictionaries.
        """
        ru = ReadsUtils(self.callback_url)
        reads_info = ru.download_reads(({
            'read_libraries': reads_upas,
            'interleaved': 'true',
            'gzipped': None
        }))
        return reads_info

    def save_assembly_files(self, file_paths):
        """
        From a list of file paths, uploads them to KBase, generates Assembly objects,
        then returns the generated UPAs.
        """
        au = AssemblyUtil(self.callback_url)
        assembly_upas = []
        return assembly_upas
