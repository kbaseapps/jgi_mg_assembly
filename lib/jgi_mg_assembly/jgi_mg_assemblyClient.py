# -*- coding: utf-8 -*-
############################################################
#
# Autogenerated by the KBase type compiler -
# any changes made here will be overwritten
#
############################################################

from __future__ import print_function
# the following is a hack to get the baseclient to import whether we're in a
# package or not. This makes pep8 unhappy hence the annotations.
try:
    # baseclient and this client are in a package
    from .baseclient import BaseClient as _BaseClient  # @UnusedImport
except:
    # no they aren't
    from baseclient import BaseClient as _BaseClient  # @Reimport


class jgi_mg_assembly(object):

    def __init__(
            self, url=None, timeout=30 * 60, user_id=None,
            password=None, token=None, ignore_authrc=False,
            trust_all_ssl_certificates=False,
            auth_svc='https://kbase.us/services/authorization/Sessions/Login'):
        if url is None:
            raise ValueError('A url is required')
        self._service_ver = None
        self._client = _BaseClient(
            url, timeout=timeout, user_id=user_id, password=password,
            token=token, ignore_authrc=ignore_authrc,
            trust_all_ssl_certificates=trust_all_ssl_certificates,
            auth_svc=auth_svc)

    def run_mg_assembly_pipeline(self, params, context=None):
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
        return self._client.call_method(
            'jgi_mg_assembly.run_mg_assembly_pipeline',
            [params], self._service_ver, context)

    def status(self, context=None):
        return self._client.call_method('jgi_mg_assembly.status',
                                        [], self._service_ver, context)
