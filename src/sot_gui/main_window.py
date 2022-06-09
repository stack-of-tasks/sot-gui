from PySide2.QtWidgets import (QMainWindow, QGraphicsScene, QGraphicsView, QToolBar,
    QAction, QGraphicsRectItem, QGraphicsPolygonItem, QMessageBox)
from PySide2.QtGui import QColor

from sot_gui.graph import Graph


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stack Of Tasks GUI")

        self._graph_scene = GraphScene(self)
        self._view = QGraphicsView(self)
        self._view.setScene(self._graph_scene)
        self.setCentralWidget(self._view)

        self._view.setFixedSize(1000, 750)
        self._view.setSceneRect(0, 0, 900, 650)
        #self._view.fitInView(0, 0, 900, 650, Qt.KeepAspectRatio)

        # Adding a toolbar with buttons:
        toolbar = QToolBar("Toolbar")
        self.addToolBar(toolbar)

        button_refresh = QAction("Refresh", self)
        button_refresh.triggered.connect(self.refresh_graph)
        toolbar.addAction(button_refresh)

        button_reconnect = QAction("Reconnect", self)
        button_reconnect.triggered.connect(self.reconnect_and_refresh_graph)
        toolbar.addAction(button_reconnect)

        button_add_rect = QAction("Add rect", self)
        button_add_rect.triggered.connect(self._graph_scene.add_rect)
        toolbar.addAction(button_add_rect)

        button_change_color = QAction("Change color", self)
        button_change_color.triggered.connect(self._graph_scene.change_color)
        toolbar.addAction(button_change_color)

        button_nb_items = QAction("Print nb items", self)
        button_nb_items.triggered.connect(self._graph_scene.print_nb_items)
        toolbar.addAction(button_nb_items)

        # Displaying the graph:
        self.refresh_graph()


    #
    # BUTTONS CALLBACKS
    #

    def refresh_graph(self):
        try:
            self._graph_scene.refresh()
        except ConnectionError:
            self.message_box_reconnect_and_refresh()


    def reconnect_and_refresh_graph(self):
        try:
            self._graph_scene.reconnect_and_refresh()
        except ConnectionError:
            self.message_box_reconnect_and_refresh()


    #
    # MESSAGE BOXES
    #

    def message_box_reconnect_and_refresh(self):
        message_box = QMessageBox(self.parent())
        message_box.setWindowTitle("No connection")

        # Asking the user if they want to reconnect and refresh:
        message_box.setText("There is no connection to the kernel.")
        message_box.setInformativeText('Try to connect again and refresh the graph?')
        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        message_box.setDefaultButton(QMessageBox.Yes)

        return_value = message_box.exec_()
        if return_value == QMessageBox.Yes:
            self.reconnect_and_refresh_graph()  
        

class GraphScene(QGraphicsScene):

    def __init__(self, parent):
        super().__init__(parent)
        #self.setSceneRect(0, 0, 1000, 750)
        self._graph = Graph()


    def refresh(self):
        """ Raises a ConnectionError if the kernel is not running. """
            
        self._graph.refresh_graph()
        self.clear()
        self._items = self._graph.get_qt_items()
        for item in self._items:
            self.addItem(item)

        # TODO: update scene's size, etc


    def reconnect_and_refresh(self):
        """ Raises a ConnectionError if the kernel is not running. """
        self._graph.reconnect_to_kernel()
        self.refresh()


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
