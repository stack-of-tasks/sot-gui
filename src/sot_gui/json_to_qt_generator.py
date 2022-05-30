from typing import Any, Dict, List, Tuple, Union

from json import loads

from PySide2.QtWidgets import (QGraphicsPolygonItem, QGraphicsEllipseItem, QGraphicsItem,
    QGraphicsRectItem, QGraphicsTextItem, QGraphicsPathItem)
from PySide2.QtGui import QPolygonF, QPainterPath
from PySide2.QtCore import QRectF, QPointF

from sot_gui.utils import (get_dict_with_element, get_dicts_with_element,
    get_dict_with_element_in_list)


# Documentation on dot's json output:
# https://graphviz.org/docs/outputs/json/


class JsonParsingUtils:
    # Keys for lists of clusters, nodes and edges:
    OBJECTS = 'objects' # nodes and clusters
    EDGES = 'edges'
    CLUSTER_NODES = 'nodes'
    CLUSTER_EDGES = 'edges'

    # Keys for nodes, clusters and edges' identification:
    ID = '_gvid'
    NAME = 'name'
    HEAD_ID = 'head'
    TAIL_ID = 'tail'

    # Keys for display data of nodes and edges' parts:
    BODY_DRAW = '_draw_'
    HEAD_DRAW = '_hdraw_'
    TAIL_DRAW = '_tdraw_'
    LABEL_DRAW = '_ldraw_'
    HEAD_LABEL_DRAW = '_hldraw_'
    TAIL_LABEL_DRAW = 'tldraw__'

    # Keys for displayed elements' attributes:
    TYPE = 'op' # Type of the json data object
    DIMENSIONS = 'bb' # Bounding box of the graph or a cluster
    WIDTH = 'width'
    HEIGHT = 'height'
    POINTS = 'points'
    RECT = 'rect' # Ellipse's rectangle
    STYLE = 'style'
    COLOR = 'color'
    TEXT = 'text'
    TEXT_POS = 'pt'
    FONT = 'face'
    FONT_SIZE = 'size'

    # Possible values for json data objects' types (TYPE):
    T_STYLE = ['S']
    T_COLOR = ['c', 'C']
    T_FONT = ['F']
    T_TEXT = ['t', 'T']
    T_POLYGON = ['p', 'P']
    T_ELLIPSE = ['e', 'E']
    T_SPLINE = ['b', 'B']
    T_POLYLINE = ['L']

j = JsonParsingUtils


class JsonToQtGenerator:
    """ """

    def __init__(self, json_string: str):
        self._qt_generator_per_type = {
            # j.T_STYLE[0]: self._generate_rectangle,
            # j.T_COLOR[0] self._generate_rectangle,
            # j.T_COLOR[1]: self._generate_rectangle,
            # j.T_FONT[0]: self._generate_rectangle,
            j.T_TEXT[0]: self._generate_text,
            j.T_TEXT[1]: self._generate_text,
            j.T_POLYGON[0]: self._generate_polygon,
            j.T_POLYGON[1]: self._generate_polygon,
            j.T_ELLIPSE[0]: self._generate_ellipse,
            j.T_ELLIPSE[1]: self._generate_ellipse,
            j.T_SPLINE[0]: self._generate_spline,
            j.T_SPLINE[1]: self._generate_spline,
            # j.T_POLYGON[0]: self._generate_rectangle,
        }

        self._graph_data: Dict[str, Any] = loads(json_string)

        # Getting the graph's dimensions:
        bounding_box = [ float(str) for str in self._graph_data[j.DIMENSIONS].split(',') ]
        self._graph_bounding_box = {
            'x': bounding_box[0],
            'y': bounding_box[1],
            'width': bounding_box[2],
            'height': bounding_box[3]
        }


    #
    # Nodes and edges generation
    #

    def get_qt_item_for_node(self, node_name: str) -> QGraphicsItem:
        # Getting the node whose name is `node_name`:
        node = get_dict_with_element(self._graph_data[j.OBJECTS], j.NAME, node_name)
        if node is None:
            raise ValueError(f"Node {node_name} could not be found in dot's json output.")
        
        if node.get(j.STYLE) == 'invis': # If the node is invisible
            return None

        # Creating the node's body (node = body + label):
        qt_item_body = self._get_node_body(node[j.BODY_DRAW])

        # Creating the node's label, with the node's shape as parent:
        label = self._get_label(node[j.LABEL_DRAW])
        label.setParentItem(qt_item_body)

        return qt_item_body


    def get_qt_item_for_edge(self, head_name: str, tail_name: str) -> QGraphicsItem:
        # Getting the edge's display info:
        edge_data = self._get_edge_per_nodes_names(head_name, tail_name)
        if edge_data is None:
            raise ValueError(f"Could not find edge with tail {tail_name} and head\
                {head_name}.")

        if edge_data.get(j.STYLE) == 'invis': # If the edge is invisible
            return None

        # Getting the edge's curve, and the tail and head as its children:
        curve = self._get_edge_body(edge_data)
        if curve is None:
            return None

        # Getting the labels:
        for label_type in [j.LABEL_DRAW, j.HEAD_LABEL_DRAW, j.TAIL_LABEL_DRAW]:
            label_data = edge_data.get(label_type)
            if label_data is not None:
                label = self._get_label(label_data)
                label.setParentItem(curve)
        
        return curve


    def _get_node_body(self, body_data: List[Dict]) -> QGraphicsItem:
        # Getting the body's shape:
        shape_data = get_dict_with_element_in_list(body_data, j.TYPE,
                j.T_POLYGON + j.T_ELLIPSE)
        shape_type = shape_data[j.TYPE]
        qt_item_body = self._qt_generator_per_type[shape_type](shape_data)
        return qt_item_body


    def _get_edge_body(self, edge_data: Dict[str, Any]) -> QGraphicsItem:
        # Getting the spline:
        spline_data = get_dict_with_element_in_list(edge_data.get(j.BODY_DRAW),
                j.TYPE, j.T_SPLINE)
        if spline_data is None or spline_data.get(j.POINTS) is None:
            return None
        curve = self._generate_spline(spline_data.get(j.POINTS))
        # TODO: add an additional path to QPainterPath if there are several bezier curves

        # Getting the head and setting the curve as its parent:
        head_data = get_dict_with_element_in_list(edge_data.get(j.HEAD_DRAW),
                j.TYPE, j.T_POLYGON)
        if head_data is not None and head_data.get(j.POINTS) is not None:
            head = self._generate_polygon(head_data)
            head.setParentItem(curve)

        return curve


    def _get_label(self, label_data: List[Dict]) -> QGraphicsItem:
        # Getting the text:
        text_data = get_dict_with_element_in_list(label_data, j.TYPE, j.T_TEXT)
        qt_item_label = self._generate_text(text_data)

        # Getting the font info:
        font_data = get_dict_with_element_in_list(label_data, j.TYPE, j.T_FONT)

        # Setting its position:
        position = QPointF(
            text_data[j.TEXT_POS][0] - text_data[j.WIDTH] / 2,
            text_data[j.TEXT_POS][1] - font_data[j.FONT_SIZE] / 2
        )
        qt_item_label.setPos(position)

        return qt_item_label


    #
    # Basic `QGraphicsItem`s generation
    #

    def _generate_polygon(self, data: Dict[str, Any]) -> QGraphicsPolygonItem:
        polygon = QPolygonF()

        # Adding each of the polygon's points:
        for point in data[j.POINTS]:
            qt_coord = self._dot_coords_to_qt_coords((point[0], point[1]))
            polygon.append(QPointF(qt_coord[0], qt_coord[1]))
        
        polygonItem = QGraphicsPolygonItem(polygon)
        return polygonItem


    def _generate_rectangle(self, data: Dict[str, Any]) -> QGraphicsRectItem:
        # TODO
        rect = QGraphicsRectItem(0, 0, 10, 10)
        return rect


    def _generate_ellipse(self, data: Dict[str, Any]) -> QGraphicsEllipseItem:
        # Gettings the ellipse's rectangle's dimensions:
        rect_data = data[j.RECT]
        width = rect_data[2] * 2
        height = rect_data[3] * 2

        # Getting its coords:
        dot_coords = (rect_data[0] - width / 2, rect_data[1] + height / 2)
        qt_coords = self._dot_coords_to_qt_coords(dot_coords)

        # Creating the ellipse:
        rect = QRectF(qt_coords[0], qt_coords[1], width, height)
        ellipse = QGraphicsEllipseItem(rect)
        return ellipse


    def _generate_text(self, data: Dict[str, Any]) -> QGraphicsTextItem:
        #font = QFont('Times', 14)
        text = QGraphicsTextItem(data[j.TEXT])
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


    #
    # Utils
    # 

    def _dot_coords_to_qt_coords(self, coords: Tuple[float, float]) -> Tuple[float, float]:
        """ Converts dot coordinates (origin on the bottom-left corner) to Qt
            coordinates (origin on the top-left corner).
        """
        (x_coord, y_coord) = coords
        return (x_coord, self._graph_bounding_box['height'] - y_coord)


    def _get_node_gvid_per_name(self, name: str) -> int:
        node = get_dict_with_element(self._graph_data[j.OBJECTS], j.NAME, name)
        return node.get(j.ID)


    def _get_edge_per_nodes_names(self, head_name: str, tail_name: str) -> Dict[str, Any]:
        # Retrieving the nodes' _gvid IDs:
        head_id = self._get_node_gvid_per_name(head_name)
        tail_id = self._get_node_gvid_per_name(tail_name)

        # Getting the edges whose heads are `head_name`:
        all_edges = self._graph_data[j.EDGES]
        edges_with_correct_head = get_dicts_with_element(all_edges, j.HEAD_ID, head_id)

        # Among these edges, finding the one whose tail is `tail_name`:
        correct_edges = get_dicts_with_element(edges_with_correct_head, j.TAIL_ID, tail_id)
        if correct_edges == []:
            return None
        edge = correct_edges[0]
        return edge
