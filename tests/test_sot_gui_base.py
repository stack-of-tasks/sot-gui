import unittest
from pathlib import Path
import time
from subprocess import Popen

from sot_ipython_connection.sot_kernel import SOTKernel


class TestSotGuiBase(unittest.TestCase):

    @classmethod
    def setup_class(self):
        # Launching the kernel in a subprocess:
        interpreter_path = (
            Path(__file__).resolve().parent.parent /
            'sot_ipython_connection'/'app'/'sot_interpreter.py'
        )
        self.kernel_process = Popen(["python3", interpreter_path])
        time.sleep(5)

        self.kernel = SOTKernel()
        self.kernel.run()


    @classmethod
    def teardown_class(self):
        # Terminating and killing the kernel's subprocess:
        self.kernel_process.terminate()
        self.kernel_process.wait(10)
        self.kernel_process.kill()
        self.kernel_process.wait(10)