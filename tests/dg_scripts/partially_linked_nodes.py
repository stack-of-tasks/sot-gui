from dynamic_graph import plug 
from dynamic_graph.sot.core.operator import Add_of_double 

a = Add_of_double('a')
b = Add_of_double('b')
c = Add_of_double('c')

a.sin(0).value = 1
b.sin(1).value = 2

plug(b.sout, c.sin(1))
