"""
Some utility functions for mangling, er, managing files.
Specifically:
    - reads file pulling
    - assembly file pushing
    - KBaseReport assembly and uploading
"""

def fetch_reads_files(reads_upas):
    """
    From a list of reads UPAs, uses ReadsUtils to fetch the reads as files.
    """
