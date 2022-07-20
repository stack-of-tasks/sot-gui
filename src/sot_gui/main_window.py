from __future__ import annotations
from typing import Union, List, Dict
from enum import Enum
import threading
from time import sleep

from PySide2.QtWidgets import (QMainWindow, QGraphicsScene, QGraphicsView,
    QToolBar, QAction, QMessageBox, QLabel, QGraphicsItem, QInputDialog,
    QDockWidget, QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QScrollArea, QWidget)
from PySide2.QtGui import QColor
from PySide2.QtCore import Qt

from sot_gui.graph import Graph, Node, Port, Edge, InputNode, Cluster
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

        self._add_main_toolbar()
        self._add_cluster_toolbar()
        self._add_status_bar()
        self._add_cluster_side_panel()
        self._add_info_side_panel()

        # Displaying the graph:
        self._refresh_graph()


    def __del__(self):
        self._kernel_heartbeat_thread.join()
        del self._kernel_heartbeat_thread


    #
    # ADDITIONAL WIDGETS
    #

    def _add_main_toolbar(self) -> None:
        """ Adds the sot graph toolbar to the main window. """
        toolbar = QToolBar("main_toolbar")
        self._main_toolbar = toolbar
        self.addToolBar(toolbar)

        button_refresh = QAction("Refresh", self)
        button_refresh.triggered.connect(self._refresh_graph)
        toolbar.addAction(button_refresh)

        button_reconnect = QAction("Reconnect", self)
        button_reconnect.triggered.connect(self._reconnect)
        toolbar.addAction(button_reconnect)

        button_clusterize = QAction("Create cluster", self)
        button_clusterize.triggered.connect(self._create_entity_group)
        toolbar.addAction(button_clusterize)

        button_manage_clusters = QAction("Manage clusters", self)
        button_manage_clusters.triggered.connect(self._manage_clusters)
        toolbar.addAction(button_manage_clusters)


    def _add_cluster_toolbar(self):
        self.addToolBarBreak()
        toolbar = QToolBar("cluster_toolbar")
        self.addToolBar(toolbar)
        self._cluster_toolbar = toolbar

        button_complete = QAction("Confirm cluster", self)
        button_complete.triggered.connect(self._view._completeGroupCreation)
        toolbar.addAction(button_complete)

        button_cancel = QAction("Cancel clusterization", self)
        button_cancel.triggered.connect(self._view.cancelGroupCreation)
        toolbar.addAction(button_cancel)

        # This toolbar will only be shown during cluster creation
        toolbar.hide()


    def show_cluster_toolbar(self):
        self._cluster_toolbar.show()
    def hide_cluster_toolbar(self):
        self._cluster_toolbar.hide()


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


    def _add_cluster_side_panel(self) -> None:
        self._cluster_side_panel = ClustersPanel(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self._cluster_side_panel)
        self._cluster_side_panel.hide()


    def _add_info_side_panel(self) -> None:
        self._info_side_panel = InfoPanel(self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self._info_side_panel)
        self._info_side_panel.hide()


    def _message_box_no_connection(self, refresh: bool = False) -> None:
        """ Displays a message box which asks the user if the want to reconnect
            to the kernel.

            If the user clicks Yes, a connection attempt is made. If they click
            No, nothing is done. In any case, the message box is closed.

            Args:
                refresh: if True, the graph will be refreshed after the
                    connection attempt, if it was successful.
        """
        message_box = QMessageBox(self)
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
        self._cancel_ongoing_actions()
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
        self._cancel_ongoing_actions()
        if self._graph_scene.reconnect():
            self._reconnection_needed = False
        else:
            self._message_box_no_connection()


    def _create_entity_group(self) -> None:
        """ Launches the creation of an entity group. """
        self._view.enter_group_creation_mode()


    def _cancel_ongoing_actions(self) -> None:
        if (self._view.interactionMode ==
            SoTGraphView.InteractionMode.GROUP_CREATION):
            self._view.cancelGroupCreation()


    def _manage_clusters(self) -> None:
        self._cluster_side_panel.show()


#
# SIDE WIDGETS
#

class ClustersPanel(QDockWidget):
    def __init__(self, parent):
        super().__init__('Clusters', parent)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self._list_widget = QListWidget(self)
        self.setWidget(self._list_widget)
        option_delete = QAction("Delete", self)
        option_delete.triggered.connect(self._remove_clusters)
        self._list_widget.addAction(option_delete)
        self._list_widget.setContextMenuPolicy(Qt.ActionsContextMenu)
        self._list_widget.setSortingEnabled(True)


    def add_cluster(self, cluster: Cluster) -> None:
        item = QListWidgetItem(cluster.name())
        self._list_widget.addItem(item)


    def _remove_clusters(self) -> None:
        selected_items = self._list_widget.selectedItems()
        for item in selected_items:
            item_row = self._list_widget.indexFromItem(item).row()
            self._list_widget.takeItem(item_row)
            cluster_name = item.text()
            self.parent()._view.scene().remove_cluster(cluster_name)


class InfoPanel(QDockWidget):
    def __init__(self, parent):
        super().__init__('Element info', parent)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self._display_entity_info({})


    def _display_entity_info(self, entity_info: Dict) -> None:

        self._scroll_area = QScrollArea()
        self._info_widget = QWidget()
        self.layout = QVBoxLayout()

        for i in range(1,20):
            object = QLabel("TextLabel:\naaa\n\n")
            self.layout.addWidget(object)

        self._info_widget.setLayout(self.layout)

        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setWidget(self._info_widget)

        self.setWidget(self._scroll_area)


        # self._table_info = QTableWidget(12, 2, self)
        # self._table_info.setEditTriggers(QTableWidget.NoEditTriggers)
        # self.setWidget(self._table_info)

        # newItem = QTableWidgetItem('aaaaa')
        # self._table_info.setItem(0, 0, newItem)



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
        super().wheelEvent(event)
        # The user can zoom in or out by rotating the mouse wheel:
        self._handleZoom(event.angleDelta().y())


    def mouseReleaseEvent(self, event):
        """ See QGraphicsView.mouseReleaseEvent """
        super().mouseReleaseEvent(event)
        click_pos = event.localPos()
        clicked_item = self.itemAt(click_pos.x(), click_pos.y())
        if clicked_item is None:
            return
        #print(self.scene().get_graph_elem_per_qt_item(clicked_item))

        if self.interactionMode == self.InteractionMode.GROUP_CREATION:
            self.scene().select_item_for_group_creation(clicked_item)
        elif self.interactionMode == self.InteractionMode.DEFAULT:
            self.parent()._info_side_panel.show()



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


    def enter_group_creation_mode(self) -> None:
        """ TODO """
        if self.interactionMode != self.InteractionMode.GROUP_CREATION:
            self.parent().show_cluster_toolbar()
            self.interactionMode = self.InteractionMode.GROUP_CREATION
    def exit_group_creation_mode(self) -> None:
        """ TODO """
        self.interactionMode = self.InteractionMode.DEFAULT
        self.parent().hide_cluster_toolbar()
        self.scene().clear_selection()


    def _completeGroupCreation(self) -> None:
        # If clusterizing the selected nodes is not possible, we let the user
        # keep on selecting:
        if self.scene().check_clusterizability() is False:
            self._message_box_wrong_cluster()
            return

        # Else, we let them enter the name of the group in a dialog box:
        group_name, clicked_ok = QInputDialog().getText(self, 'Group name',
                                'Please enter a name for this entity group.')

        if clicked_ok:
            new_cluster = self.scene().complete_group_creation(group_name)
            self.parent()._cluster_side_panel.add_cluster(new_cluster)
            self.exit_group_creation_mode()
        # If the user canceled, we let them keep on selecting


    def cancelGroupCreation(self) -> None:
        self.exit_group_creation_mode()



    def _message_box_wrong_cluster(self) -> None:
        """ Displays a message box to tell the user that the current selection
            is sot suitable to create a cluster.
        """
        message_box = QMessageBox(self)
        message_box.setWindowTitle("Wrong selection")

        # Asking the user if they want to reconnect and refresh:
        message_box.setText("A cluster cannot be created with the currently "
                            "selected nodes.")
        message_box.setInformativeText('Please select:\n  - at least two nodes'
                                        '\n  - only directly linked nodes')
        message_box.exec_()


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


    def update_display(self) -> None:
        """ Updates the graph display. New graph data will not be fetched from
            the kernel.
        """
        self._graph.generate_qt_items()
        self.clear()
        self._items = self._graph.get_qt_items()
        for item in self._items:
            self.addItem(item)


    def refresh(self) -> None:
        """ Refreshes the graph. New graph data will be fetched from the kernel
            and displayed.

        Raises:
            ConnectionError: the kernel is not running.
        """

        self._graph.refresh_graph_data()
        self.update_display()


    def reconnect(self) -> bool:
        """ Attemps to reconnect the client to the latest kernel.

        Returns:
            True if the connection was successful, False if not.
        """
        return self._dg_communication.connect_to_kernel()


    def select_item_for_group_creation(self, item: QGraphicsItem) -> None:
        selected_node = None
        graph_elem = self.get_graph_elem_per_qt_item(item)

        if isinstance(graph_elem, Node):
            selected_node = graph_elem

        elif isinstance(graph_elem, Port):
            selected_node = graph_elem.node()

        elif isinstance(graph_elem, Edge):
            return # Edges are not selected

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


    def complete_group_creation(self, group_name: str) -> Cluster:
        new_cluster = self._graph.add_cluster(group_name,
                                              self._selected_nodes.copy())
        self.update_display()
        return new_cluster


    def remove_cluster(self, cluster_name: str) -> None:
        self._graph.remove_cluster(cluster_name)
        self.update_display()


    def check_clusterizability(self) -> bool:
        """ Returns True if a cluster can be created from the currently selected
            nodes.
        """
        return self._graph.check_clusterizability(self._selected_nodes.copy())


    def clear_selection(self) -> None:
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
        if node.qt_item() is not None:
            node.qt_item().setBrush(QColor(new_color))

        if not isinstance(node, InputNode):
            for port in node.ports():
                if port.qt_item() is not None:
                    port.qt_item().setBrush(QColor(new_color))

    def get_cluster_list(self) -> List[Cluster]:
        return self._graph.clusters()


    def get_graph_elem_per_qt_item(self, item: QGraphicsItem) \
        -> Union[Node, Port, Edge]:
        """ TODO """
        graph_elem = self._graph.get_elem_per_qt_item(item)
        return graph_elem
