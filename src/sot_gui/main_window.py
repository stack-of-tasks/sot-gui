from typing import Union
from enum import Enum
import threading
from time import sleep

from PySide2.QtWidgets import (QMainWindow, QGraphicsScene, QGraphicsView,
    QToolBar, QAction, QMessageBox, QLabel, QGraphicsItem, QInputDialog)
from PySide2.QtGui import QColor
from PySide2.QtCore import Qt

from sot_gui.graph import Graph, Node, Port, Edge, EntityNode, InputNode
from sot_gui.dynamic_graph_communication import DynamicGraphCommunication


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stack Of Tasks GUI")

        # Adding the graph scene and its view:
        self._graph_scene = SoTGraphScene(self)
        self._view = SoTGraphView(self)
        self._view.setScene(self._graph_scene)
        self.setCentralWidget(self._view)

        self._add_toolbar()
        self._add_status_bar()

        # Displaying the graph:
        self._refresh_graph()


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
        button_refresh.triggered.connect(self._refresh_graph)
        toolbar.addAction(button_refresh)

        button_reconnect = QAction("Reconnect", self)
        button_reconnect.triggered.connect(self._reconnect)
        toolbar.addAction(button_reconnect)

        button_clusterize = QAction("Create group", self)
        button_clusterize.triggered.connect(self._create_entity_group)
        toolbar.addAction(button_clusterize)


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
            self._reconnect()
            if refresh:
                self._refresh_graph()


    #
    # BUTTONS CALLBACKS
    #

    def _refresh_graph(self) -> None:
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


    def _reconnect(self) -> None:
        """ Reconnects the graph to the latest running kernel.

            The graph will not be automatically refreshed.
            If there is no running kernel, a message box is opened to alert the
            user and let them launch one before re-attempting a connection.
        """
        if self._graph_scene.reconnect():
            self._reconnection_needed = False
        else:
            self._message_box_no_connection()


    def _create_entity_group(self) -> None:
        """ Launches the creation of an entity group. """
        self._view.launch_group_creation()


class SoTGraphView(QGraphicsView):
    """ QGraphicsView which handles events to interact with the SoTGraphScene
        items.
    """

    def __init__(self, parent):
        super().__init__(parent)

        self.interactionMode = self.InteractionMode.DEFAULT

        # When the user drags the mouse, it moves the view:
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        # To center the zoom on the position of the mouse:
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)


    class InteractionMode(Enum):
        """ This enum is used to determine how to handle events based on there
            being an ongoing user action or not (e.g when the user creates a
            group of entities, a click on a node must be handled differently)
        """
        DEFAULT = 0
        GROUP_CREATION = 1 # When the user is creating a group of entities


    #
    # EVENT OVERRIDES
    #

    def wheelEvent(self, event):
        """ See QGraphicsView.wheelEvent """
        # The user can zoom in or out by rotating the mouse wheel:
        self._handleZoom(event.angleDelta().y())


    def keyReleaseEvent(self, event):
        """ See QGraphicsView.keyReleaseEvent """
        # If the group creation mode is on, releasing the escape key cancels the
        # action and releasing the return key completes it:
        if self.interactionMode == self.InteractionMode.GROUP_CREATION:
            key = event.key()
            if key == Qt.Key_Enter or key == Qt.Key_Return:
                self._completeGroupCreation()
            elif key == Qt.Key_Escape:
                self._cancelGroupCreation()


    def mouseReleaseEvent(self, event):
        """ See QGraphicsView.mouseReleaseEvent """
        click_pos = event.localPos()
        clicked_item = self.itemAt(click_pos.x(), click_pos.y())
        if clicked_item is None:
            return

        if self.interactionMode == self.InteractionMode.GROUP_CREATION:
            self.scene().select_item_for_group_creation(clicked_item)


    #
    # EVENT CALLBACKS
    #

    def _handleZoom(self, delta: int) -> None:
        """ Rescales the view according to the amount that the mouse wheel was
            rotated.

            Args:
                delta: relative amount that the wheel was rotated
        """
        # For more info on the delta value, see:
        # https://doc.qt.io/qtforpython-5/PySide2/QtGui/QWheelEvent.html#PySide2.QtGui.PySide2.QtGui.QWheelEvent.angleDelta
        if delta > 0:
            self.scale(1.25, 1.25)
        else:
            self.scale(0.8, 0.8)


    def launch_group_creation(self) -> None:
        """ TODO """
        if self.interactionMode != self.InteractionMode.GROUP_CREATION:
            self.interactionMode = self.InteractionMode.GROUP_CREATION


    def _completeGroupCreation(self) -> None:
        """ TODO """
        self.interactionMode = self.InteractionMode.DEFAULT
        group_name, clicked_ok = QInputDialog().getText(self, 'Group name',
                                'Please enter a name for this entity group.')

        if clicked_ok:
            self.scene().complete_group_creation(group_name)
        else:
            self._cancelGroupCreation()


    def _cancelGroupCreation(self) -> None:
        """ TODO """
        self.interactionMode = self.InteractionMode.DEFAULT
        self.scene().clear_selection()


class SoTGraphScene(QGraphicsScene):
    """ QGraphicsScene which contains the graph qt items and manages the
        communication with the Graph object.

        Attributes: See QGraphicsScene
    """

    _selected_color = 'lightGray'
    _unselected_color = 'white'

    def __init__(self, parent):
        super().__init__(parent)
        self._connected_to_kernel = False
        self._dg_communication = DynamicGraphCommunication()
        self._graph = Graph(self._dg_communication)

        self._selected_nodes = []


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


    def select_item_for_group_creation(self, item: QGraphicsItem) -> None:
        """ TODO """
        selected_node = None
        graph_elem = self.get_graph_elem_per_qt_item(item)

        if isinstance(graph_elem, EntityNode):
            selected_node = graph_elem

        elif isinstance(graph_elem, Port):
            selected_node = graph_elem.node()

        elif isinstance(graph_elem, InputNode) or isinstance(graph_elem, Edge):
            # InputNodes and Edges are not selected
            return

        self._update_selected_nodes(selected_node)


    def _update_selected_nodes(self, node: Node) -> None:
        """ Adds / removes a node to / from the selection.

            When a node is selected, if will be colored in its entirety (label
            cell + ports).

            Args:
                node: The node to add or remove.
        """
        if node in self._selected_nodes:
            self._selected_nodes.remove(node)
            self._update_color_selected_node(node, False)
        else:
            self._selected_nodes.append(node)
            self._update_color_selected_node(node, True)


    def complete_group_creation(self, group_name: str) -> None:
        """ TODO """
        print(len(self._selected_nodes), group_name)
        self.clear_selection()


    def clear_selection(self) -> None:
        """ TODO """
        for node in self._selected_nodes:
            self._update_color_selected_node(node, False)
        self._selected_nodes = []


    def _update_color_selected_node(self, node: Node, selected: bool) -> None:
        """ Changes a node's color (middle column + ports) depending on its
            selection status.

            Args:
                node: The node whose color will be updated.
                selected: If True (respectively if False), the node's color will
                    be updated to make it appear selected (respectively
                    unselected).
        """
        new_color = self._selected_color if selected else self._unselected_color
        node.qt_item().setBrush(QColor(new_color))
        for port in node.ports():
            port.qt_item().setBrush(QColor(new_color))


    def get_graph_elem_per_qt_item(self, item: QGraphicsItem) \
        -> Union[Node, Port, Edge]:
        """ TODO """
        graph_elem = self._graph.get_elem_per_qt_item(item)
        return graph_elem
