from dynamic_graph import plug 
from dynamic_graph.sot.core.operator import Add_of_double 

a = Add_of_double('a')
b = Add_of_double('b')
c = Add_of_double('c')

plug(a.sout, c.sin(0))
plug(b.sout, c.sin(1))
