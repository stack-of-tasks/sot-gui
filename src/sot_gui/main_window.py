from tokenize import Double
from PyQt5.QtWidgets import (QApplication, QMainWindow, QGraphicsScene,
    QGraphicsView, QToolBar, QDockWidget, QWidget, QAction, QGraphicsRectItem,
    QGraphicsPolygonItem, QGraphicsEllipseItem, QGraphicsSimpleTextItem, 
    QGraphicsPathItem)

from PyQt5.QtGui import QPainter, QPen, QPolygonF, QPainterPath

from PyQt5.QtCore import Qt, QRectF, QPointF

from sot_gui.utils import dot_coords_to_qt_coords
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

        self._graph = Graph()
        self._items = self._graph.get_qt_items()
        for item in self._items:
            self._scene.addItem(item)

        # Rectangles
        # rect = QGraphicsRectItem(0, 0, 60, 160)
        # self.scene.addItem(rect)

        # Polygons
        # polygon = QPolygonF()
        # polygon.append(QPointF(0, 0))
        # polygon.append(QPointF(20, 20))
        # polygon.append(QPointF(30, 50))
        # polygonItem = QGraphicsPolygonItem(polygon)
        # self.scene.addItem(polygonItem)

        # Ellipses / cercles
        # rect = QRectF(0, 0, 60, 160)
        # ellipse = QGraphicsEllipseItem(rect)
        # square = QRectF(0, 0, 60, 60)
        # circle = QGraphicsEllipseItem(square)
        # self.scene.addItem(ellipse)
        # self.scene.addItem(circle)

        # Text
        # text = QGraphicsSimpleTextItem("hello world")
        # self.scene.addItem(text)

        # Curve / straightline
        # /!\ Add a path to QPainterPath if there are several bezier curves
        # pointsCurve = [[47.510,114.130],[60.020,107.810],[76.800,100.890],[93.580,98.710]]
        # pointsStraightLine = [[54.080,72.000],[65.840,72.000],[80.030,72.000],[93.700,72.000]]
        # coordsQt = []
        # for list in pointsCurve:
        #   sceneRect = self.scene.itemsBoundingRect()
        #   sceneHeight = sceneRect.height()
        #     coordsQt.append(dotCoordsToQtCoords((list[0], list[1]), sceneHeight))
        # path = QPainterPath()
        # path.moveTo(coordsQt[0][0], coordsQt[0][1])
        # path.cubicTo(coordsQt[1][0], coordsQt[1][1], coordsQt[2][0], coordsQt[2][1],
        #     coordsQt[3][0], coordsQt[3][1])
        # curve = QGraphicsPathItem(path)
        # self.scene.addItem(curve)

        #self.show()


    
