from typing import Dict, Tuple, List, Any


# Graphviz documentation:
# https://graphviz.org/documentation/
# https://www.graphviz.org/pdf/dotguide.pdf

# Interactive tool to test dot code's output (xdot, json, svg...):
# https://dreampuf.github.io/GraphvizOnline/


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
        """ Adds a node to the graph, with optional attributes.
        
        Args:
            name: The name of the node
            attributes: A dictionary containing the attributes of the node.
                The keys and values are in the same form as in dot code (e.g
                `attributes['shape'] = 'box'` corresponds to `shape=box` in dot.
        """

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
                Each element of this tuple is a list of tuples (name, label)
                containing the port's data.
            label: label of the node. If None, the name of the node will be
                used.

        Raises:
            RuntimeError: there are no inputs or outputs.
        """

        (inputs, outputs) = ports
        if inputs == [] or outputs == []:
            raise RuntimeError('')

        if label is None:
            label = name

        table_content = self._get_html_rows_for_node(label, inputs, outputs)
        html = (f'<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" '
                f'CELLPADDING="4">\n{table_content}\t</TABLE>>')

        self._graph_content_str += f'\t{name} [label={html}]\n'


    # When the number of inputs is not a multiple of the number of
    # outputs (or vice versa), the height of the cells will vary in the column
    # with less elements.
    # Regular html allows for a balanced table thanks to empty rows (<TR></TR>),
    # but dot does not support them.
    # If support for empty rows is added to dot in the future, this method
    # should be updated to allow for a more even display of the ports.
    # Online tool to help understand where to use empty rows:
    # https://www.tablesgenerator.com/html_tables
    def _get_html_rows_for_node(self, label: str, inputs: List[Tuple[str]],
                                outputs: List[Tuple[str]]) -> str:
        """ Generates html code for the rows of a node.

        Args:
            label: label of the node
            inputs: input ports of the node, as a list of tuples (input_name,
                input_label).
            outputs: output ports of the node, as a list of tuples (output_name,
                output_label).

        Returns:
            Html code for the rows of the node, as a string.
        """

        # We determine which column (inputs or outputs) has more rows
        inputs_nb = len(inputs)
        outputs_nb = len(outputs)
        max_nb = None
        if inputs_nb > outputs_nb:
            max_nb = 'inputs'
        elif inputs_nb < outputs_nb:
            max_nb = 'outputs'
        nb_rows = max(inputs_nb, outputs_nb)

        input_count, output_count = 0, 0

        # For each row, we add its elements from left to right.
        # Online tool to generate html tables based on the desired layout:
        # https://www.tablesgenerator.com/html_tables
        rows_html = ""
        for i in range(nb_rows):
            input, output = None, None
            rowspan_input, rowspan_output = 1, 1
            remaining_nb_rows = nb_rows - i

            # If there are more inputs, each input cell will have a rowspan of
            # 1, the middle column (node's label) will have a rowspan of
            # `inputs_nb`, and each output cell will span over
            # `inputs_nb // outputs_nb` nb of lines, except the last one which
            # will span over the remaining available rows.
            if max_nb == 'inputs':
                input = inputs[i]
                rowspan_output = inputs_nb // outputs_nb
                if (output_count < outputs_nb and
                    i == output_count * rowspan_output):
                    output = outputs[output_count]
                    if output_count == outputs_nb - 1: # If it's the last output
                        rowspan_output = remaining_nb_rows
                    output_count += 1
                input_count += 1
            
            # The same logic applies if there are more outputs
            elif max_nb == 'outputs':
                output = outputs[i]
                rowspan_input = outputs_nb // inputs_nb
                if input_count < inputs_nb and i == input_count * rowspan_input:
                    input = inputs[input_count]
                    if input_count == inputs_nb - 1: # If it's the last input
                        rowspan_input = remaining_nb_rows
                    input_count += 1
                output_count += 1

            # If `inputs_nb` and `outputs_nb` are equal, we add one input and
            # one output on each row, so both with a rowspan of 1
            else:
                input = inputs[i]
                output = outputs[i]
                input_count += 1
                output_count += 1

            # Creating the html code for the row
            input_cell = ''
            if input is not None:
                (in_name, in_label) = input
                input_cell = (f'\t\t\t<TD ROWSPAN="{rowspan_input}" '
                    f'PORT="{in_name}">{in_label}</TD>\n')

            # The node's label is added to the first row and spans over each row
            label_cell = ''
            if i == 0:
                label_cell = f'\t\t\t<TD ROWSPAN="{nb_rows}">{label}</TD>\n'

            output_cell = ''
            if output is not None:
                (out_name, out_label) = output
                output_cell = (f'\t\t\t<TD ROWSPAN="{rowspan_output}" '
                    f'PORT="{out_name}">{out_label}</TD>\n')

            row_content = input_cell + label_cell + output_cell
            rows_html += f'\t\t<TR>\n{row_content}\t\t</TR>\n'

        return rows_html
    

    def add_edge(self, tail: Tuple[str, str], head: Tuple[str, str],
                 attributes: Dict[str, Any] = None) -> None:
        """ Adds an edge to the graph, with optional attributes.

        Args:
            tail: tuple containing the tail's data: (node's name, port's name).
                The port's name can be None.
            head: tuple containing the head's data: (node's name, port's name)
                The port's name can be None.
            attributes: A dictionary containing the attributes of the edge.
                The keys and values are in the same form as in dot code (e.g
                `attributes['color'] = 'red'` corresponds to `color=red` in dot.
        """

        tail_node, tail_port = tail
        head_node, head_port = head

        # The head and tail are in the form: `node:port`, or simply `node` if
        # no port is specified
        tail_str = tail_node
        if tail_port is not None:
            tail_str += f':{tail_port}'
        head_str = head_node
        if head_port is not None:
            head_str += f':{head_port}'

        new_line = f"\t{tail_str} -> {head_str}"
        if attributes is not None:
            new_line += ' '
            new_line += self._generate_list_of_attributes(attributes)
        new_line += '\n'

        self._graph_content_str += new_line


    def set_graph_attributes(self, attributes: Dict[str, Any]) -> None:
        """ Sets graph attributes.

        This method can be called anytime during the graph creation.

        Args:
            attributes: A dictionary containing the attributes of the graph.
                The keys and values are in the same form as in dot code (e.g
                `attributes['rankdir'] = 'LR'` corresponds to `rankdir=LR`
                in dot.
        """
        new_lines = ""
        if attributes is not None:
            for (key, value) in attributes.items():
                new_lines += f"\t{key}={str(value)}\n"
        self._graph_content_str += new_lines


    def set_node_attributes(self, attributes: Dict[str, Any]) -> None:
        """ Sets nodes attributes.
        
        These attributes will only be applied to nodes created after calling
        this method.

        Args:
            attributes: A dictionary containing the attributes to apply to the
                nodes from now on. The keys and values are in the same form as
                in dot code (e.g `attributes['shape'] = 'box'` corresponds to
                `shape=box` in dot.
        """
        if len(attributes) == 0:
            return
        new_line = '\tnode '
        new_line += self._generate_list_of_attributes(attributes)
        new_line += '\n'
        self._graph_content_str += new_line


    def set_edge_attributes(self, attributes: Dict[str, Any]) -> None:
        """ Sets edges attributes.
        
        These attributes will only be applied to edges created after calling
        this method.

        Args:
            attributes: A dictionary containing the attributes to apply to the
                edges from now on. The keys and values are in the same form as
                in dot code (e.g `attributes['color'] = 'red'` corresponds to
                `color=red` in dot.
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

        Args:
            attributes: A dictionary containing the attributes to format.
                The keys and values are in the same form as in dot code
                (e.g `attributes['color'] = 'red'` corresponds to `color=red`
                in dot.
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
