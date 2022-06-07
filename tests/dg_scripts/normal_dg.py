from dynamic_graph import plug 
from dynamic_graph.sot.core.operator import Add_of_double, Multiply_of_double

a = Add_of_double('a')
b = Add_of_double('b')
c = Multiply_of_double('c')

a.sin(0).value = 1
a.sin(1).value = 2
b.sin(0).value = 3
b.sin(1).value = 4

plug(a.sout, c.sin(0))
plug(b.sout, c.sin(1))

c.sout.recompute(1)
