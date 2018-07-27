# -*- coding: utf-8 -*-
import unittest
import os  # noqa: F401
import json  # noqa: F401

from pprint import pprint  # noqa: F401

from jgi_mg_assembly.jgi_mg_assemblyImpl import jgi_mg_assembly
from jgi_mg_assembly.jgi_mg_assemblyServer import MethodContext
from jgi_mg_assembly.authclient import KBaseAuth as _KBaseAuth
from jgi_mg_assembly.runner.readlength import readlength

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
        cls.reads_upa = util.load_pe_reads(os.path.join("data", "small.forward.fq"),
                                           os.path.join("data", "small.reverse.fq"))

    @classmethod
    def tearDownClass(cls):
        util.tear_down_workspace()

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    def test_run_pipeline_ok(self):
        # load some data here.
        output = self.getImpl().run_mg_assembly_pipeline(self.getContext(), {
            "reads_upa": self.reads_upa,
            "output_assembly_name": "MyNewAssembly",
            "workspace_name": util.get_ws_name()
        })[0]

        self.assertIn('report_name', output)
        self.assertIn('report_ref', output)
        self.assertIn('assembly_upa', output)
        pprint(output)

    def test_run_pipeline_missing_inputs(self):
        with self.assertRaises(ValueError):
            self.getImpl().run_mg_assembly_pipeline(self.getContext(), {
                "reads_upa": None,
                "output_assembly_name": "MyNewAssembly",
                "workspace_name": util.get_ws_name()
            })
        with self.assertRaises(ValueError):
            self.getImpl().run_mg_assembly_pipeline(self.getContext(), {
                "reads_upa": self.reads_upa,
                "output_assembly_name": None,
                "workspace_name": util.get_ws_name()
            })
        with self.assertRaises(ValueError):
            self.getImpl().run_mg_assembly_pipeline(self.getContext(), {
                "reads_upa": self.reads_upa,
                "output_assembly_name": "MyNewAssembly",
                "workspace_name": None
            })

    def test_readlength(self):
        # copy small fq file to scratch
        file_path = util.file_to_scratch(os.path.join("data", "small.forward.fq"), overwrite=True)
        reads_info = readlength(file_path, "readlen_out.txt")
        self.assertEqual(reads_info["count"], 1250)
        self.assertEqual(reads_info["bases"], 125000)
        self.assertEqual(reads_info["max"], 100)
        self.assertEqual(reads_info["min"], 100)
        self.assertEqual(reads_info["avg"], 100.0)
        self.assertEqual(reads_info["median"], 100)
        self.assertEqual(reads_info["mode"], 100)
        self.assertEqual(reads_info["std_dev"], 0.0)
