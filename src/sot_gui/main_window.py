from PySide2.QtCore import Qt

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

        self._view.setFixedSize(1000, 750)
        self._view.setSceneRect(0, 0, 900, 650)
        #self._view.fitInView(0, 0, 900, 650, Qt.KeepAspectRatio)

        toolbar = QToolBar("Toolbar")
        self.addToolBar(toolbar)
        button_action = QAction("Refresh", self)
        button_action.setStatusTip("Refresh the graph")
        button_action.triggered.connect(self._scene.refresh_graph)
        toolbar.addAction(button_action)


class GraphScene(QGraphicsScene):

    def __init__(self, parent):
        super().__init__(parent)
        #self.setSceneRect(0, 0, 1000, 750)
        self._graph = Graph()
        self.refresh_graph()


    def refresh_graph(self):
        self.clear()
        self._graph.refresh_graph()
        self._items = self._graph.get_qt_items()
        for item in self._items:
            self.addItem(item)

        # TODO: update scene's background color, size, etc
