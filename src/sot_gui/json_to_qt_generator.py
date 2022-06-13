from typing import Any, Dict, List, Tuple, Union

from json import loads

from PySide2.QtWidgets import (QGraphicsPolygonItem, QGraphicsEllipseItem, QGraphicsItem,
    QGraphicsRectItem, QGraphicsTextItem, QGraphicsPathItem)
from PySide2.QtGui import QPolygonF, QPainterPath, QBrush, QColor
from PySide2.QtCore import QRectF, QPointF

from sot_gui.utils import (get_dict_with_element, get_dicts_with_element,
    get_dict_with_element_in_list, get_dicts_with_element_in_list)


# Documentation on dot's json output:
# https://graphviz.org/docs/outputs/json/


class JsonParsingUtils:
    """ This is a helper class for parsing the dot's json output. """

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
    TAIL_LABEL_DRAW = '_tldraw_'

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


    def get_data_by_key_value(dict_list: List[Dict], key: str, values: Union[Any, List[Any]]) \
            -> Dict:
        """ From the dictionary list, returns the first one whose key/value pair corresponds
            to the given arguments, or None if none was found. `values` can be a single element
            or a list of possible values.
        """
        if isinstance(values, list):
            return get_dict_with_element_in_list(dict_list, key, values)
        else:
            return get_dict_with_element(dict_list, key, values)


    def get_data_list_by_key_value(dict_list: List[Dict], key: str, values:
            Union[Any, List[Any]]) -> List[Dict]:
        """ From the dictionary list, returns those whose key/value pairs correspond
            to the given arguments, or None if none was found. `values` can be a single
            element or a list of possible values.
        """
        if isinstance(values, list):
            return get_dicts_with_element_in_list(dict_list, key, values)
        else:
            return get_dicts_with_element(dict_list, key, values)


j = JsonParsingUtils


class JsonToQtGenerator:
    """ When given dot's json output as a string, this class can generate qt items
        for nodes, ports and edges.
    """

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
            # j.T_POLYLINE[0]: self._generate_rectangle,
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
        """ Generates and returns a qt item for the node named `node_name` in the dot
            code used to generate the json output.
            The qt item will be the node's body (i.e shape OR html table) as the parent
            QGraphicsItem, which will contain the node label as a child item (only if the
            body is a shape).
            All those items' positions will be set before return.
            If the node's style was set to invisible, this method will return None.
        """
        # Getting the node whose name is `node_name`:
        node = j.get_data_by_key_value(self._graph_data[j.OBJECTS], j.NAME, node_name)
        if node is None:
            raise ValueError(f"Node {node_name} could not be found in dot's json output.")
        
        if node.get(j.STYLE) == 'invis': # If the node is invisible
            return None

        # Creating the node's body (node = (shape + label) OR html table):
        qt_item_body = None

        # If the node has a shape, we add the label as its child:
        if j.BODY_DRAW in node:
            qt_item_shape = self._get_node_shape(node[j.BODY_DRAW])
            qt_item_body = qt_item_shape
            # Adding the node's label:
            label = self._get_label(node[j.LABEL_DRAW])
            label.setParentItem(qt_item_body)

        else:
            # If the node has no shape, its body is an html table.
            # No label has to be added, as the table is technically the label.
            qt_item_html_table = self._get_node_html_table(node[j.LABEL_DRAW])
            qt_item_body = qt_item_html_table


        return qt_item_body


    def get_qt_item_for_edge(self, head_name: str, tail_name: str) -> QGraphicsItem:
        """ Generates and returns a qt item for the edge linked to the nodes named
            `head_name` and `tail_name` in the dot code used to generate the json output.
            The qt item will be the edge's body (i.e the spline) as the parent
            QGraphicsItem, which will contain the labels as a child items.
            All those items' positions will be set before return.
            If the edge's style was set to invisible, this method will return None.
        """
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

        # Getting the labels (label, headlabel, taillabel):
        for label_type in [j.LABEL_DRAW, j.HEAD_LABEL_DRAW, j.TAIL_LABEL_DRAW]:
            label_data = edge_data.get(label_type)
            if label_data is not None:
                label = self._get_label(label_data)
                label.setParentItem(curve)
        
        return curve


    def _get_node_shape(self, body_data: List[Dict]) -> QGraphicsItem:
        """ Generates and returns a qt item for a node's shape, with its position set.
            Returns None if the node has no shape.
        """
        # If the node has no shape:
        if body_data is None:
            return None

        # Getting the body's shape type and data (polygon or ellipse):
        shape_data = j.get_data_by_key_value(body_data, j.TYPE, j.T_POLYGON + j.T_ELLIPSE)
        if shape_data is None:
            return None
        shape_type = shape_data[j.TYPE]

        # Generating the shape:
        qt_item_body = self._qt_generator_per_type[shape_type](shape_data)
        return qt_item_body


    def _get_node_html_table(self, table_data: List[Dict]) -> QGraphicsItem:
        """ Generates and returns a qt item for a node's html table. The qt item consists
            of the table's outline as the parent item, containing every cell's outline which
            contain the cell's label. The position of each item is set in this method.
            Raises a RuntimeError if the table could not be generated due to missing data.
        """

        # Getting the polygons and labels data lists:
        display_data = self._get_html_table_data_lists(table_data)

        if len(display_data) == 0:
            raise RuntimeError('JsonToQtGenerator._get_node_html_table: not enough' +
            " elements in node's label json data.")

        # Creating each cell. The middle column will be the parent (qt_item_node),
        # as it represents the node's body, and the side columns are the ports:
        qt_item_node = None
        for idx, (cell_outline_data, cell_label_data) in enumerate(display_data):
            cell_qt_item = self._get_html_table_cell(cell_outline_data, cell_label_data)
            if idx == 1:
                # During the dot code generation, the middle cell is always created 2nd
                qt_item_node = cell_qt_item
            else:
                # If it's a port's qt item
                cell_qt_item.setParentItem(qt_item_node)
        
        # TODO: make the node's middle the parent item, and the ports the children

        return qt_item_node


    def _get_html_table_cell(self, outline_data: List[Dict], label_data: List[Dict]) \
            -> QGraphicsItem:
        """ Generates and returns qt items for a node's html table's cell,
            with their positions set. The outline will be the parent item, containing
            the label.
        """

        # Generating the outline:
        polygon_data = j.get_data_by_key_value(outline_data, j.TYPE, j.T_POLYGON)
        cell_outline = self._generate_polygon(polygon_data)

        # Generating the label:
        cell_label = self._get_label(label_data)
        cell_label.setParentItem(cell_outline)

        return cell_outline
        

    def _get_html_table_data_lists(self, table_data: List[Dict]) -> List[Tuple[List[Dict]]]:
        """ Goes through a list of dictionaries corresponding to a node's html table
            display data (table outline, cells' outlines and cells' labels), and returns
            a list of every cell's display data.
            The display data for a cell is a tuple. Its first element is a list of the
            outline's data dictionaries, and its second element is a list of the label's
            data dictionaries.
        """
        table_data_list = []

        # For each cell, we get its outline's data and its label's data:
        cell_outline = []
        cell_label = []
        current_data_is_outline = True # Each cell data sequence is: outline, then label
        for data in table_data:
            if current_data_is_outline:
                cell_outline.append(data)
                # A label's data sequence ends with its text:
                if data[j.TYPE] in j.T_POLYGON:
                    current_data_is_outline = False

            else:
                cell_label.append(data)
                # An outline's data sequence ends with the coords of its vertices:
                if data[j.TYPE] in j.T_TEXT:
                    current_data_is_outline = True
                    table_data_list.append((cell_outline, cell_label))
                    cell_outline = []
                    cell_label = []

        return table_data_list


    def _get_edge_body(self, edge_data: Dict[str, Any]) -> QGraphicsItem:
        """ Generates and returns qt items for an edge's body based on the given data,
            with their positions set.
            The body consists of the edge's spline, and its head.
        """

        # Getting the spline:
        spline_data = j.get_data_by_key_value(edge_data.get(j.BODY_DRAW), j.TYPE, j.T_SPLINE)
        if spline_data is None or spline_data.get(j.POINTS) is None:
            return None
        curve = self._generate_spline(spline_data.get(j.POINTS))
        # TODO: add an additional path to QPainterPath if there are several bezier curves

        # Getting the head and setting the curve as its parent:
        head_data = j.get_data_by_key_value(edge_data.get(j.HEAD_DRAW), j.TYPE, j.T_POLYGON)
        if head_data is not None and head_data.get(j.POINTS) is not None:
            head = self._generate_polygon(head_data)
            head.setBrush(QBrush(QColor("black"))) # Filling it with black
            head.setParentItem(curve)

        return curve


    def _get_label(self, label_data: List[Dict]) -> QGraphicsItem:
        """ Generates and returns qt items for a label based on the given data,
            with their positions set.
        """

        # Getting the text:
        text_data = j.get_data_by_key_value(label_data, j.TYPE, j.T_TEXT)
        qt_item_label = self._generate_text(text_data)

        # Getting the font info:
        font_data = j.get_data_by_key_value(label_data, j.TYPE, j.T_FONT)

        # Setting its position:
        dot_coords = (text_data[j.TEXT_POS][0], text_data[j.TEXT_POS][1])
        qt_coords = self._dot_coords_to_qt_coords(dot_coords)
        position = QPointF(
            qt_coords[0] - text_data[j.WIDTH] / 2,
            qt_coords[1] - font_data[j.FONT_SIZE]
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


    def _get_node_id_per_name(self, name: str) -> int:
        node = j.get_data_by_key_value(self._graph_data[j.OBJECTS], j.NAME, name)
        return node.get(j.ID)


    def _get_edge_per_nodes_names(self, head_name: str, tail_name: str) -> Dict[str, Any]:
        # Retrieving the nodes' IDs:
        head_id = self._get_node_id_per_name(head_name)
        tail_id = self._get_node_id_per_name(tail_name)

        # Getting the edges whose heads are `head_name`:
        all_edges = self._graph_data[j.EDGES]
        edges_with_correct_head = j.get_data_list_by_key_value(all_edges, j.HEAD_ID, head_id)

        # Among these edges, finding the one whose tail is `tail_name`:
        edge = j.get_data_by_key_value(edges_with_correct_head, j.TAIL_ID, tail_id)
        return edge
