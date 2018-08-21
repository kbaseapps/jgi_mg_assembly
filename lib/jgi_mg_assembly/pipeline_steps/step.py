from __future__ import print_function
import subprocess


class Step(object):
    def __init__(self, name, base_command, scratch_dir, shell_cmd):
        """
        base_command: the string for which command to run from the command line.
        name: the name of the command for showing the user.
        scratch_dir: the working directory to use.
        shell_cmd: True if this is a shell command, False otherwise. I.e., if subprocess.Popen needs shell access
        """
        self.base_command = base_command
        self.step_name = name
        self.shell_cmd = shell_cmd
        self.scratch_dir = scratch_dir

    def run(self, *params):
        """
        params: the list of command line parameters to use for the command.

        This invokes the command to be run with the list of command line parameters by calling
        subprocess.Popen.

        This handles the running part. Extending functions should handle the rest, including
        exception raising based on the exit code.

        Returns the exit code, and the command string (concatenated with spaces), mainly for reporting out to the user.
        """
        command = [self.base_command] + list(params)
        print("In working directory: ")
        print("Running Pipeline Step: {}".format(self.step_name))
        print("Running command: {}".format(command))

        run_command = command
        if self.shell_cmd:
            run_command = " ".join(run_command)
        p = subprocess.Popen(run_command, cwd=self.scratch_dir, shell=self.shell_cmd)
        exit_code = p.wait()

        if exit_code == 0:
            print("Successfully ran {}".format(self.step_name))
        else:
            print("========================================\nPipeline step {} returned a nonzero error code!\nCommand: {}\nExit code: {}\n\n".format(self.step_name, ' '.join(command), exit_code))
        return (exit_code, ' '.join(command))