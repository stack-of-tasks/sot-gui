from sot_gui.dot_data_generator import DotDataGenerator

from sot_gui.utils import dotCoordsToQtCoords

def main():
    # app = QApplication([])
    # window = MainWindow()
    # window.show()
    # app.exec()

    dotData = DotDataGenerator()
    dotData.setGraphAttributes({'rankdir':'LR'})
    dotData.addNode("add1")
    dotData.setNodeAttributes({'label':'"aaah"', 'color':'red'})
    dotData.setEdgeAttributes({'label':'"aaah"', 'color':'red'})
    dotData.addNode("add2", {'label':'"aaah"', 'color':'red'})
    dotData.addEdge("add1", "add2", {'label':'"aaah"', 'color':'red'})
    print(dotData.getDotString())
    

if __name__ == "__main__" :
    main()