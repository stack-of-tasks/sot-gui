from PyQt5.QtWidgets import (QApplication, QMainWindow, QGraphicsScene,
    QGraphicsView, QToolBar, QDockWidget, QWidget, QAction, QGraphicsRectItem,
    QGraphicsPolygonItem, QGraphicsEllipseItem, QGraphicsSimpleTextItem, 
    QGraphicsPathItem)

from PyQt5.QtGui import QPainter, QPen, QPolygonF, QPainterPath

from PyQt5.QtCore import Qt, QRectF, QPointF

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stack Of Tasks GUI")

        toolbar = QToolBar("My main toolbar")
        self.addToolBar(toolbar)
        button_action = QAction("Your button", self)
        button_action.setStatusTip("This is your button")
        button_action.triggered.connect(self.onMyToolBarButtonClick)
        toolbar.addAction(button_action)

        sotGraphView = SOTGraphView(self)
        self.setCentralWidget(sotGraphView)
        #self.addDockWidget(Qt.BottomDockWidgetArea, QDockWidget(sotGraphView))

    def onMyToolBarButtonClick(self):
        print("hdfgjqy")


class SOTGraphView(QGraphicsView):

    def __init__(self, parentWidget):
        super().__init__(parentWidget)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

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
        #     coordsQt.append(self.dotCoordsToQtCoords((list[0], list[1])))
        # path = QPainterPath()
        # path.moveTo(coordsQt[0][0], coordsQt[0][1])
        # path.cubicTo(coordsQt[1][0], coordsQt[1][1], coordsQt[2][0], coordsQt[2][1],
        #     coordsQt[3][0], coordsQt[3][1])
        # curve = QGraphicsPathItem(path)
        # self.scene.addItem(curve)

        self.show()


    def dotCoordsToQtCoords(self, coords):
        (xCoord, yCoord) = coords
        sceneRect = self.scene.itemsBoundingRect()
        sceneHeight = sceneRect.height()
        return xCoord, sceneHeight - yCoord


app = QApplication([])

window = MainWindow()
window.show()

app.exec()