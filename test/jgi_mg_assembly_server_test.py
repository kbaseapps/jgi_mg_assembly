# -*- coding: utf-8 -*-
import unittest
import os  # noqa: F401
import json  # noqa: F401
import shutil

from pprint import pprint  # noqa: F401

from jgi_mg_assembly.jgi_mg_assemblyImpl import jgi_mg_assembly
from jgi_mg_assembly.jgi_mg_assemblyServer import MethodContext
from jgi_mg_assembly.authclient import KBaseAuth as _KBaseAuth

from AssemblyUtil.AssemblyUtilClient import AssemblyUtil
from ReadsUtils.ReadsUtilsClient import ReadsUtils

import util


class jgi_mg_assemblyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        token = util.get_token()
        cls.cfg = util.get_config()
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'jgi_mg_assembly',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.serviceImpl = jgi_mg_assembly(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']

    @classmethod
    def tearDownClass(cls):
        util.tear_down_workspace()

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    def load_fasta_file(self, filename, obj_name, contents):
        f = open(filename, 'w')
        f.write(contents)
        f.close()
        assemblyUtil = AssemblyUtil(self.callback_url)
        assembly_ref = assemblyUtil.save_assembly_from_fasta({'file': {'path': filename},
                                                              'workspace_name': util.get_ws_name(),
                                                              'assembly_name': obj_name
                                                              })
        return assembly_ref

    def load_pe_reads(self, fwd_file, rev_file):
        """
        Copies from given dir to scratch. Then calls ReadsUtils to upload from scratch.
        """
        fwd_file_path = os.path.join(self.scratch, "fwd_file.fastq")
        rev_file_path = os.path.join(self.scratch, "rev_file.fastq")
        shutil.copy(fwd_file, fwd_file_path)
        shutil.copy(rev_file, rev_file_path)
        ru = ReadsUtils(self.callback_url)
        pe_reads_params = {
            'fwd_file': fwd_file_path,
            'rev_file': rev_file_path,
            'sequencing_tech': 'Illumina',
            'wsname': util.get_ws_name(),
            'name': 'MyPairedEndLibrary'
        }
        return ru.upload_reads(pe_reads_params)['obj_ref']

    def test_run_pipeline_ok(self):
        # load some data here.
        reads_upa = self.load_pe_reads(os.path.join("data", "small.forward.fq"), os.path.join("data", "small.reverse.fq"))
        output = self.getImpl().run_mg_assembly_pipeline(self.getContext(), {
            "reads_upa": reads_upa,
            "output_assembly_name": "MyNewAssembly",
            "workspace_name": util.get_ws_name()
        })[0]

        self.assertIn('report_name', output)
        self.assertIn('report_ref', output)
        self.assertIn('assembly_upa', output)
        pprint(output)
