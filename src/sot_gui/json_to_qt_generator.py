from typing import Any, Dict

from json import loads

from PySide2.QtWidgets import QGraphicsPolygonItem, QGraphicsEllipseItem
from PySide2.QtGui import QPolygonF
from PySide2.QtCore import QRectF, QPointF

from sot_gui.utils import dot_coords_to_qt_coords


class JsonToQtGenerator:
    """ """

    def __init__(self, json_string: str):
        # https://graphviz.org/docs/outputs/json/
        self._graph_data: Dict[str, Any] = loads(json_string)




# Rectangle
# rect = QGraphicsRectItem(0, 0, 60, 160)

# Polygon
# polygon = QPolygonF()
# polygon.append(QPointF(0, 0))
# polygon.append(QPointF(20, 20))
# polygon.append(QPointF(30, 50))
# polygonItem = QGraphicsPolygonItem(polygon)

# Ellipsis / circle
# rect = QRectF(0, 0, 60, 160)
# ellipse = QGraphicsEllipseItem(rect)
# square = QRectF(0, 0, 60, 60)
# circle = QGraphicsEllipseItem(square)

# Text
# text = QGraphicsSimpleTextItem("hello world")

# Curve / straightline
# /!\ Add a path to QPainterPath if there are several bezier curves
# pointsCurve = [[47.510,114.130],[60.020,107.810],[76.800,100.890],[93.580,98.710]]
# pointsStraightLine = [[54.080,72.000],[65.840,72.000],[80.030,72.000],[93.700,72.000]]
# coordsQt = []
# for list in pointsCurve:
#   sceneRect = self.scene.itemsBoundingRect()
#   sceneHeight = sceneRect.height()
#     coordsQt.append(dotCoordsToQtCoords((list[0], list[1]), sceneHeight))
# path = QPainterPath()
# path.moveTo(coordsQt[0][0], coordsQt[0][1])
# path.cubicTo(coordsQt[1][0], coordsQt[1][1], coordsQt[2][0], coordsQt[2][1],
#     coordsQt[3][0], coordsQt[3][1])
# curve = QGraphicsPathItem(path)