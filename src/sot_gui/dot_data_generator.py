from typing import Dict, Tuple, List, Any
from sot_gui.utils import quoted


"""
    Graphviz documentation:
    https://graphviz.org/documentation/
    https://www.graphviz.org/pdf/dotguide.pdf

    Interactive tool to test dot code's output (xdot, json, svg...):
    https://dreampuf.github.io/GraphvizOnline/
"""


class DotDataGenerator:
    """ This class allows to generate dot code through a simple API. """

    def __init__(self, graph_name: str = "G"):
        self._graph_name = graph_name
        self._graph_content_str = ""


    def get_dot_string(self) -> str:
        """ Returns the generated dot code as a string. """
        final_string = "digraph " + self._graph_name + " {\n"
        final_string += self._graph_content_str
        final_string += "}\n"
        return final_string


    def get_encoded_dot_string(self) -> bytes:
        """ Returns the generated dot code as a utf-8 encoded string. """
        return self.get_dot_string().encode()

    
    def add_node(self, name: str, attributes: Dict[str, Any] = None) -> None:
        """ Adds a node to the graph, with optional attributes. """

        # The name cannot contain a colon, as this character is used to work
        # with ports 
        if ':' in name:
            raise ValueError("Node name cannot contain a colon ':'")

        new_line = f"\t{name}"
        if attributes is not None:
            new_line += ' '
            new_line += self._generate_list_of_attributes(attributes)
        new_line += "\n"

        self._graph_content_str += new_line


    def add_html_node(self, name: str, ports: Tuple[List[Tuple[str]]],
        label: str = None) -> None:
        """ Adds an html-style node to the graph.

            Args:
              name: name of the node
              ports: inputs and outputs of the node, as a tuple (inputs, outputs).
                Each element of this tuple is a list of tuples containing the port's
                data: (name, label).
              label: label of the node. If None, the name of the node will be used.

            Raises:
                RuntimeError: there are no inputs or outputs.
        """

        (inputs, outputs) = ports
        if inputs == [] or outputs == []:
            raise RuntimeError('')

        if label is None:
            label = quoted(name)

        # Online tool to generate html tables based on the desired layout:
        # https://www.tablesgenerator.com/html_tables
        html = '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">\n'

        nb_rows = max(len(inputs), len(outputs))

        # For each row, we add its elements from left to right:
        for i in range(nb_rows):
            html += '\t\t<TR>\n'

            # Adding the node's label:
            if i == 0:
                html += f'\t\t\t<TD ROWSPAN="{nb_rows}">{label}</TD>\n'

            html += '\t\t</TR>\n'

        html += '</TABLE>>'

        self._graph_content_str += f'\t{name} [label={html}]\n'

    
    def add_edge(self, tail: str, head: str, attributes: Dict[str, Any] = None) -> None:
        """ Adds an edge to the graph, with optional attributes. Its tail and
            head can be nodes, or nodes' ports.
        """
        new_line = f"\t{tail} -> {head}"
        if attributes is not None:
            new_line += ' '
            new_line += self._generate_list_of_attributes(attributes)
        new_line += '\n'

        self._graph_content_str += new_line


    def set_graph_attributes(self, attributes: Dict[str, Any]) -> None:
        """ Sets graph attributes. This method can be called anytime during the
            graph creation.
        """
        new_lines = ""
        if attributes is not None:
            for (key, value) in attributes.items():
                new_lines += f"\t{key}={str(value)}\n"
        self._graph_content_str += new_lines


    def set_node_attributes(self, attributes: Dict[str, Any]) -> None:
        """ Sets nodes attributes. These attributes will only be applied to
            nodes created after calling this method.
        """
        if len(attributes) == 0:
            return
        new_line = '\tnode '
        new_line += self._generate_list_of_attributes(attributes)
        new_line += '\n'
        self._graph_content_str += new_line


    def set_edge_attributes(self, attributes: Dict[str, Any]) -> None:
        """ Sets edges attributes. These attributes will only be applied to
            edges created after calling this method.
        """
        if len(attributes) == 0:
            return
        new_line = '\tedge '
        new_line += self._generate_list_of_attributes(attributes)
        new_line += '\n'
        self._graph_content_str += new_line


    def _generate_list_of_attributes(self, attributes: Dict[str, Any]) -> str:
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
