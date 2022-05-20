class DotDataGenerator:
    """ This class allows to generate dot code through a simple API. """

    def __init__(self, graphName: str = "G") -> None:
        self._graphName = graphName
        self._graphContentStr = ""


    def getDotString(self) -> str:
        """ Returns the generated dot code as a string. """
        finalString = "digraph " + self._graphName + " {\n"
        finalString += self._graphContentStr
        finalString += "}\n"
        return finalString


    def getEncodedDotString(self) -> bytes:
        """ Returns the generated dot code as a utf-8 encoded string. """
        return self.getDotString().encode()

    
    def addNode(self, name: str, attributes: dict = None) -> None:
        """ Adds a node to the graph, with optional attributes. """

        # The name cannot contain a colon, as this character is used to work
        # with ports 
        if ':' in name:
            raise ValueError("Node name cannot contain a colon ':'")

        newLine = f"\t{name}"
        if attributes is not None:
            newLine += ' '
            newLine += self._generateListOfAttributes(attributes)
        newLine += "\n"

        self._graphContentStr += newLine

    
    def addEdge(self, tail: str, head: str, attributes: dict = None) -> None:
        """ Adds an edge to the graph, with optional attributes. Its tail and
            head can be nodes, or nodes' ports.
        """
        newLine = f"\t{tail} -> {head}"
        if attributes is not None:
            newLine += ' '
            newLine += self._generateListOfAttributes(attributes)
        newLine += '\n'

        self._graphContentStr += newLine


    def setGraphAttributes(self, attributes: dict) -> None:
        """ Sets graph attributes. This method can be called anytime during the
            graph creation.
        """
        newLines = ""
        if attributes is not None:
            for (key, value) in attributes.items():
                newLines += f"\t{key}={str(value)}\n"
        self._graphContentStr += newLines


    def setNodeAttributes(self, attributes: dict) -> None:
        """ Sets nodes attributes. These attributes will only be applied to
            nodes created after calling this method.
        """
        if len(attributes) == 0:
            return
        newLine = '\tnode '
        newLine += self._generateListOfAttributes(attributes)
        newLine += '\n'
        self._graphContentStr += newLine


    def setEdgeAttributes(self, attributes: dict) -> None:
        """ Sets edges attributes. These attributes will only be applied to
            edges created after calling this method.
        """
        if len(attributes) == 0:
            return
        newLine = '\tedge '
        newLine += self._generateListOfAttributes(attributes)
        newLine += '\n'
        self._graphContentStr += newLine


    def _generateListOfAttributes(self, attributes: dict) -> str:
        """ Returns a string containing a dot-formatted list of node or edge
            attributes.    
        """

        # Example of a list of attributes: [label='add1', color=red]
        if len(attributes) > 0:
            string = "["
            for i, (key, value) in enumerate(attributes.items()):
                string += f"{key}={str(value)}"
                if i < len(attributes) - 1:
                    string += ", "
            string += "]"
        return string
