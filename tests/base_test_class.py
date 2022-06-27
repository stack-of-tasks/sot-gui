from typing import Dict, List
from unittest import TestCase
from pathlib import Path

from PySide2.QtWidgets import QGraphicsItem, QGraphicsTextItem

from sot_ipython_connection.sot_kernel import SOTKernel
from sot_ipython_connection.app.sot_script_executer import main as script_executer
from sot_gui.graph import Graph


input_scripts_dir = str(Path(__file__).resolve().parent/'dg_scripts')


# FIXME:
# If a SOTKernel is already running, another cannot be launched because it
# would use the same ports (this is expected behavior).
# When running these tests when a SOTKernel is already running, it should fail
# because this class launches its own SOTKernel. But the tests are run anyway
# because the exception when launching the kernel is ignored, and each test
# class launches a client that connect to the latest SOTKernel (i.e the one
# launched before the tests).


class BaseTestClass(TestCase):

    def setUp(self):
        # Launching the kernel in a subprocess
        self._kernel = SOTKernel()
        self._kernel.run_non_blocking()
        self._script_executer = script_executer
        self._graph = Graph()

    def tearDown(self):
        # Terminating the kernel's subprocess
        del self._graph
        self._kernel.stop_non_blocking()


    def _get_qt_items_info(self, qt_items: List[QGraphicsItem]) -> Dict:
        items_info = []

        for item in qt_items:
            item_info = {}

            item_type = type(item)
            item_info['type'] = item_type

            item_info['children'] = self.get_qt_items_info(item.childItems())

            if item_type == QGraphicsTextItem:
                item_info['text'] = item.toPlainText()

            items_info.append(item_info)

        return items_info


    def _is_expected_in_actual_list(self, expected: Dict, actual: List[Dict]) \
                                    -> bool:
        # for idx, actual_item in enumerate(actual_items_info):
        #         if self._deep_comparison_item_info(expected_item, actual_item):
        #             actual_items_info.pop(idx)
        #             return True

        #     # If the expected item wasn't found in the actual items:
        #     return False
        ...


    def _deep_comparison_item_info(self, dict1: Dict, dict2: Dict) -> bool:
        ...