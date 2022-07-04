from dynamic_graph import plug 
from dynamic_graph.sot.core.operator import Add_of_double 
from dynamic_graph.sot.core.operator import Multiply_of_double

NUMBER_OF_LINES = 2

def getNbOfNodesOnLine(lineIdx):
    return pow(2, lineIdx)

lowestLine = None
previousLine = None

# Building the graph from bottom (last node) to top (inputs)
for lineIdx in range(NUMBER_OF_LINES):

    currentLine = []
    for i in range(getNbOfNodesOnLine(lineIdx)):

        # Creating the entities, alterning between lines of adds and mults
        if lineIdx % 2 == 0:
            newEntity = Add_of_double(f"add_{lineIdx}_{i}")
        else:
            newEntity = Multiply_of_double(f"mult_{lineIdx}_{i}")

        if lineIdx == NUMBER_OF_LINES - 1:
            # Setting the input values of the last (highest) line's entities:
            newEntity.sin(0).value = 1
            newEntity.sin(1).value = 2
        if lineIdx != 0 and i % 2 == 1:
            # Linking this line's entities with the previous one's with signals:
            plug(newEntity.sout, previousLine[i // 2].sin(0))
            plug(currentLine[i - 1].sout, previousLine[i // 2].sin(1))

        currentLine.append(newEntity)

    previousLine = currentLine
    if lineIdx == 0:
        lowestLine = currentLine

# Executing the graph
lowestLine[0].sout.recompute(1)
