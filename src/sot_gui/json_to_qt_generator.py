from typing import Any, Dict, List, Tuple, Union

from json import loads

from PySide2.QtWidgets import (QGraphicsPolygonItem, QGraphicsEllipseItem, QGraphicsItem,
    QGraphicsRectItem, QGraphicsTextItem, QGraphicsPathItem)
from PySide2.QtGui import QPolygonF, QPainterPath
from PySide2.QtCore import QRectF, QPointF

from sot_gui.utils import (get_dict_with_element, get_dicts_with_element,
    get_dict_with_element_in_list)


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
            'e': self._generate_ellipse, # Ellipse
            'E': self._generate_ellipse, # Ellipse
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


    def get_qt_item_for_node(self, node_name: str) -> QGraphicsItem:
        # Getting the node whose name is `node_name`:
        node = get_dict_with_element(self._graph_data['objects'], 'name', node_name)
        if node is None:
            raise ValueError(f"Node {node_name} could not be found in dot's json output.")
        if node.get('style') == 'invis': # If the node is invisible
            return []

        # Creating the node's body (node = body + label):
        qt_item_body = self._get_node_body(node['_draw_'])

        # Creating the node's label, with the node's shape as parent:
        label = self._get_label(node['_ldraw_'])
        label.setParentItem(qt_item_body)

        return qt_item_body


    def get_qt_item_for_edge(self, head_name: str, tail_name: str) -> QGraphicsItem:
        # Getting the edge's display info:
        edge = self._get_edge_per_nodes_names(head_name, tail_name)

        # Drawing the spline:
        spline_data = get_dict_with_element_in_list(edge.get('_draw_'), 'op', ['b', 'B'])
        if spline_data is None or spline_data.get('points') is None:
            return
        curve = self._generate_spline(spline_data.get('points'))
        # TODO: add an additional path to QPainterPath if there are several bezier curves

        # Drawing the head and setting the curve as its parent:
        # head_data = get_dict_with_element_in_list(edge.get('_hdraw_'), 'op', ['p', 'P'])
        # if head_data is not None:
        #     head = self._get_edge_head(head_data)
        #     head.setParentItem(curve)
        
        return curve


    def _get_node_body(self, body_data: List[Dict]) -> QGraphicsItem:
        # Getting the body's shape:
        shape_data = get_dict_with_element_in_list(body_data, 'op',
                ['p', 'P', 'e', 'E'])
        shape_type = shape_data['op']
        qt_item_body = self._qt_generator_for_type[shape_type](shape_data)
        return qt_item_body


    def _get_label(self, label_data: List[Dict]) -> QGraphicsItem:
        # Getting the text:
        text_data = get_dict_with_element(label_data, 'op', 'T')
        qt_item_label = self._generate_text(text_data)

        # Getting the font info:
        font_data = get_dict_with_element(label_data, 'op', 'F')

        # Setting its position:
        position = QPointF(
            text_data['pt'][0] - text_data['width'] / 2,
            text_data['pt'][1] - font_data['size'] / 2
        )
        qt_item_label.setPos(position)

        return qt_item_label


    def _generate_polygon(self, data: Dict[str, Any]) -> QGraphicsPolygonItem:
        polygon = QPolygonF()

        # Adding each of the polygon's points:
        for point in data['points']:
            qt_coord = self._dot_coords_to_qt_coords((point[0], point[1]))
            polygon.append(QPointF(qt_coord[0], qt_coord[1]))
        
        polygonItem = QGraphicsPolygonItem(polygon)
        return polygonItem


    def _generate_ellipse(self, data: Dict[str, Any]) -> QGraphicsEllipseItem:
        # Gettings the ellipse's rectangle's dimensions:
        width = data['rect'][2] * 2
        height = data['rect'][3] * 2

        # Getting its coords:
        dot_coords = (data['rect'][0] - width / 2, data['rect'][1] + height / 2)
        qt_coords = self._dot_coords_to_qt_coords(dot_coords)

        # Creating the ellipse:
        rect = QRectF(qt_coords[0], qt_coords[1], width, height)
        ellipse = QGraphicsEllipseItem(rect)
        return ellipse


    def _generate_text(self, data: Dict[str, Any]) -> QGraphicsTextItem:
        #font = QFont('Times', 14)
        text = QGraphicsTextItem(data['text'])
        #text.setFont(font)
        return text


    def _generate_spline(self, data: Dict[str, Any]) -> QGraphicsPathItem:
        # Getting the points' qt coordinates:
        coordsQt = []
        for point in data:
           coordsQt.append(self._dot_coords_to_qt_coords((point[0], point[1])))

        path = QPainterPath()

        # Setting the first point:
        path.moveTo(coordsQt[0][0], coordsQt[0][1])
        # Setting the 3 next points:
        path.cubicTo(coordsQt[1][0], coordsQt[1][1], coordsQt[2][0], coordsQt[2][1],
            coordsQt[3][0], coordsQt[3][1])

        curve = QGraphicsPathItem(path)
        return curve


    def _temporary_placeholder_function(self, _) -> QGraphicsRectItem:
        return QGraphicsRectItem(0, 0, 10, 10)


    def _dot_coords_to_qt_coords(self, coords: Tuple[float, float]) -> Tuple[float, float]:
        """ Converts dot coordinates (origin on the bottom-left corner) to Qt
            coordinates (origin on the top-left corner).
        """
        (x_coord, y_coord) = coords
        return (x_coord, self._graph_bounding_box['height'] - y_coord)


    def _get_node_gvid_per_name(self, name: str) -> int:
        node = get_dict_with_element(self._graph_data['objects'], 'name', name)
        return node.get('_gvid')


    def _get_edge_per_nodes_names(self, head_name: str, tail_name: str) -> Dict[str, Any]:
        # Retrieving the nodes' _gvid IDs:
        head_gvid = self._get_node_gvid_per_name(head_name)
        tail_gvid = self._get_node_gvid_per_name(tail_name)

        # Getting the edges whose heads are `head_name`:
        all_edges = self._graph_data['edges']
        edges_with_correct_head = get_dicts_with_element(all_edges, 'head', head_gvid)

        # Among these edges, finding the one whose tail is `tail_name`:
        correct_edges = get_dicts_with_element(edges_with_correct_head, 'tail', tail_gvid)
        if correct_edges == []:
            raise ValueError(f"Could not find edge with tail {tail_name} and head\
                {head_name}.")
        edge = correct_edges[0]
        return edge



# Rectangle
# rect = QGraphicsRectItem(0, 0, 60, 160)


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