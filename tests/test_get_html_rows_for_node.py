from unittest import TestCase
from sot_gui.dot_data_generator import DotDataGenerator

# To check if the dot code given as output is correct by displaying the
# graph: dreampuf.github.io/GraphvizOnline/

class TestHTMLRows(TestCase):
    """ Tests for the _get_html_rows_for_node method of the DotDataGenerator class. """

    def setUp(self):
        self._gen = DotDataGenerator()


    def test_equal_nb_in_out(self):
        """ Cases were the number of inputs is equal to the number of outputs. """
        
        # 1 input, 1 output:
        label = 'entity'
        inputs = [('sin0', 'input 0')]
        outputs = [('sout0', 'output 0')]
        expected_output = '\t\t<TR>\n' +\
            '\t\t\t<TD ROWSPAN="1" PORT="sin0">input 0</TD>\n' +\
            '\t\t\t<TD ROWSPAN="1">entity</TD>\n' +\
            '\t\t\t<TD ROWSPAN="1" PORT="sout0">output 0</TD>\n' +\
            '\t\t</TR>\n'
        actual_output = self._gen._get_html_rows_for_node(label, inputs, outputs)
        assert actual_output == expected_output

        # 2 inputs, 2 outputs:
        label = 'entity'
        inputs = [('sin0', 'input 0'), ('sin1', 'input 1')]
        outputs = [('sout0', 'output 0'), ('sout1', 'output 1')]
        expected_output = '\t\t<TR>\n' +\
            '\t\t\t<TD ROWSPAN="1" PORT="sin0">input 0</TD>\n' +\
            '\t\t\t<TD ROWSPAN="2">entity</TD>\n' +\
            '\t\t\t<TD ROWSPAN="1" PORT="sout0">output 0</TD>\n\t\t</TR>\n' +\
            '\t\t<TR>\n\t\t\t<TD ROWSPAN="1" PORT="sin1">input 1</TD>\n' +\
            '\t\t\t<TD ROWSPAN="1" PORT="sout1">output 1</TD>\n\t\t</TR>\n'
        actual_output = self._gen._get_html_rows_for_node(label, inputs, outputs)
        assert actual_output == expected_output

        # 4 inputs, 4 outputs:
        label = 'entity'
        inputs = [('sin0', 'input 0'), ('sin1', 'input 1'), ('sin2', 'input 2'),
            ('sin3', 'input 3')]
        outputs = [('sout0', 'output 0'), ('sout1', 'output 1'), ('sout2', 'output 2'),
            ('sout3', 'output 3')]
        expected_output = '\t\t<TR>\n' +\
            '\t\t\t<TD ROWSPAN="1" PORT="sin0">input 0</TD>\n' +\
            '\t\t\t<TD ROWSPAN="4">entity</TD>\n' +\
            '\t\t\t<TD ROWSPAN="1" PORT="sout0">output 0</TD>\n\t\t</TR>\n' +\
            '\t\t<TR>\n\t\t\t<TD ROWSPAN="1" PORT="sin1">input 1</TD>\n' +\
            '\t\t\t<TD ROWSPAN="1" PORT="sout1">output 1</TD>\n\t\t</TR>\n' +\
            '\t\t<TR>\n\t\t\t<TD ROWSPAN="1" PORT="sin2">input 2</TD>\n' +\
            '\t\t\t<TD ROWSPAN="1" PORT="sout2">output 2</TD>\n\t\t</TR>\n' +\
            '\t\t<TR>\n\t\t\t<TD ROWSPAN="1" PORT="sin3">input 3</TD>\n' +\
            '\t\t\t<TD ROWSPAN="1" PORT="sout3">output 3</TD>\n\t\t</TR>\n'
        actual_output = self._gen._get_html_rows_for_node(label, inputs, outputs)
        assert actual_output == expected_output


    def test_one_in_several_out(self):
        """ Cases were there is one input and several outputs. """

        # 1 input, 2 outputs
        label = 'entity'
        inputs = [('sin0', 'input 0')]
        outputs = [('sout0', 'output 0'), ('sout1', 'output 1')]
        expected_output = '\t\t<TR>\n' +\
            '\t\t\t<TD ROWSPAN="2" PORT="sin0">input 0</TD>\n' +\
            '\t\t\t<TD ROWSPAN="2">entity</TD>\n' +\
            '\t\t\t<TD ROWSPAN="1" PORT="sout0">output 0</TD>\n\t\t</TR>\n' +\
            '\t\t<TR>\n\t\t\t<TD ROWSPAN="1" PORT="sout1">output 1</TD>\n\t\t</TR>\n'
        actual_output = self._gen._get_html_rows_for_node(label, inputs, outputs)
        assert actual_output == expected_output

        # 1 input, 3 outputs
        label = 'entity'
        inputs = [('sin0', 'input 0')]
        outputs = [('sout0', 'output 0'), ('sout1', 'output 1'), ('sout2', 'output 2')]
        expected_output = '\t\t<TR>\n\t\t\t<TD ROWSPAN="3" PORT="sin0">input 0</TD>\n' +\
            '\t\t\t<TD ROWSPAN="3">entity</TD>\n' +\
            '\t\t\t<TD ROWSPAN="1" PORT="sout0">output 0</TD>\n\t\t</TR>\n\t\t<TR>\n' +\
            '\t\t\t<TD ROWSPAN="1" PORT="sout1">output 1</TD>\n\t\t</TR>\n\t\t<TR>\n' +\
            '\t\t\t<TD ROWSPAN="1" PORT="sout2">output 2</TD>\n\t\t</TR>\n'
        actual_output = self._gen._get_html_rows_for_node(label, inputs, outputs)
        assert actual_output == expected_output


    def test_several_in_one_out(self):
        """ Cases were there is several inputs and one output. """

        # 2 inputs, 1 output
        label = 'entity'
        inputs = [('sin0', 'input 0'), ('sin1', 'input 1')]
        outputs = [('sout0', 'output 0')]
        expected_output = '\t\t<TR>\n\t\t\t<TD ROWSPAN="1" PORT="sin0">input 0</TD>\n' +\
            '\t\t\t<TD ROWSPAN="2">entity</TD>\n' +\
            '\t\t\t<TD ROWSPAN="2" PORT="sout0">output 0</TD>\n\t\t</TR>\n\t\t<TR>\n' +\
            '\t\t\t<TD ROWSPAN="1" PORT="sin1">input 1</TD>\n\t\t</TR>\n'
        actual_output = self._gen._get_html_rows_for_node(label, inputs, outputs)
        assert actual_output == expected_output

        # 3 inputs, 1 output
        label = 'entity'
        inputs = [('sin0', 'input 0'), ('sin1', 'input 1'), ('sin2', 'input 2')]
        outputs = [('sout0', 'output 0')]
        expected_output = '\t\t<TR>\n\t\t\t<TD ROWSPAN="1" PORT="sin0">input 0</TD>\n' +\
            '\t\t\t<TD ROWSPAN="3">entity</TD>\n' +\
            '\t\t\t<TD ROWSPAN="3" PORT="sout0">output 0</TD>\n\t\t</TR>\n\t\t<TR>\n' +\
            '\t\t\t<TD ROWSPAN="1" PORT="sin1">input 1</TD>\n\t\t</TR>\n\t\t<TR>\n' +\
            '\t\t\t<TD ROWSPAN="1" PORT="sin2">input 2</TD>\n\t\t</TR>\n'
        actual_output = self._gen._get_html_rows_for_node(label, inputs, outputs)
        assert actual_output == expected_output


    def test_several_in_out_multiples(self):
        """ Cases were there are several inputs and outputs, and one of the numbers is
            a multiple of the other one.
        """

        # 2 inputs, 4 outputs
        label = 'entity'
        inputs = [('sin0', 'input 0'), ('sin1', 'input 1')]
        outputs = [('sout0', 'output 0'), ('sout1', 'output 1'), ('sout2', 'output 2'),
            ('sout3', 'output 3')]
        expected_output = '\t\t<TR>\n\t\t\t<TD ROWSPAN="2" PORT="sin0">input 0</TD>\n' +\
            '\t\t\t<TD ROWSPAN="4">entity</TD>\n' +\
            '\t\t\t<TD ROWSPAN="1" PORT="sout0">output 0</TD>\n\t\t</TR>\n\t\t<TR>\n' +\
            '\t\t\t<TD ROWSPAN="1" PORT="sout1">output 1</TD>\n\t\t</TR>\n\t\t<TR>\n' +\
            '\t\t\t<TD ROWSPAN="2" PORT="sin1">input 1</TD>\n' +\
            '\t\t\t<TD ROWSPAN="1" PORT="sout2">output 2</TD>\n\t\t</TR>\n' +\
            '\t\t<TR>\n\t\t\t<TD ROWSPAN="1" PORT="sout3">output 3</TD>\n\t\t</TR>\n'
        actual_output = self._gen._get_html_rows_for_node(label, inputs, outputs)
        assert actual_output == expected_output

        # 4 inputs, 2 outputs
        label = 'entity'
        inputs = [('sin0', 'input 0'), ('sin1', 'input 1'), ('sin2', 'input 2'),
            ('sin3', 'input 3')]
        outputs = [('sout0', 'output 0'), ('sout1', 'output 1')]
        expected_output = '\t\t<TR>\n\t\t\t<TD ROWSPAN="1" PORT="sin0">input 0</TD>\n' +\
            '\t\t\t<TD ROWSPAN="4">entity</TD>\n' +\
            '\t\t\t<TD ROWSPAN="2" PORT="sout0">output 0</TD>\n\t\t</TR>\n' +\
            '\t\t<TR>\n\t\t\t<TD ROWSPAN="1" PORT="sin1">input 1</TD>\n\t\t</TR>\n' +\
            '\t\t<TR>\n\t\t\t<TD ROWSPAN="1" PORT="sin2">input 2</TD>\n' +\
            '\t\t\t<TD ROWSPAN="2" PORT="sout1">output 1</TD>\n\t\t</TR>\n' +\
            '\t\t<TR>\n\t\t\t<TD ROWSPAN="1" PORT="sin3">input 3</TD>\n\t\t</TR>\n'
        actual_output = self._gen._get_html_rows_for_node(label, inputs, outputs)
        assert actual_output == expected_output


    def test_several_in_out_not_multiples(self):
        """ Cases were there are several inputs and outputs, and none of the numbers is
            a multiple of the other one.
        """

        # 2 inputs, 3 outputs
        label = 'entity'
        inputs = [('sin0', 'input 0'), ('sin1', 'input 1')]
        outputs = [('sout0', 'output 0'), ('sout1', 'output 1'), ('sout2', 'output 2')]
        expected_output = '\t\t<TR>\n\t\t\t<TD ROWSPAN="1" PORT="sin0">input 0</TD>\n' +\
            '\t\t\t<TD ROWSPAN="3">entity</TD>\n' +\
            '\t\t\t<TD ROWSPAN="1" PORT="sout0">output 0</TD>\n\t\t</TR>\n' +\
            '\t\t<TR>\n\t\t\t<TD ROWSPAN="2" PORT="sin1">input 1</TD>\n' +\
            '\t\t\t<TD ROWSPAN="1" PORT="sout1">output 1</TD>\n\t\t</TR>\n' +\
            '\t\t<TR>\n\t\t\t<TD ROWSPAN="1" PORT="sout2">output 2</TD>\n\t\t</TR>\n'
        actual_output = self._gen._get_html_rows_for_node(label, inputs, outputs)
        assert actual_output == expected_output

        # 3 inputs, 2 outputs
        label = 'entity'
        inputs = [('sin0', 'input 0'), ('sin1', 'input 1'), ('sin2', 'input 2')]
        outputs = [('sout0', 'output 0'), ('sout1', 'output 1')]
        expected_output = '\t\t<TR>\n\t\t\t<TD ROWSPAN="1" PORT="sin0">input 0</TD>\n' +\
            '\t\t\t<TD ROWSPAN="3">entity</TD>\n' +\
            '\t\t\t<TD ROWSPAN="1" PORT="sout0">output 0</TD>\n\t\t</TR>\n' +\
            '\t\t<TR>\n\t\t\t<TD ROWSPAN="1" PORT="sin1">input 1</TD>\n' +\
            '\t\t\t<TD ROWSPAN="2" PORT="sout1">output 1</TD>\n\t\t</TR>\n' +\
            '\t\t<TR>\n\t\t\t<TD ROWSPAN="1" PORT="sin2">input 2</TD>\n\t\t</TR>\n'
        actual_output = self._gen._get_html_rows_for_node(label, inputs, outputs)
        assert actual_output == expected_output


    def test_several_in_out_big_difference(self):
        """ Cases were there are several inputs and outputs, and the diffenrence between
            the two numbers is high.
        """

        # 2 inputs, 7 outputs
        label = 'entity'
        inputs = [('sin0', 'input 0'), ('sin1', 'input 1')]
        outputs = [('sout0', 'output 0'), ('sout1', 'output 1'), ('sout2', 'output 2'),
            ('sout3', 'output 3'), ('sout4', 'output 4'), ('sout5', 'output 5'),
            ('sout6', 'output 6')]
        expected_output = '\t\t<TR>\n\t\t\t<TD ROWSPAN="3" PORT="sin0">input 0</TD>\n' +\
            '\t\t\t<TD ROWSPAN="7">entity</TD>\n' +\
            '\t\t\t<TD ROWSPAN="1" PORT="sout0">output 0</TD>\n\t\t</TR>\n' +\
            '\t\t<TR>\n\t\t\t<TD ROWSPAN="1" PORT="sout1">output 1</TD>\n\t\t</TR>\n' +\
            '\t\t<TR>\n\t\t\t<TD ROWSPAN="1" PORT="sout2">output 2</TD>\n\t\t</TR>\n' +\
            '\t\t<TR>\n\t\t\t<TD ROWSPAN="4" PORT="sin1">input 1</TD>\n' +\
            '\t\t\t<TD ROWSPAN="1" PORT="sout3">output 3</TD>\n\t\t</TR>\n' +\
            '\t\t<TR>\n\t\t\t<TD ROWSPAN="1" PORT="sout4">output 4</TD>\n\t\t</TR>\n' +\
            '\t\t<TR>\n\t\t\t<TD ROWSPAN="1" PORT="sout5">output 5</TD>\n\t\t</TR>\n' +\
            '\t\t<TR>\n\t\t\t<TD ROWSPAN="1" PORT="sout6">output 6</TD>\n\t\t</TR>\n'
        actual_output = self._gen._get_html_rows_for_node(label, inputs, outputs)
        assert actual_output == expected_output

        # 7 inputs, 2 outputs
        label = 'entity'
        inputs = [('sin0', 'input 0'), ('sin1', 'input 1'), ('sin2', 'input 2'),
            ('sin3', 'input 3'), ('sin4', 'input 4'), ('sin5', 'input 5'),
            ('sin6', 'input 6')]
        outputs = [('sout0', 'output 0'), ('sout1', 'output 1')]
        expected_output = '\t\t<TR>\n\t\t\t<TD ROWSPAN="1" PORT="sin0">input 0</TD>\n' +\
            '\t\t\t<TD ROWSPAN="7">entity</TD>\n' +\
            '\t\t\t<TD ROWSPAN="3" PORT="sout0">output 0</TD>\n\t\t</TR>\n' +\
            '\t\t<TR>\n\t\t\t<TD ROWSPAN="1" PORT="sin1">input 1</TD>\n\t\t</TR>\n' +\
            '\t\t<TR>\n\t\t\t<TD ROWSPAN="1" PORT="sin2">input 2</TD>\n\t\t</TR>\n' +\
            '\t\t<TR>\n\t\t\t<TD ROWSPAN="1" PORT="sin3">input 3</TD>\n' +\
            '\t\t\t<TD ROWSPAN="4" PORT="sout1">output 1</TD>\n\t\t</TR>\n' +\
            '\t\t<TR>\n\t\t\t<TD ROWSPAN="1" PORT="sin4">input 4</TD>\n\t\t</TR>\n' +\
            '\t\t<TR>\n\t\t\t<TD ROWSPAN="1" PORT="sin5">input 5</TD>\n\t\t</TR>\n' +\
            '\t\t<TR>\n\t\t\t<TD ROWSPAN="1" PORT="sin6">input 6</TD>\n\t\t</TR>\n'
        actual_output = self._gen._get_html_rows_for_node(label, inputs, outputs)
        assert actual_output == expected_output
