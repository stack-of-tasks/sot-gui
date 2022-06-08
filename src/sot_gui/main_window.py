from PySide2.QtCore import Qt

from PySide2.QtWidgets import (QMainWindow, QGraphicsScene, QGraphicsView,
    QToolBar, QAction, QGraphicsRectItem, QGraphicsPolygonItem)
from PySide2.QtGui import QColor

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

        button_refresh = QAction("Refresh", self)
        #button_refresh.setStatusTip("Refresh the graph")
        button_refresh.triggered.connect(self._scene.refresh_graph)
        toolbar.addAction(button_refresh)

        button_add_rect = QAction("Add rect", self)
        #button_add_rect.setStatusTip("Refresh the graph")
        button_add_rect.triggered.connect(self._scene.add_rect)
        toolbar.addAction(button_add_rect)

        button_change_color = QAction("Change color", self)
        #button_change_color.setStatusTip("Refresh the graph")
        button_change_color.triggered.connect(self._scene.change_color)
        toolbar.addAction(button_change_color)

        button_nb_items = QAction("Print nb items", self)
        #button_nb_items.setStatusTip("Refresh the graph")
        button_nb_items.triggered.connect(self._scene.print_nb_items)
        toolbar.addAction(button_nb_items)

        button_reconnect = QAction("Reconnect", self)
        #button_reconnect.setStatusTip("Refresh the graph")
        button_reconnect.triggered.connect(self._scene.reconnect_to_kernel)
        toolbar.addAction(button_reconnect)
        

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

        # TODO: update scene's size, etc


    def add_rect(self):
        self.addItem(QGraphicsRectItem(0, 0, 1000, 1000))


    def change_color(self):
        items = self.items()
        for item in items:
            if isinstance(item, QGraphicsPolygonItem):
                item.setBrush(QColor("red"))


    def print_nb_items(self):
        items = self.items()
        print(len(items))


    def reconnect_to_kernel(self):
        self._graph.reconnect_to_kernel()
        self.refresh_graph()
