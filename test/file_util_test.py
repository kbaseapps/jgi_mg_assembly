import unittest
import util
import os
from jgi_mg_assembly.utils.file import FileUtil


class file_util_test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = util.get_config()
        cls.scratch_dir = cls.config['scratch']
        cls.callback_url = os.environ["SDK_CALLBACK_URL"]
        cls.reads_upa = util.load_pe_reads(
            os.path.join("data", "small.forward.fq"),
            os.path.join("data", "small.reverse.fq"))
        cls.scratch_assembly = util.file_to_scratch(os.path.join("data", "small_assembly.fa"))

    @classmethod
    def tearDownClass(cls):
        util.tear_down_workspace()

    def _get_file_util(self):
        return FileUtil(self.callback_url)

    def test_fetch_reads_ok(self):
        """
        happy test - reads exist, good upa, etc.
        """
        reads_upa = self.reads_upa
        file_util = self._get_file_util()
        reads_dl = file_util.fetch_reads_files([reads_upa])
        self.assertIsNotNone(reads_dl)
        self.assertIn(reads_upa, reads_dl)
        self.assertTrue(os.path.exists(reads_dl[reads_upa]))

    def test_fetch_reads_no_upas(self):
        """
        Empty UPAs or null list. Should fail properly.
        """
        file_util = self._get_file_util()
        with self.assertRaises(ValueError) as cm:
            file_util.fetch_reads_files(None)
        exception = cm.exception
        self.assertIn("reads_upas must be a list of UPAs", str(exception))

        with self.assertRaises(ValueError) as cm:
            file_util.fetch_reads_files([])
        exception = cm.exception
        self.assertIn("reads_upas must contain at least one UPA", str(exception))

    def test_fetch_reads_bad_upas(self):
        """
        Badly formatted upas, or referencing non-reads object. Should fail properly.
        """
        file_util = self._get_file_util()
        with self.assertRaises(Exception):
            file_util.fetch_reads_files(["not_an_upa"])

    def test_upload_assembly_ok(self):
        """
        happy test - all fields properly made.
        """
        file_util = self._get_file_util()
        asm_upa = file_util.upload_assembly(self.scratch_assembly, util.get_ws_name(), "MyAssembly")
        self.assertIsNotNone(asm_upa)
        ws = util.get_ws_client()
        asm_info = ws.get_object_info3({'objects': [{'ref': asm_upa}]})['infos'][0]
        self.assertEquals("MyAssembly", asm_info[1])
        self.assertIn("KBaseGenomeAnnotations.Assembly", asm_info[2])

    def test_upload_assembly_bad_inputs(self):
        """
        Missing or malformed inputs to file.upload_assembly(). Should fail properly.
        """
        file_util = self._get_file_util()
        with self.assertRaises(ValueError) as cm:
            file_util.upload_assembly(None, util.get_ws_name(), "MyAssembly")
        self.assertIn("must be defined", str(cm.exception))
        with self.assertRaises(ValueError) as cm:
            file_util.upload_assembly("not_a_file", util.get_ws_name(), "MyAssembly")
        self.assertIn("does not exist", str(cm.exception))
        with self.assertRaises(ValueError) as cm:
            file_util.upload_assembly(self.scratch_assembly, None, "MyAssembly")
        self.assertIn("must be defined", str(cm.exception))
        with self.assertRaises(ValueError) as cm:
            file_util.upload_assembly(self.scratch_assembly, util.get_ws_name(), None)
        self.assertIn("must be defined", str(cm.exception))
        with self.assertRaises(Exception):
            file_util.upload_assembly(self.scratch_assembly, "not_a_workspace", "MyAssembly")
