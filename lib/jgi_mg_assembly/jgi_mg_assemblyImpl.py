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
    VERSION = "0.0.1"
    GIT_URL = "https://github.com/briehl/jgi_mg_assembly"
    GIT_COMMIT_HASH = "5762c9a774c822366b3a668e88a4ee1c0f666580"

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
        :param params: instance of type "AssemblyPipelineParams" ->
           structure: parameter "reads_ref" of type "reads_ref" (Should be
           only Paired-end reads.), parameter "workspace_name" of String,
           parameter "assembly_name" of String
        :returns: instance of type "AssemblyPipelineResults" -> structure:
           parameter "report_name" of String, parameter "report_ref" of
           String, parameter "assembly_output" of type "assembly_ref"
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
