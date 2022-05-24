from typing import Any, Dict

from json import loads

from PyQt5.QtWidgets import QGraphicsPolygonItem, QGraphicsEllipseItem
from PyQt5.QtGui import QPolygonF
from PyQt5.QtCore import QRectF, QPointF


class JsonToQtGenerator:
    """ """

    def __init__(self, json_string: str):
        self._graph_data: Dict[str, Any] = loads(json_string)




# polygon = QPolygonF()
# polygon.append(QPointF(0, 0))
# polygon.append(QPointF(20, 20))
# polygon.append(QPointF(30, 50))
# polygonItem = QGraphicsPolygonItem(polygon)

# rect = QRectF(0, 0, 60, 160)
# ellipse = QGraphicsEllipseItem(rect)
# square = QRectF(0, 0, 60, 60)
# circle = QGraphicsEllipseItem(square)

# return [polygonItem, ellipse, circle]