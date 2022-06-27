import threading
from time import sleep

from PySide2.QtWidgets import (QMainWindow, QGraphicsScene, QGraphicsView,
    QToolBar, QAction, QMessageBox, QLabel, QGraphicsRectItem)
from PySide2.QtGui import QColor
from PySide2.QtCore import Signal

from sot_gui.graph import Graph
from sot_gui.dynamic_graph_communication import DynamicGraphCommunication
from sot_gui.graph_items import (GraphPolygon)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stack Of Tasks GUI")

        # Adding the graph scene and its view:
        self._graph_scene = GraphScene(self)
        self._view = QGraphicsView(self)
        self._view.setScene(self._graph_scene)
        self.setCentralWidget(self._view)

        self._add_toolbar()
        self._add_status_bar()

        # Displaying the graph:
        self.refresh_graph()


    def __del__(self):
        self._kernel_heartbeat_thread.join()
        del self._kernel_heartbeat_thread


    #
    # ADDITIONAL WIDGETS
    #

    def _add_toolbar(self) -> None:
        toolbar = QToolBar("Toolbar")
        self.addToolBar(toolbar)

        button_refresh = QAction("Refresh", self)
        button_refresh.triggered.connect(self.refresh_graph)
        toolbar.addAction(button_refresh)

        button_reconnect = QAction("Reconnect", self)
        button_reconnect.triggered.connect(self.reconnect)
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


    def _add_status_bar(self) -> None:
        # If the kernel is stopped and relaunched, its session has changed and
        # sending commands will result in a crash. To prevent this, we don't
        # allow the user to send commands until they triggered a reconnection:
        self._reconnection_needed = not self._graph_scene.connection_status()

        # Adding a status bar displaying the connection status:
        self._co_status_indicator = QLabel("")
        self.statusBar().addPermanentWidget(self._co_status_indicator)

        def _connection_status_updating() -> None:
            while 1:
                if self._graph_scene.connection_status() is False:
                    self._reconnection_needed = True

                self._update_co_status_indicator()
                sleep(0.1)
            
        # Launching a thread to update the connection status of the kernel:
        self._kernel_heartbeat_thread = threading.Thread(
            target=_connection_status_updating)
        self._kernel_heartbeat_thread.setDaemon(True)
        self._kernel_heartbeat_thread.start()


    def _update_co_status_indicator(self) -> None:
        if self._graph_scene.connection_status() is False:
            color = 'red'
            text = 'No kernel detected'

        elif self._reconnection_needed is True:
            color = 'orange'
            text = 'Reconnection available'

        else:
            color = 'green'
            text = 'Connected'
        self._co_status_indicator.setText(text)
        self._co_status_indicator.setStyleSheet('QLabel {color: ' + color + '}')


    def _message_box_no_connection(self, refresh: bool = False) -> None:
        message_box = QMessageBox(self.parent())
        message_box.setWindowTitle("No connection")

        # Asking the user if they want to reconnect and refresh:
        message_box.setText("A connection to the kernel is needed.")
        message_box.setInformativeText('Do you want to try to connect?')
        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        message_box.setDefaultButton(QMessageBox.Yes)

        return_value = message_box.exec_()
        if return_value == QMessageBox.Yes:
            self.reconnect()
            if refresh:
                self.refresh_graph()
        

    #
    # BUTTONS CALLBACKS
    #

    def refresh_graph(self) -> None:
        if self._reconnection_needed:
            self._message_box_no_connection(refresh=True)
        else:
            try:
                self._graph_scene.refresh()
            except ConnectionError:
                self._message_box_no_connection(refresh=True)


    def reconnect(self) -> None:
        if self._graph_scene.reconnect():
            self._reconnection_needed = False
        else:
            self._message_box_no_connection()


class GraphScene(QGraphicsScene):

    item_clicked = Signal(object)

    def __init__(self, parent):
        super().__init__(parent)
        self._connected_to_kernel = False
        self._dg_communication = DynamicGraphCommunication()
        self._graph = Graph(self._dg_communication)

    
    def connection_status(self) -> bool:
        return self._dg_communication.is_kernel_alive()
        

    def refresh(self) -> None:
        """ Raises a ConnectionError if the kernel is not running. """
            
        self._graph.refresh_graph()
        self.clear()
        self._items = self._graph.get_qt_items()
        for item in self._items:
            self.addItem(item)


    def reconnect(self) -> bool:
        return self._dg_communication.connect_to_kernel()


    def add_rect(self):
        print(self.sceneRect())
        self.addItem(QGraphicsRectItem(0, 0, 1000, 1000))
        print(self.sceneRect())


    def change_color(self):
        items = self.items()
        for item in items:
            if isinstance(item, GraphPolygon):
                item.setBrush(QColor('orange'))


    def print_nb_items(self):
        items = self.items()
        print(len(items))
