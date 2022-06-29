import threading
from time import sleep

from PySide2.QtWidgets import (QMainWindow, QGraphicsScene, QGraphicsView,
    QToolBar, QAction, QMessageBox, QLabel, QGraphicsRectItem,
    QGraphicsPolygonItem)
from PySide2.QtGui import QColor, QPainterPath

from sot_gui.graph import Graph, Edge
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
        """ Adds the sot graph toolbar to the main window. """
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
        """ Adds a status bar to the main window.

            The status bar displays the connection status. This method launches
            a thread to monitor this status.
        """
        # If the kernel is stopped and relaunched, its session has changed and
        # sending commands will result in a crash. To prevent this, we don't
        # allow the user to send commands until they triggered a reconnection:
        self._reconnection_needed = not self._graph_scene.is_kernel_running()

        # Adding a status bar displaying the connection status:
        self._co_status_indicator = QLabel("")
        self.statusBar().addPermanentWidget(self._co_status_indicator)

        def _connection_status_updating() -> None:
            while 1:
                if self._graph_scene.is_kernel_running() is False:
                    self._reconnection_needed = True

                self._update_co_status_indicator()
                sleep(0.1)
            
        # Launching a thread to update the connection status of the kernel:
        self._kernel_heartbeat_thread = threading.Thread(
            target=_connection_status_updating)
        self._kernel_heartbeat_thread.setDaemon(True)
        self._kernel_heartbeat_thread.start()


    def _update_co_status_indicator(self) -> None:
        """ Updates the text and color of the connection status indicator. """
        if self._co_status_indicator is None:
            return

        if self._graph_scene.is_kernel_running() is False:
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
        """ Displays a message box which asks the user if the want to reconnect
            to the kernel.

            If the user clicks Yes, a connection attempt is made. If they click
            No, nothing is done. In any case, the message box is closed.

            Args:
                refresh: if True, the graph will be refreshed after the
                    connection attempt, if it was successful.
        """
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
        """ Refreshes the graph. New graph data will be fetched from the kernel
            and displayed.

            If there is no connection to a running kernel, the refresh is
            aborted and a message box is opened to offer the user to connect.
            If they click yes, a new graph refresh will be attempted after the
            reconnection.
        """
        if self._reconnection_needed:
            self._message_box_no_connection(refresh=True)
        else:
            try:
                self._graph_scene.refresh()
            except ConnectionError:
                self._message_box_no_connection(refresh=True)


    def reconnect(self) -> None:
        """ Reconnects the graph to the latest running kernel.

            The graph will not be automatically refreshed.
            If there is no running kernel, a message box is opened to alert the
            user and let them launch one before re-attempting a connection.
        """
        if self._graph_scene.reconnect():
            self._reconnection_needed = False
        else:
            self._message_box_no_connection()


class GraphScene(QGraphicsScene):
    """ Scene which displays the graph qt items and manages the communication to
        the kernel.

        Attributes:
            parent: See QGraphicsScene
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._connected_to_kernel = False
        self._dg_communication = DynamicGraphCommunication()
        self._graph = Graph(self._dg_communication)


    def mouseReleaseEvent(self, event):
        """ See QGraphicsScene """
        click_pos = event.scenePos()
        trans_matrix = self.views()[0].transform()
        clicked_item = self.itemAt(click_pos, trans_matrix)
        
        if clicked_item is not None:
            graph_elem = self._graph.get_elem_per_qt_item(clicked_item)
            if isinstance(graph_elem, Edge):
                print(graph_elem.tail().node().name(),
                      graph_elem.head().node().name())
            else:
                print(graph_elem.name())

    
    def is_kernel_running(self) -> bool:
        """ Returns True if a running SOTKernel is detected.

            Every SOTKernel uses the same ports, which means a kernel can be
            detected without the client being connected to it (if the client
            was previously connected to a SOTKernel which has been stopped).
        """
        return self._dg_communication.is_kernel_alive()
        

    def refresh(self) -> None:
        """ Refreshes the graph. New graph data will be fetched from the kernel
            and displayed.

        Raises:
            ConnectionError: the kernel is not running.
        """
            
        self._graph.refresh_graph()
        self.clear()
        self._items = self._graph.get_qt_items()
        for item in self._items:
            self.addItem(item)


    def reconnect(self) -> bool:
        """ Attemps to reconnect the client to the latest kernel.
        
        Returns:
            True if the connection was successful, False if not.
        """
        return self._dg_communication.connect_to_kernel()


    def add_rect(self):
        print(self.sceneRect())
        self.addItem(QGraphicsRectItem(0, 0, 1000, 1000))

        coords = ...
        path = QPainterPath()

        print(self.sceneRect())


    def change_color(self):
        items = self.items()
        for item in items:
            if isinstance(item, QGraphicsPolygonItem):
                item.setBrush(QColor('orange'))


    def print_nb_items(self):
        items = self.items()
        print(len(items))
