from __future__ import annotations # To prevent circular dependencies of annotations
from typing import List, Any, Dict
import subprocess

from PyQt5.QtWidgets import QGraphicsItem # TODO: replace by pyside

from sot_gui.dynamic_graph_communication import DynamicGraphCommunication
from sot_gui.dot_data_generator import DotDataGenerator
from sot_gui.utils import quoted


class Node:
    """  """
    def __init__(self):
        self._name: str = None
        self._type: str = None
        self._inputs: List[self.Port] = None
        self._outputs: List[self.Port] = None
        self._qtItems: List[QGraphicsItem] = None


    def name(self) -> str:
        return self._name


    def type(self) -> str:
        return self._type
    def setType(self, type: str) -> None:
        self._type = type


    def inputs(self) -> List[Port]:
        return self._inputs.copy()


    def outputs(self) -> List[Port]:
        return self._outputs.copy()


    def addPort(self, name: str, type: str) -> Port:
        newPort = self.Port(name, type, self)
        if type == 'input':
            self._inputs.append(newPort)
        elif type == 'output':
            self._outputs.append(newPort)
        else:
            raise ValueError("Port type must be either 'input' or 'output'")
        return newPort


    def setEdgeForPort(self, edge: Edge, portName: str) -> None:
        port = self._getPortPerName(portName)
        if port is None:
            raise ValueError(f"Port {portName} of node {self._name} does not exist.")
        port.setEdge(edge)


    def _getPortPerName(self, name: str) -> Port | None:
        for port in self._inputs + self._outputs:
            if port.name() == name:
                return port
        return None

    
    class Port:
        def __init__(self, name: str, type: str, node: Node):
            self.qtItems: List[QGraphicsItem] = None
            self._edge = None
            self._name = name
            self._type = type # 'input' or 'output'
            self._node = node


        def name(self) -> str:
            return self._name


        def type(self) -> str:
            return self._type


        def node(self) -> str:
            return self._node


        def edge(self) -> str:
            return self._edge
        def setEdge(self, edge: Edge) -> str:
            self._edge = edge
            if self._type == 'input':
                edge.setHead(self)
            elif self._type == 'output':
                edge.setTail(self)
            else:
                raise ValueError("Port type must be either 'input' or 'output'")


class InputNode(Node):
    _inputNodeCount = 0

    def __init__(self, outputEdge: Edge):
        # TODO: generate name with name of child node + corresponding plug?
        self._qtItems = []
        self._type = outputEdge.valueType()

        self._name = f"InputNode{InputNode._inputNodeCount}"
        InputNode._inputNodeCount += 1

        outputPort = self.Port("sout0", 'output', self)
        outputPort.setEdge(outputEdge)
        self._outputs = [outputPort]


class EntityNode(Node):
    def __init__(self, name: str, type: str = None):
        self._name = name
        self._type = type
        self._inputs = []
        self._outputs = []
        self._qtItems = []


class Edge:
    def __init__(self, value: Any = None, valueType: str = None,
                head: Node.Port = None, tail: Node.Port = None):
        self._value = value
        self._valueType = valueType
        self._head = head
        self._tail = tail


    def name(self) -> str:
        return self._name


    def value(self) -> Any:
        return self._value


    def valueType(self) -> str:
        return self._valueType
    def setValueType(self, valueType: str) -> None:
        self._valueType = valueType


    def head(self) -> Node.Port:
        return self._head
    def setHead(self, head: Node.Port) -> None:
        self._head = head


    def tail(self) -> Node.Port:
        return self._tail
    def setTail(self, tail: Node.Port) -> None:
        self._tail = tail


class Graph:
    """ This class holds the graph's information: it gets the dynamic graph's
        entities and signals, and generates their corresponding PySide items.
    """

    def __init__(self):
        self._dgCommunication = DynamicGraphCommunication()

        # Entities that exist in the dynamic graph:
        self._dgEntities: List[EntityNode] = []
        # Input nodes that don't exist in the dynamic graph:
        self._inputNodes: List[InputNode] = []


    def _getNodePerName(self, name:str) -> Node | None:
        for node in self._dgEntities + self._inputNodes:
            if node.name() == name:
                return node
        return None


    def _getDgData(self) -> None:
        # Gettings every entity:
        entitiesNames = self._dgCommunication.getAllEntitiesNames()
        if entitiesNames is None:
            return

        # For each entity, we will store its signals' infos to create edges later
        # (they have to be created after all ports have been created):
        entitiesPlugsInfos: Dict[EntityNode, List[str]] = {}

        for name in entitiesNames:
            # Creating the node:
            type = self._dgCommunication.getEntityType(name)
            newNode = EntityNode(name, type)
            self._dgEntities.append(newNode)

            # Creating the node's ports:
            entitiesPlugsInfos[newNode] = []
            sigDescriptions = self._dgCommunication.getEntitySignals(name)
            for sigDescription in sigDescriptions:
                plugInfo = self._parseSignalDescription(sigDescription)
                if plugInfo is None:
                    continue
                # Storing this plug's info:
                entitiesPlugsInfos[newNode].append(plugInfo)
                # Adding this port to the node:
                newNode.addPort(plugInfo['name'], plugInfo['type'])

        # Linking the ports with edges:
        for (node, plugsInfos) in entitiesPlugsInfos.items():
            for plugInfo in plugsInfos:
                # Creating the edge that will be plugged to this port:
                # We only handle input signals to prevent creating an edge twice
                if plugInfo['type'] == 'input':
                    self._addSignalToDgData(plugInfo, node)


    def _addSignalToDgData(self, plugInfo: Dict[str, str], childNode: Node) -> None:
        sigName = plugInfo['name']
        childNodeName = childNode.name()

        signalValue = self._dgCommunication.getSignalValue(childNodeName, sigName)
        newEdge = Edge(signalValue, plugInfo['valueType'])

        # Linking the signal to the child port:
        childNode.setEdgeForPort(newEdge, plugInfo['name'])

        # Getting the description of the plug this signal is plugged to, 
        # i.e an output signal of the parent entity:
        linkedPlugDescr = self._dgCommunication.getLinkedPlug(childNodeName, sigName)
        linkedPlugInfo = self._parseSignalDescription(linkedPlugDescr)

        # If the signal is autoplugged (i.e has a fixed value instead of
        # being plugged to a another entity), the entity will appear as
        # linked to itself through this signal
        if childNodeName == linkedPlugInfo['entityName']:
            # If the signal is autoplugged, we add an InputNode to the graph
            # to represent the input value
            newNode = InputNode(newEdge)
            self._inputNodes.append(newNode)
        else:
            # If the signal is not autoplugged, we link it to the parent entity
            parentEntity = self._getNodePerName(linkedPlugInfo['entityName'])
            parentEntity.setEdgeForPort(newEdge, linkedPlugInfo['name'])


    def _parseSignalDescription(self, signalDescription: str) -> Dict[str, str] | None:
        """ Parses a signal's descriptionb (e.g
            `'Add_of_double(add1)::input(double)::sin0'`) and returns a
            dictionary containing its information:
            - `name`: e.g `'sin0'`
            - `type`: `'input'` or `'output'`
            - `valueType`: type of the signal's value (e.g `'double'`)
            - `entityName`: name of the entity plugged to the signal
            - `entityType`: class name of the entity plugged to the
              signal (e.g `'Add_of_double'`)
        """
        try:
            splitDescription = signalDescription.split("::")
            return dict(
                entityType = splitDescription[0].split('(')[0],
                entityName = splitDescription[0].split('(')[1].split(')')[0],
                type = splitDescription[1].split('(')[0],
                valueType = splitDescription[1].split('(')[1].split(')')[0],
                name = splitDescription[2]
            )
        except:
            print(f"Cannot handle signal: {signalDescription}")
            return None


    def _getEncodedDotCode(self) -> bytes:
        dotGenerator = DotDataGenerator()
        dotGenerator.setGraphAttributes({'rankdir': quoted('LR')})

        # Adding the input nodes:
        dotGenerator.setNodeAttributes({'shape': 'circle'})
        for node in self._inputNodes:
            outputPorts = node.outputs()
            if len(outputPorts) != 1:
                raise ValueError("An InputNode should have exactly one output.")
            outputValue = outputPorts[0].edge().value()
            dotGenerator.addNode(node.name(), {'label': outputValue})

        # Adding the dynamic graph entities' nodes and their input edges:
        dotGenerator.setNodeAttributes({'shape': 'box'})
        for entity in self._dgEntities:
            dotGenerator.addNode(entity.name(), {'label': quoted(entity.name())})

            inputEdges = [ port.edge() for port in entity.inputs() ]
            for edge in inputEdges:
                parentNodeName = edge.tail().node().name()
                # The value is displayed only if the parent node isn't an InputNode:
                attributes = None
                if isinstance(self._getNodePerName(parentNodeName), EntityNode):
                    attributes = {'label': edge.value()}
                dotGenerator.addEdge(parentNodeName, entity.name(), attributes)

        return dotGenerator.getEncodedDotString()


    def _generateQtItems(self) -> None:
        encodedDotCode = self._getEncodedDotCode()
        (out, _) = subprocess.Popen(['dot', '-Tjson'], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate(encodedDotCode)
        print(out.decode('utf-8'))


    def getQtItems(self) -> List[QGraphicsItem]:
        ...
