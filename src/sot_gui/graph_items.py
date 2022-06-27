
""" QGraphicsItems subclasses to allow interactions with items. """

from PySide2.QtWidgets import (QGraphicsPolygonItem, QGraphicsEllipseItem,
    QGraphicsTextItem, QGraphicsPathItem)

class GraphPolygon(QGraphicsPolygonItem):
    def mouseClickEvent(self, event):
        print("Yep")
        self.scene().itemClicked.emit(self)


class GraphEllipse(QGraphicsEllipseItem):
    ...


class GraphText(QGraphicsTextItem):
    ...


class GraphPath(QGraphicsPathItem):
    ...
