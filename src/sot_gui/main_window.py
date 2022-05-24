from PySide2.QtWidgets import (QMainWindow, QGraphicsScene, QGraphicsView,
    QToolBar, QAction)

from sot_gui.graph import Graph


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stack Of Tasks GUI")

        self._scene = GraphScene(self)
        self._view = QGraphicsView(self)
        self._view.setScene(self._scene)
        self.setCentralWidget(self._view)

        toolbar = QToolBar("Toolbar")
        self.addToolBar(toolbar)
        button_action = QAction("Refresh", self)
        button_action.setStatusTip("Refresh the graph")
        button_action.triggered.connect(self._scene.refresh_graph)
        toolbar.addAction(button_action)


class GraphScene(QGraphicsScene):

    def __init__(self, parent):
        super().__init__(parent)

        self._graph = Graph()
        self._graph.refresh_graph()
        self._items = self._graph.get_qt_items()
        for item in self._items:
            self.addItem(item)


    def refresh_graph(self):
        self._graph.refresh_graph()