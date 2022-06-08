from __future__ import annotations # To prevent circular dependencies of annotations
from typing import List, Any, Dict
from subprocess import Popen, PIPE
from copy import deepcopy

from PySide2.QtWidgets import QGraphicsItem

from sot_gui.dynamic_graph_communication import DynamicGraphCommunication
from sot_gui.dot_data_generator import DotDataGenerator
from sot_gui.json_to_qt_generator import JsonToQtGenerator
from sot_gui.utils import quoted


class Node:
    """  """
    def __init__(self):
        self._name: str = None
        self._type: str = None
        self._inputs: List[self.Port] = None
        self._outputs: List[self.Port] = None
        self._qt_items: List[QGraphicsItem] = None


    def name(self) -> str:
        return self._name


    def type(self) -> str:
        return self._type
    def set_type(self, type: str) -> None:
        self._type = type


    def qt_items(self) -> List[QGraphicsItem]:
        if self._qt_items is not None:
            return self._qt_items.copy()
        return []
    def set_qt_items(self, qt_items: List[QGraphicsItem]) -> None:
        self._qt_items = qt_items


    def inputs(self) -> List[Port]:
        if self._inputs is not None:
            return self._inputs.copy()
        return []


    def outputs(self) -> List[Port]:
        if self._outputs is not None:
            return self._outputs.copy()
        return []


    def add_port(self, name: str, type: str) -> Port:
        new_port = self.Port(name, type, self)
        if type == 'input':
            self._inputs.append(new_port)
        elif type == 'output':
            self._outputs.append(new_port)
        else:
            raise ValueError("Port type must be either 'input' or 'output'")
        return new_port


    def set_edge_for_port(self, edge: Edge, port_name: str) -> None:
        port = self._get_port_per_name(port_name)
        if port is None:
            raise ValueError(f"Port {port_name} of node {self._name} does not exist.")
        port.set_edge(edge)


    def _get_port_per_name(self, name: str) -> Port | None:
        for port in self._inputs + self._outputs:
            if port.name() == name:
                return port
        return None

    
    class Port:
        def __init__(self, name: str, type: str, node: Node):
            self._qt_items: List[QGraphicsItem] = []
            self._edge = None
            self._name = name
            self._type = type # 'input' or 'output'
            self._node = node


        def name(self) -> str:
            return self._name


        def type(self) -> str:
            return self._type


        def qt_items(self) -> List[QGraphicsItem]:
            if self._qt_items is not None:
                return self._qt_items.copy()
            return []
        def set_qt_items(self, qt_items: List[QGraphicsItem]) -> None:
            self._qt_items = qt_items


        def node(self) -> str:
            return self._node


        def edge(self) -> str:
            return self._edge
        def set_edge(self, edge: Edge) -> str:
            self._edge = edge
            if self._type == 'input':
                edge.set_head(self)
            elif self._type == 'output':
                edge.set_tail(self)
            else:
                raise ValueError("Port type must be either 'input' or 'output'")


class InputNode(Node):
    _input_node_count = 0

    def __init__(self, output_edge: Edge):
        # TODO: generate name with name of child node + corresponding plug?
        self._qt_items = []
        self._type = output_edge.value_type()

        self._name = f"InputNode{InputNode._input_node_count}"
        InputNode._input_node_count += 1

        output_port = self.Port("sout0", 'output', self)
        output_port.set_edge(output_edge)
        self._outputs = [output_port]


class EntityNode(Node):
    def __init__(self, name: str, type: str = None):
        self._name = name
        self._type = type
        self._inputs = []
        self._outputs = []
        self._qt_items = []


class Edge:
    def __init__(self, value: Any = None, value_type: str = None,
                head: Node.Port = None, tail: Node.Port = None):
        self._qt_items: List[QGraphicsItem] = []
        self._value = value
        self._value_type = value_type
        self._head = head
        self._tail = tail


    def name(self) -> str:
        return self._name


    def value(self) -> Any:
        return self._value


    def value_type(self) -> str:
        return self._value_type
    def set_value_type(self, value_type: str) -> None:
        self._value_type = value_type


    def qt_items(self) -> List[QGraphicsItem]:
        if self._qt_items is not None:
            return self._qt_items.copy()
        return []
    def set_qt_items(self, qt_items: List[QGraphicsItem]) -> None:
        self._qt_items = qt_items


    def head(self) -> Node.Port:
        return self._head
    def set_head(self, head: Node.Port) -> None:
        self._head = head


    def tail(self) -> Node.Port:
        return self._tail
    def set_tail(self, tail: Node.Port) -> None:
        self._tail = tail


class Graph:
    """ This class holds the graph's information: it gets the dynamic graph's
        entities and signals, and generates their corresponding PySide items.
    """

    def __init__(self):
        self._dg_communication = DynamicGraphCommunication()

        # Entities that exist in the dynamic graph:
        self._dg_entities: List[EntityNode] = []
        # Input nodes that don't exist in the dynamic graph:
        self._input_nodes: List[InputNode] = []
        # Information about the graph as a whole (name, dimensions, background color...):
        self._graph_info: Dict[str, Any] = {}


    def graph_info(self) -> Dict[str, Any]:
        return deepcopy(self._graph_info)


    def _get_node_per_name(self, name: str) -> Node | None:
        for node in self._dg_entities + self._input_nodes:
            if node.name() == name:
                return node
        return None


    def _get_dg_data(self) -> None:
        # Gettings every entity:
        entities_names = self._dg_communication.get_all_entities_names()
        if entities_names is None:
            return

        # For each entity, we will store its signals' infos to create edges later
        # (they have to be created after all ports have been created):
        entities_plugs_infos: Dict[EntityNode, List[str]] = {}

        for name in entities_names:
            # Creating the node:
            type = self._dg_communication.get_entity_type(name)
            new_node = EntityNode(name, type)
            self._dg_entities.append(new_node)

            # Creating the node's ports:
            entities_plugs_infos[new_node] = []
            sig_descriptions = self._dg_communication.get_entity_signals(name)
            for sig_description in sig_descriptions:
                plug_info = self._parse_signal_description(sig_description)
                if plug_info is None:
                    continue
                # Storing this plug's info:
                entities_plugs_infos[new_node].append(plug_info)
                # Adding this port to the node:
                new_node.add_port(plug_info['name'], plug_info['type'])

        # Linking the ports with edges:
        for (node, plugs_infos) in entities_plugs_infos.items():
            for plug_info in plugs_infos:
                # Creating the edge that will be plugged to this port:
                # We only handle input signals to prevent creating an edge twice
                if plug_info['type'] == 'input':
                    self._add_signal_to_dg_data(plug_info, node)


    def _add_signal_to_dg_data(self, plug_info: Dict[str, str], child_node: Node) -> None:
        sig_name = plug_info['name']
        child_node_name = child_node.name()

        # Getting the description of the plug this signal is plugged to, 
        # i.e an output signal of the parent entity:
        is_plugged = self._dg_communication.is_signal_plugged(child_node_name, sig_name)
        if not is_plugged:
            return
        linked_plug_descr = self._dg_communication.get_linked_plug(child_node_name, sig_name)
        if linked_plug_descr is None: # If the node doesn't have a parent node
            return
        linked_plug_info = self._parse_signal_description(linked_plug_descr)

        signal_value = self._dg_communication.get_signal_value(child_node_name, sig_name)
        new_edge = Edge(signal_value, plug_info['value_type'])

        # Linking the signal to the child port:
        child_node.set_edge_for_port(new_edge, plug_info['name'])

        # If the signal is autoplugged (i.e has a fixed value instead of
        # being plugged to a another entity), the entity will appear as
        # linked to itself through this signal
        if child_node_name == linked_plug_info['entity_name']:
            # If the signal is autoplugged, we add an InputNode to the graph
            # to represent the input value
            new_node = InputNode(new_edge)
            self._input_nodes.append(new_node)
        else:
            # If the signal is not autoplugged, we link it to the parent entity
            parent_entity = self._get_node_per_name(linked_plug_info['entity_name'])
            parent_entity.set_edge_for_port(new_edge, linked_plug_info['name'])


    def _parse_signal_description(self, signal_description: str) -> Dict[str, str] | None:
        """ Parses a signal's description (e.g
            `'Add_of_double(add1)::input(double)::sin0'`) and returns a
            dictionary containing its information:
            - `name`: e.g `'sin0'`
            - `type`: `'input'` or `'output'`
            - `value_type`: type of the signal's value (e.g `'double'`)
            - `entity_name`: name of the entity plugged to the signal
            - `entity_type`: class name of the entity plugged to the
              signal (e.g `'Add_of_double'`)
        """
        try:
            split_description = signal_description.split("::")
            return dict(
                entity_type = split_description[0].split('(')[0],
                entity_name = split_description[0].split('(')[1].split(')')[0],
                type = split_description[1].split('(')[0],
                value_type = split_description[1].split('(')[1].split(')')[0],
                name = split_description[2]
            )
        except:
            print(f"Cannot handle signal: {signal_description}")
            return None


    def _get_encoded_dot_code(self) -> bytes:
        dot_generator = DotDataGenerator()
        dot_generator.set_graph_attributes({'rankdir': quoted('LR')})

        # Adding the input nodes:
        dot_generator.set_node_attributes({'shape': 'circle'})
        for node in self._input_nodes:
            output_ports = node.outputs()
            if len(output_ports) != 1:
                raise ValueError("An InputNode should have exactly one output.")
            output_value = output_ports[0].edge().value()
            dot_generator.add_node(node.name(), {'label': output_value})

        # Adding the dynamic graph entities' nodes and their input edges:
        dot_generator.set_node_attributes({'shape': 'box'})
        for entity in self._dg_entities:
            dot_generator.add_node(entity.name(), {'label': quoted(entity.name())})

            input_edges = [ port.edge() for port in entity.inputs() ]
            for edge in input_edges:
                if edge is None:
                    continue
                parent_node_name = edge.tail().node().name()
                # The value is displayed only if the parent node isn't an InputNode:
                attributes = None
                if isinstance(self._get_node_per_name(parent_node_name), EntityNode):
                    attributes = {'label': edge.value()}
                dot_generator.add_edge(parent_node_name, entity.name(), attributes)

        return dot_generator.get_encoded_dot_string()


    def _generate_qt_items(self) -> None:
        """ For each Node, Port and Edge, this function generates the corresponding
            list of qt items and stores it as their `_qt_items` attribute.
        """
        encoded_dot_code = self._get_encoded_dot_code()
        #print(encoded_dot_code.decode('utf-8'))
        (out, _) = Popen(['dot', '-Tjson'], stdin=PIPE, stdout=PIPE, stderr=PIPE)\
            .communicate(encoded_dot_code)
        #print(out.decode('utf-8'))

        qt_generator = JsonToQtGenerator(out.decode('utf-8'))
        # For every node, we get its qt items:
        for node in self._input_nodes + self._dg_entities:
            qt_item_node = qt_generator.get_qt_item_for_node(node.name())
            node.set_qt_items([qt_item_node]) # TODO: make it a single item?

            if isinstance(node, InputNode):
                continue

            for port in node.inputs():
                edge = port.edge()
                if edge is None:
                    continue
                head_name = edge.head().node().name()
                tail_name = edge.tail().node().name()
                
                qt_item_edge = qt_generator.get_qt_item_for_edge(head_name, tail_name)
                edge.set_qt_items([qt_item_edge])


    def _clear_dg_data(self) -> None:
        self._dg_entities = []
        self._input_nodes = []
        self._graph_info = {}


    def get_qt_items(self) -> List[QGraphicsItem]:
        self._generate_qt_items()
        qt_items = []

        # For each node, we add the qt items of the node, of its ports, and of the
        # port's edge if it's an input (so that edges are not handled twice)
        nodes = self._dg_entities + self._input_nodes
        for node in nodes:
            qt_items += node.qt_items()

            ports = node.outputs()
            if isinstance(node, EntityNode):
                ports += node.inputs()

            for port in ports:
                qt_items += port.qt_items()
                if port.type() == 'input' and port.edge() is not None:
                    qt_items += port.edge().qt_items()

        return qt_items


    def refresh_graph(self):
        """ This function updates the graph by fetching the dynamic graph's data,
            generating a new graph layout with dot and creating the needed qt items.
        """
        self._clear_dg_data()
        self._get_dg_data()
        self._generate_qt_items()


    def reconnect_to_kernel(self):
        """ Create a new connection to the latest kernel. """

        self._dg_communication.reconnect_to_kernel()
