from PySide2.QtWidgets import (QMainWindow, QGraphicsScene, QGraphicsView, QToolBar,
    QAction, QGraphicsRectItem, QGraphicsPolygonItem, QMessageBox)
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

        button_reconnect = QAction("Reconnect", self)
        #button_reconnect.setStatusTip("Refresh the graph")
        button_reconnect.triggered.connect(self._scene.reconnect_to_kernel)
        toolbar.addAction(button_reconnect)

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
        

class GraphScene(QGraphicsScene):

    def __init__(self, parent):
        super().__init__(parent)
        #self.setSceneRect(0, 0, 1000, 750)
        self._graph = Graph()
        self.refresh_graph()


    def refresh_graph(self):
        # Trying to get data from the kernel. Suggest reconnecting if the
        # connection to the kernel is not open:

        try:
            self._graph.refresh_graph()
            self.clear()
            self._items = self._graph.get_qt_items()
            for item in self._items:
                self.addItem(item)

        except:
            self.message_box_reconnect()

        # TODO: update scene's size, etc


    def reconnect_to_kernel(self):
        self._graph.reconnect_to_kernel()
        self.refresh_graph()


    def message_box_reconnect(self):
        message_box = QMessageBox(self.parent())
        message_box.setWindowTitle("No connection")

        # Asking the user if they want to reconnect and refresh:
        message_box.setText("The connection to the kernel has been closed.")
        message_box.setInformativeText('Do you want to reconnect and refresh?')
        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        message_box.setDefaultButton(QMessageBox.Yes)

        return_value = message_box.exec_()
        if return_value == QMessageBox.Yes:
            self.reconnect_to_kernel()    


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
