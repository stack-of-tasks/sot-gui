from sot_gui.dot_data_generator import DotDataGenerator

from sot_gui.graph import Graph

def main():
    # app = QApplication([])
    # window = MainWindow()
    # window.show()
    # app.exec()

    # dotGenerator = DotDataGenerator()
    # dotGenerator.setGraphAttributes({'rankdir':'LR'})
    # dotGenerator.addNode("add1")
    # dotGenerator.setNodeAttributes({'label':'"aaah"', 'color':'red'})
    # dotGenerator.setEdgeAttributes({'label':'"aaah"', 'color':'red'})
    # dotGenerator.addNode("add2", {'label':'"aaah"', 'color':'red'})
    # dotGenerator.addEdge("add1", "add2", {'label':'"aaah"', 'color':'red'})
    # print(dotGenerator.getDotString())
    
    graph = Graph()
    graph._getDgData()
    graph._generateQtItems()


if __name__ == "__main__" :
    main()