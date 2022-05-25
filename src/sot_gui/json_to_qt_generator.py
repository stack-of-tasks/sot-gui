from typing import Any, Dict, List, Tuple

from json import loads

from PySide2.QtWidgets import (QGraphicsPolygonItem, QGraphicsEllipseItem, QGraphicsItem,
    QGraphicsRectItem, QGraphicsSimpleTextItem)
from PySide2.QtGui import QPolygonF
from PySide2.QtCore import QRectF, QPointF

from sot_gui.utils import filter_dicts_per_attribute


class JsonToQtGenerator:
    """ """

    def __init__(self, json_string: str):
        self._qt_generator_for_type = {
            'S': self._temporary_placeholder_function, # Style
            'c': self._temporary_placeholder_function, # Color
            'C': self._temporary_placeholder_function, # Color
            'F': self._temporary_placeholder_function, # Font
            't': self._temporary_placeholder_function, # Font?
            'T': self._generate_text, # Text
            'p': self._generate_polygon,
            'P': self._generate_polygon,
            'e': self._temporary_placeholder_function, # Ellipse
            'E': self._temporary_placeholder_function, # Ellipse
            'b': self._temporary_placeholder_function, # Bezier spline
            'B': self._temporary_placeholder_function, # Bezier spline
            'L': self._temporary_placeholder_function, # Polyline
        }

        # https://graphviz.org/docs/outputs/json/
        self._graph_data: Dict[str, Any] = loads(json_string)

        # Getting the graph's dimensions:
        bounding_box = [ float(str) for str in self._graph_data['bb'].split(',') ]
        self._graph_bounding_box = {
            'x': bounding_box[0],
            'y': bounding_box[1],
            'width': bounding_box[2],
            'height': bounding_box[3]
        }


    def get_qt_items_for_node(self, node_name: str) -> List[QGraphicsItem]:
        # Getting the node whose name is `node_name`:
        nodes = filter_dicts_per_attribute(self._graph_data['objects'], 'name', node_name)
        if len(nodes) == 0:
            raise ValueError(f"Node {node_name} could not be found in dot's json output.")
        node = nodes[0]

        qt_items = []
        # Creating the node's shape:
        for object in node['_draw_']:
            object_type = object['op']
            qt_item = self._qt_generator_for_type[object_type](object)
            qt_items.append(qt_item)

        # Creating the node's label:
        for object in node['_ldraw_']:
            object_type = object['op']
            qt_item = self._qt_generator_for_type[object_type](object)
            qt_items.append(qt_item)

        return qt_items


    def _dot_coords_to_qt_coords(self, coords: Tuple[float, float]):
        """ Converts dot coordinates (origin on the bottom-left corner) to Qt
            coordinates (origin on the top-left corner).
        """
        (x_coord, y_coord) = coords
        return (x_coord, self._graph_bounding_box['height'] - y_coord)


    def _generate_polygon(self, data: Dict[str, Any]) -> QGraphicsPolygonItem:
        # TODO: add color
        polygon = QPolygonF()

        # Adding each of the polygon's points:
        for point in data['points']:
            qt_coord = self._dot_coords_to_qt_coords((point[0], point[1]))
            polygon.append(QPointF(qt_coord[0], qt_coord[1]))
        
        polygonItem = QGraphicsPolygonItem(polygon)
        return polygonItem


    def _generate_text(self, data: Dict[str, Any]) -> QGraphicsSimpleTextItem:
        # TOOD: add color, font, etc
        return QGraphicsSimpleTextItem(data['text'])


    def _temporary_placeholder_function(self, _) -> QGraphicsRectItem:
        return QGraphicsRectItem(0, 0, 10, 10)




# Rectangle
# rect = QGraphicsRectItem(0, 0, 60, 160)

# Polygon
# polygon = QPolygonF()
# polygon.append(QPointF(0, 0))
# polygon.append(QPointF(20, 20))
# polygon.append(QPointF(30, 50))
# polygonItem = QGraphicsPolygonItem(polygon)

# Ellipse / circle
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