# from pathlib import Path

# from .test_sot_gui_base import TestSotGuiBase, input_scripts_dir
# from sot_ipython_connection.app.sot_script_executer import main as script_executer
# from sot_gui.graph import Graph

# class TestNormalDG(TestSotGuiBase):

#     def test_connected_graph(self):
#         # Executing a script to create the graph in the kernel:
#         script_path = str(Path(input_scripts_dir)/'normal_dg.py')
#         script_executer([script_path])

#         self.graph = Graph()
#         self.graph.refresh_graph()
#         items = self.graph.get_qt_items()

#         assert len(items) == 24
#         assert items != []
#         ...