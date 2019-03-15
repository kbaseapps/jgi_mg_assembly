# -*- coding: utf-8 -*-
#BEGIN_HEADER
# The header block is where all import statments should live
import os
from Bio import SeqIO
from pprint import pprint, pformat
from AssemblyUtil.AssemblyUtilClient import AssemblyUtil
from KBaseReport.KBaseReportClient import KBaseReport

from jgi_mg_assembly.runner.pipeline import Pipeline
#END_HEADER


class jgi_mg_assembly:
    '''
    Module Name:
    jgi_mg_assembly

    Module Description:
    A KBase module: jgi_mg_assembly
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.5.5"
    GIT_URL = "https://github.com/briehl/jgi_mg_assembly"
    GIT_COMMIT_HASH = "2bd8a5ce33c46ef2d3a6da603ee627e9d02d2082"

    #BEGIN_CLASS_HEADER
    # Class variables and functions can be defined in this block
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR

        # Any configuration parameters that are important should be parsed and
        # saved in the constructor.
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.scratch_dir = config['scratch']

        #END_CONSTRUCTOR
        pass


    def run_mg_assembly_pipeline(self, ctx, params):
        """
        :param params: instance of type "AssemblyPipelineParams" (Inputs for
           the Assembly pipeline. reads_upa: UPA for the input reads object.
           This should be a Paired-End Illumina reads file. workspace_name:
           name of the workspace to upload to at the end.
           output_assembly_name: name of the output assembly file.
           skip_rqcfilter: If 1, skip the RQCFilter step of the pipeline. If
           0, run it. (default = 0) cleaned_reads_name (optional): If not
           empty, this will cause the finalized, cleaned/filtered reads to be
           uploaded as a new reads object with this name. This'll be an
           interleaved paired-end reads object. filtered_reads_name
           (optional, unless alignment_name is present): If not empty, this
           will cause the RQCFiltered reads to be uploaded as a new reads
           object. These are the reads aligned to the final assembly, so
           these are needed to associate with the final alignment if that
           alignment is to be kept. debug (hidden option): If 1, run in debug
           mode. A little more verbose, and trims some parameters from
           various steps so it can run locally(ish). You probably don't want
           to do this in production, it's meant for testing.) -> structure:
           parameter "reads_upa" of type "reads_upa" (Should be only
           Paired-end reads.), parameter "workspace_name" of String,
           parameter "output_assembly_name" of String, parameter
           "cleaned_reads_name" of String, parameter "filtered_reads_name" of
           String, parameter "skip_rqcfilter" of type "boolean" (A boolean -
           0 for false, 1 for true. @range (0, 1)), parameter "debug" of type
           "boolean" (A boolean - 0 for false, 1 for true. @range (0, 1))
        :returns: instance of type "AssemblyPipelineResults" (Outputs from
           the Assembly pipeline. report_name: The name of the generated
           report object. report_ref: The UPA for the generated report
           object. assembly_upa: The UPA for the newly made assembly object.
           cleaned_reads_upa (optional): The UPA for the finalized, cleaned
           reads that are assembled in the pipeline, if requested by the
           input. filtered_reads_upa (optional): The UPA for the RQCFiltered
           reads, if requested by the input, AND skip_rqcfilter is not true.)
           -> structure: parameter "report_name" of String, parameter
           "report_ref" of String, parameter "assembly_upa" of type
           "assembly_upa", parameter "cleaned_reads_upa" of type "reads_upa"
           (Should be only Paired-end reads.), parameter "filtered_reads_upa"
           of type "reads_upa" (Should be only Paired-end reads.)
        """
        # ctx is the context object
        # return variables are: results
        #BEGIN run_mg_assembly_pipeline
        pipeline = Pipeline(self.callback_url, self.scratch_dir)
        results = pipeline.run(params)
        #END run_mg_assembly_pipeline

        # At some point might do deeper type checking...
        if not isinstance(results, dict):
            raise ValueError('Method run_mg_assembly_pipeline return value ' +
                             'results is not type dict as required.')
        # return the results
        return [results]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
