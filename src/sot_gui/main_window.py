from PySide2.QtWidgets import (QMainWindow, QGraphicsScene, QGraphicsView,
    QToolBar, QAction, QGraphicsRectItem)

from sot_gui.graph import Graph


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stack Of Tasks GUI")

        toolbar = QToolBar("My main toolbar")
        self.addToolBar(toolbar)
        button_action = QAction("Your button", self)
        button_action.setStatusTip("This is your button")
        button_action.triggered.connect(self.button_callback)
        toolbar.addAction(button_action)

        sot_graph_view = SOTGraphView(self)
        self.setCentralWidget(sot_graph_view)


    def button_callback(self):
        print("hdfgjqy")


class SOTGraphView(QGraphicsView):

    def __init__(self, parent_widget):
        super().__init__(parent_widget)
        self._scene = QGraphicsScene()
        self.setScene(self._scene)

        rect = QGraphicsRectItem(0, 0, 60, 160)
        self._scene.addItem(rect)

        # self._graph = Graph()
        # self._items = self._graph.get_qt_items()
        # for item in self._items:
        #     self._scene.addItem(item)   
