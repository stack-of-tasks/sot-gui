from __future__ import annotations # To prevent circular dependencies of annotations
from typing import Union, List, Any, Dict

from PyQt5.QtWidgets import QGraphicsItem

from sot_gui.dynamic_graph_communication import DynamicGraphCommunication


class Node:
    """  """
    def __init__(self):
        self._name: str = None
        self._type: str = None
        self._inputs: Dict[str, Edge] = None
        self._outputs: Dict[str, Edge] = None
        self._ports: List[Port] = None
        self._pyqtElements: List[QGraphicsItem] = None


    def name(self) -> str:
        return self._name


    def type(self) -> str:
        return self._type
    def setType(self, type: str) -> None:
        self._type = type


    def inputs(self) -> Dict[str, Edge]:
        return self._inputs.copy()
    def addInput(self, plugName: str, input: Edge) -> None:
        self._inputs[plugName] = input
        input.setHead(self)


    def outputs(self) -> Dict[str, Edge]:
        return self._outputs.copy()
    def addOutput(self, plugName: str, output: Edge) -> None:
        self._outputs[plugName] = output
        output.setTail(self)


class InputNode(Node):
    _inputNodeCount = 0

    def __init__(self, type: str = None):
        self._type = type
        self._name = f"InputNode{InputNode._inputNodeCount}"
        InputNode._inputNodeCount += 1
        self._outputs = []
        self._pyqtElements = []


class EntityNode(Node):
    def __init__(self, name: str, type: str = None):
        self._name = name
        self._type = type
        self._inputs = []
        self._outputs = []
        self._ports = []
        self._pyqtElements = []


class Port:
    def __init__(self, name: str, node: Node):
        ...


class Edge:
    def __init__(self, value: Any = None, valueType: str = None,
                head: Union[Node, Port] = None, tail: Union[Node, Port] = None):
        self._value = value
        self._valueType = valueType
        self._head = head
        self._tail = tail


    def name(self) -> str:
        return self._name


    def valueType(self) -> str:
        return self._valueType
    def setValueType(self, valueType: str) -> None:
        self._valueType = valueType


    def head(self) -> Node:
        return self._head
    def setHead(self, head: Node) -> None:
        self._head = head


    def tail(self) -> Node:
        return self._tail
    def setTail(self, tail: Node) -> None:
        self._tail = tail


class Graph:
    """ This class holds the graph's information: it gets the dynamic graph's
        entities and signals, and generates their corresponding PyQt elements.
    """

    def __init__(self):
        self._dgEntities: List[self.Entity] = []
        self._pyqtEntities: List[QGraphicsItem] = []

        self._dgCommunication = DynamicGraphCommunication()


    def _getEntityPerName(self, name:str) -> Node | None:
        for entity in self._dgEntities:
            if entity.name() == name:
                return entity
        return None


    def _getDgData(self) -> None:
        # Gettings every entity:
        entitiesNames = self._dgCommunication.getAllEntitiesNames()
        for name in entitiesNames:
            type = self._dgCommunication.getEntityType(name)
            newNode = EntityNode(name, type)
            self._dgEntities.append(newNode)
    
        # Linking the entities with signals:
        for entity in self._dgEntities:
            # Handling every signal for this entity:
            sigDescriptions = self._dgCommunication.getEntitySignals(entity.name())
            for sigDescription in sigDescriptions:

                plugInfo = self._parseSignalDescription(sigDescription)
                if plugInfo is None:
                    continue

                # We only handle input signals to prevent creating an edge twice:
                if plugInfo['type'] == 'input':
                    self._addSignalToDgData(plugInfo, entity)


    def _addSignalToDgData(self, plugInfo: Dict[str, str], childEntity: Node) -> None:
        sigName = plugInfo['name']
        childEntityName = childEntity.name()

        signalValue = self._dgCommunication.getSignalValue(childEntityName, sigName)
        newEdge = Edge(signalValue, plugInfo['valueType'])

        # Linking the signal to the child entity:
        childEntity.addInput(sigName, newEdge)

        # Getting the description of the plug this signal is plugged to, 
        # i.e an output signal of the parent entity:
        linkedPlugDescr = self._dgCommunication.getLinkedPlug(childEntityName, sigName)
        linkedPlugInfo = self._parseSignalDescription(linkedPlugDescr)

        # If the signal is autoplugged (i.e has a fixed value instead of
        # being plugged to a another entity), the entity will appear as
        # linked to itself through this signal
        if childEntityName == linkedPlugInfo['entityName']:
            # If the signal is autoplugged, we add an InputNode to the graph
            # to represent the input value
            newNode = InputNode(newEdge.valueType())
            newNode.addOutput(linkedPlugInfo['name'], newEdge)
        else:
            # If the signal is not autoplugged, we link it to the parent entity
            parentEntity = self._getEntityPerName(linkedPlugInfo['name'])
            parentEntity.addOutput(linkedPlugInfo['name'], newEdge)


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


    def _generatePyQtElements(self) -> None:
        ...


    def getPyQtElements(self) -> List[QGraphicsItem]:
        ...
