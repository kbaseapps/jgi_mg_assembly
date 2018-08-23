import unittest
import os
import util
from jgi_mg_assembly.pipeline_steps.readlength import ReadLengthRunner

class TestReadlength(unittest.TestCase):
    def test_readlength(self):
        # copy small fq file to scratch
        reads_file = util.file_to_scratch(os.path.join("data", "small.forward.fq"), overwrite=True)
        readlength = ReadLengthRunner(util.get_config()["scratch"], util.get_config()["scratch"])
        reads_info = readlength.run(reads_file, "reads_info_file.txt")

        self.assertEqual(reads_info["count"], 1250)
        self.assertEqual(reads_info["bases"], 125000)
        self.assertEqual(reads_info["max"], 100)
        self.assertEqual(reads_info["min"], 100)
        self.assertEqual(reads_info["avg"], 100.0)
        self.assertEqual(reads_info["median"], 100)
        self.assertEqual(reads_info["mode"], 100)
        self.assertEqual(reads_info["std_dev"], 0.0)
        self.assertTrue(os.path.exists(reads_info["output_file"]))
        self.assertIn("readlength.sh", reads_info["command"])
        self.assertIn("BBTools", reads_info["version_string"])