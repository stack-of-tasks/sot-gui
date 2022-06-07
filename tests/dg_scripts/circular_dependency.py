from dynamic_graph import plug 
from dynamic_graph.sot.core.operator import Add_of_double 

a = Add_of_double('a')
b = Add_of_double('b')

a.sin(0).value = 1
b.sin(0).value = 2

plug(a.sout, b.sin(1))
plug(b.sout, a.sin(1))
