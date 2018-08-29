import unittest
from jgi_mg_assembly.pipeline_steps.step import Step
import util

class StepTest(unittest.TestCase):
    """
    Tests the pipeline step base class.
    """

    def test_step_bad_fn(self):
        name = "Foo"
        version_name = "Bar"
        base_command = "foo"
        output_dir = "output_dir"

        mystep = Step(name, version_name, base_command, util.get_config()["scratch"], output_dir, False)
        with util.captured_stdout() as (out, err):
            params = ["flag1", "flag2"]
            (exit_code, command) = mystep.run(*params)
        self.assertIn("raised an OSError", out.getvalue())
        self.assertEqual("foo flag1 flag2", command)
        self.assertNotEqual(exit_code, 0)

    def test_step_ok(self):
        name = "Just ls"
        version_name = "ls"
        base_command = "ls"
        output_dir = "output_dir"
        mystep = Step(name, version_name, base_command, util.get_config()["scratch"], output_dir, True)
        with util.captured_stdout() as (out, err):
            (exit_code, command) = mystep.run()
        self.assertIn("Successfully ran {}".format(name), out.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual("ls", command)