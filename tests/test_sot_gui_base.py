import unittest
from pathlib import Path
from time import sleep
from subprocess import Popen


input_scripts_dir = str(Path(__file__).resolve().parent/'dg_scripts')


class TestSotGuiBase(unittest.TestCase):

    @classmethod
    def setup_class(self):
        # Launching the kernel in a subprocess:
        interpreter_path = (
            Path(__file__).resolve().parent.parent /
            'sot_ipython_connection'/'app'/'sot_interpreter.py'
        )
        self.kernel_process = Popen(["python3", interpreter_path])
        sleep(5)


    @classmethod
    def teardown_class(self):
        # Terminating and killing the kernel's subprocess:
        self.kernel_process.terminate()
        self.kernel_process.wait(10)
        self.kernel_process.kill()
        self.kernel_process.wait(10)