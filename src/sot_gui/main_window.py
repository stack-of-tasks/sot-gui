import threading
from time import sleep

from PySide2.QtWidgets import (QMainWindow, QGraphicsScene, QGraphicsView, QToolBar,
    QAction, QGraphicsRectItem, QGraphicsPolygonItem, QMessageBox)
from PySide2.QtGui import QColor

from sot_gui.graph import Graph
from sot_gui.dynamic_graph_communication import DynamicGraphCommunication


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stack Of Tasks GUI")

        # Adding the graph scene and its view:
        self._graph_scene = GraphScene(self)
        self._view = QGraphicsView(self)
        self._view.setScene(self._graph_scene)
        self.setCentralWidget(self._view)

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

    def refresh_graph(self) -> None:
        try:
            self._graph_scene.refresh()
        except ConnectionError:
            self.message_box_reconnect_and_refresh()


    def reconnect_and_refresh_graph(self) -> None:
        try:
            self._graph_scene.reconnect_and_refresh()
        except ConnectionError:
            self.message_box_reconnect_and_refresh()


    #
    # MESSAGE BOXES
    #

    def message_box_reconnect_and_refresh(self) -> None:
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
        self._connected_to_kernel = False
        self._dg_communication = DynamicGraphCommunication()
        self._graph = Graph(self._dg_communication)

        # Launching a thread to update the status of the connection to the kernel:
        self._kernel_heartbeat_thread = threading.Thread(
            target=self._connection_status_updating)
        self._kernel_heartbeat_thread.setDaemon(True)
        self._kernel_heartbeat_thread.start()


    def refresh(self) -> None:
        """ Raises a ConnectionError if the kernel is not running. """
            
        self._graph.refresh_graph()
        self.clear()
        self._items = self._graph.get_qt_items()
        for item in self._items:
            self.addItem(item)


    def reconnect_and_refresh(self) -> None:
        """ Raises a ConnectionError if the kernel is not running. """
        self._dg_communication.connect_to_kernel()
        self.refresh()


    def _connection_status_updating(self) -> None:
        while 1:
            self._connected_to_kernel = self._dg_communication.is_kernel_alive()
            self.change_color('green' if self._connected_to_kernel else 'red')
            sleep(0.1)


    def add_rect(self):
        print(self.sceneRect())
        self.addItem(QGraphicsRectItem(0, 0, 1000, 1000))
        print(self.sceneRect())


    def change_color(self, color: str):
        items = self.items()
        for item in items:
            if isinstance(item, QGraphicsPolygonItem):
                item.setBrush(QColor(color))


    def print_nb_items(self):
        items = self.items()
        print(len(items))


    def __del__(self):
        self._kernel_heartbeat_thread.join()
        del self._kernel_heartbeat_thread
