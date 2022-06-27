from pathlib import Path

from PySide2.QtWidgets import (QGraphicsPolygonItem, QGraphicsEllipseItem, 
   QGraphicsTextItem, QGraphicsPathItem)

from .base_test_class import BaseTestClass, input_scripts_dir


class TestCircularDependency(BaseTestClass):

    def test_circular_dependency(self):
        script_path = str(Path(input_scripts_dir)/'circular_dependency.py')
        self._script_executer([script_path])

        self._graph.refresh_graph()
        qt_items = self._graph.get_qt_items()

        assert len(qt_items) == 30

        expected_items_info = [

            # 1st input node and its output signal:
            {
                'type': QGraphicsEllipseItem,
                'children': [
                    {
                        'type': QGraphicsTextItem,
                        'text': '1.0',
                        'children': [],
                    },
                ],
            },
            {
                'type': QGraphicsPathItem,
                'children': [
                    {
                        'type': QGraphicsPolygonItem,
                        'children': [],
                    },
                ],
            },
            
            # 2nd input node and its output signal:
            {
                'type': QGraphicsEllipseItem,
                'children': [
                    {
                        'type': QGraphicsTextItem,
                        'text': '2.0',
                        'children': [],
                    },
                ],
            },
            {
                'type': QGraphicsPathItem,
                'children': [
                    {
                        'type': QGraphicsPolygonItem,
                        'children': [],
                    },
                ],
            },
        ]

        actual_items_info = self._get_qt_items_info(qt_items)

        for expected_item in expected_items_info:
            assert self._is_expected_in_actual_list(expected_item,
                                                    actual_items_info)
            
