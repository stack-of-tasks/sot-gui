# Architecture of SoT GUI

SoT GUI uses the [sot-ipython-connection package](https://github.com/stack-of-tasks/sot-ipython-connection) to get data from the Stack of Tasks. It uses dot to compute the graph layout, and displays it in a window thanks to PySide (python binding for Qt).
The overall architecture of the program can be seen on Fig.1.

![](https://github.com/justinefricou/sot-gui/blob/main/doc/img/sot-gui-architecture.png)

Figure 1: Overview of SoT GUI’s architecture


### Getting the Dynamic Graph data
SoT GUI uses a SOTClient (from the sot-ipython-connection package) to communicate with the SoT contained in a SOTKernel.

This SoTClient is contained in the DynamicGraphCommunication class, which handles all communications with the kernel.
It has a set of public methods to get information from the Dynamic Graph, such as get_entity_type, is_signal_plugged, get_exec_time, etc. This kind of method takes, for instance, a node or signal name, and returns the requested value: this way, any syntax specific to the dynamic graph implementation is confined to these methods.

All these methods call the \_run method, which sends a command to the kernel, and either:
- returns the result if it is a value
- prints the result if it is an stdout-type response
- prints the error if it is an stderr-type response

DynamicGraphCommunication also allows to handle the connection to the kernel, thanks to its public methods connect_to_kernel and is_kernel_alive.

### Storing the Dynamic Graph data
All of the graph elements are stored thanks to various classes:

![](https://github.com/justinefricou/sot-gui/blob/main/doc/img/graph-element-classes.png)

Figure 2: Classes used to store the graph elements

#### GraphElement
The GraphElement class can be used as a base for any graph element class.
It stores its:
- name
- type
- last execution time
- Qt item (PySide graphic item which will represent the graph element in the display)

The GraphElement class is not meant to be instantiated, only inherited, but this is not an abstract class, as it implements getters and setters for its attributes, so as to not implement the same methods for each type of graph element (nodes, edges, ports, etc all have a name, a Qt item, etc).

#### Node (inherits GraphElement)
The Node class represents a graph node. In addition to the GraphElement attributes from which it inherits, it stores:
- an eventual cluster (Cluster class) in which the node in contained
- the inputs and outputs (Port class) of the node

There being several types of nodes, the Node class is never instantiated. To create nodes, either use an InputNode or an EntityNode, or inherit the Node class to create a new kind of node.

![](https://github.com/justinefricou/sot-gui/blob/main/doc/img/graph-example.png)

Figure 3: Example of a graph containing InputNodes, EntityNodes, Ports and Edges

#### InputNode (inherits Node)
This class represents a fixed value that is used as an entity input. Hence, this is not an entity existing in the Dynamic Graph: this is an input being displayed as a node for clarity.

For instance, after initializing an entity on the Dynamic Graph as can be seen in Fig.4, an InputNode with a value of 1 will be created in SoT GUI, and be linked to an EntityNode named ‘a’.

![](https://github.com/justinefricou/sot-gui/blob/main/doc/img/creating-entity-in-sot-example.png)

Figure 4: Creating an entity on the SoT and giving it a fixed input value

The specificities of this class are as follows:
- In addition to the Node class attributes, it has a value (which is the child entity input value).
- Its type is its value’s type (e.g int, matrix, etc).
- It has only one port: an output linked to the child entity.
- Its name is generated depending on its child node name and port. For instance, in Fig.4, the InputNode name would be ‘input_a_sin0’.


#### EntityNode (inherits Node)
This class represents an entity of the Dynamic Graph.
- Its name is the name given to the entity when it was created in the SoT.
- Its type is the type of the entity (e.g Add_of_double, etc).
- It can have any number of inputs and outputs, which depends on the entity type.

#### Edge (inherits GraphElement)
An Edge represents a signal linking two entities in the SoT.
In addition to the GraphElement attributes from which it inherits, it stores:
- the value of the signal
- the type of the value (e.g float, vector, etc)
- the head of the signal: the node port (input) where this signal is plugged
- the tail of the signal: the node port (output) where this signal is plugged

#### Port (inherits GraphElement)
A Port is where an Edge can be plugged to a Node. In the Dynamic Graph, this is the equivalent of an entity signal (e.g sin0, sin1, sout0). An Edge would be what links two Ports (e.g linking entity1::sout0 to entity2::sin1).

In addition to the GraphElement attributes from which it inherits, it stores:
- the node it belongs to
- the edge plugged into the port, if any
- a value, which is the edge value
Its type is either ‘input’ or ‘output’.

#### Cluster (inherits Node)

![](https://github.com/justinefricou/sot-gui/blob/main/doc/img/clusterization-example.png)

Figure 5: Example of nodes (InputNode 3, EntityNode 1 and EntityNode 2) being grouped into a cluster

A Cluster represents a group of nodes. It does not exist in the Dynamic Graph: it is a visual representation implemented in SoT GUI.

It contains a list of the nodes which compose the cluster. They can be any type of node (InputNode, EntityNode, another Cluster).
It must contain at least 2 nodes, and all its nodes must be directly linked (i.e each node in the cluster is a child node or parent node of at least one other node of the cluster).

A Cluster object has a name and a label: its name is used for the determination of the layout, for which many characters would be forbidden. Its label is what is actually displayed on the screen.
The name is automatically generated when creating a cluster: if it is the 5th cluster created during a session, its name will be “5”.
The label is chosen by the user after they selected the nodes.

The Cluster class has an ‘_expanded’ attribute, which indicates if the cluster is expanded or shrunk.
The “expand cluster” feature has not been implemented yet.

![](https://github.com/justinefricou/sot-gui/blob/main/doc/img/cluster-states.png)

Figure 6: Illustration of several states of a cluster

Its inputs and outputs are ClusterPorts. Every ClusterPort corresponds to a Port belonging to a node in the cluster, but every Port belonging to one of the cluster’s nodes does not have a corresponding ClusterPort.
Ports can be separated into two types:
- internal ports: their edge links two nodes which are both in the cluster. These are not stored in the Cluster object.
- external ports: they can hold an edge linking a node belonging to the cluster, to another potential node which would not be in the cluster. These are the cluster’s inputs and outputs (ClusterPorts).
For instance, in Fig.5, Port d is an internal port, while Port a is an external port.

#### ClusterPort (inherits Port)
The ClusterPort class represents a Cluster’s external port.
It contains a ‘node port’, which is the corresponding Port belonging to one of the cluster’s nodes. For instance, in Fig.5, ‘Port a’ is the corresponding node port of the first ClusterPort.

ClusterPorts are automatically generated when creating a Cluster. Their names are automatically generated based on the corresponding node name and node port name.
Its type and edge are its node port’s type and edge, and its node is the cluster it belongs to.


#### Graph
The Graph object is the central point of the program. It contains all of the graph elements and their Qt items.

It takes care of getting any data needed on the graph using a DynamicGraphCommunication object. It then determines the graph layout thanks to DotDataGenerator, and generates the graph elements’ Qt items using JsonToQtGenerator.
The Qt interface contains the Graph object, and works alongside it to handle the display. For instance:
- the Graph object indicates to the graphical interface which Qt items to display
- when a cluster is created, the graphical interface requests the Graph to create a new Cluster object
- the graphical interface requests the Graph to refresh its content when the user wants to refresh the graph display

The Graph object contains a list for each type of nodes:
- _dg_entities: EntityNode objects
- _input_nodes: InputNode objects
- _clusters: Cluster objects

Its public methods are:
- refresh_graph_data to fetch new data from the SoT without updating the display
- generate_qt_items to generate Qt graphic items for each of its graph elements
- get_qt_items, which returns all of the graph elements’ Qt items
- get_elem_per_qt_item, which returns the graph element corresponding to the given Qt item. This is useful, for instance, when the user clicks on the graph element’s Qt item, to get the element’s information
- add_cluster, remove_cluster, and check_clusterizability which checks if the given nodes can make up a cluster

The following sections explain how the Graph class orchestrates the process of creating graphic items for each element, and how the Qt window communicates with it to make an interactive interface.

### Determination of the graph layout
‘dot’ is a program allowing its user to visualize a graph in several forms: pdf, png, svg, etc. When provided with ‘DOT code’ describing a graph, it computes a layout of this graph and displays it, as can be seen in Fig.7.

![](https://github.com/justinefricou/sot-gui/blob/main/doc/img/dot-code-graph-example.png)

Figure 7: Example of DOT code and the associated graph generated by dot

SoT GUI relies on dot to compute the graph’s layout, and handles the display of each element itself, thanks to PySide. Indeed, in addition to visual outputs such as png of pdf, dot can generate json describing the graph’s layout:
- coordinates of the elements vertices
- colors of the outlines
- background colors
- sizes and fonts of the labels
- etc

dreampuf.github.io/GraphvizOnline is a useful online tool to experiment with dot code and understand its json outputs.

graphviz.org/doc/info/lang.html to understand the DOT grammar.

graphviz.org/pdf/dotguide.pdf to know more about dot and its inputs and outputs.

To generate DOT code describing the graph, the Graph object goes through all of its elements (nodes, edges, clusters…) and adds them to a DotDataGenerator object.
This object can generate DOT code for a graph element and store it until the Graph object requests the full code describing the graph.

![](https://github.com/justinefricou/sot-gui/blob/main/doc/img/dotdatagenerator-example.png)

Figure 8: Generation of DOT code by the Graph object, using DotDataGenerator

DotDataGenerator has public methods for adding regular nodes, html nodes and edges to the code:
- add_node
- add_html_node
- add_edge

It also has methods to set graph, node, or edge [attributes](https://graphviz.org/doc/info/attrs.html). The node and edge attributes apply to any node or edge added after the attribute has been added.
When every element has been added, to get the full DOT code, use the get_dot_string or get_encoded_dot_string methods.

Nodes can be added as two different types with dot:
- regular nodes: shapes such as circles, rectangles, ect. This is used for nodes whose ports are not displayed: InputNodes, and possibly EntityNodes and Clusters in the future. See [dot documentation on node shapes](https://graphviz.org/doc/info/shapes.html) for more information.
- html nodes: html tables with one cell for each port, and one middle cell for the node label. See [dotguide](https://www.graphviz.org/pdf/dotguide.pdf), parts 2.3 and 2.4, for more information.

Because of the nodes names being used in the generated DOT code, not every character can be used in them. When instantiating an entity in the SoT, you should only use alphanumeric characters and the character ‘_’.

### Generation of the graphic items
Once the Graph object has generated the dot json output describing the graph layout and how to display every item, it uses a JsonToQtGenerator object to generate every graph element’s Qt graphic item (QGraphicsItem object).
It goes through its nodes and their ports and edges, and for each of these elements, calls the corresponding JsonToQtGenerator method (get_qt_item_for_node, get_qt_item_for_port or get_qt_item_for_edge) and stores the Qt item it returns.

Most graph elements need several QGraphicsItems in order to be displayed. For instance, an edge needs a spline, a triangle as its head, and an optional label.
A GraphElement object has only one Qt item, which contains the additional child Qt items if needed:
- an edge has a spline as its Qt item, containing its head and label as child Qt items
- a regular node has a polygon or ellipse as its Qt item, containing its label
- an html node has a polygon (rectangle) as its Qt item, containing its label. It corresponds to a single cell of the html table: the one containing the node label, usually the biggest one, in the middle column
- a port has a polygon (rectangle) as its Qt item, containing its label. It corresponds to a single cell of the html table

To understand how data is organized in dot json output, visit [this link](https://graphviz.org/docs/outputs/json/).
There is a JsonParsingUtils helper class, which formalizes the json keys and allows to filter dictionaries per key / value(s) pairs.

### Window and display of the graphic items
The MainWindow class inherits PySide QMainWindow. It contains a SoTGraphView (which inherits QGraphicsView) and a SoTGraphScene (which inherits QGraphicsScene).
The scene contains the Qt items to display, and the view provides a viewport for this scene. The main window contains the view as a central widget.
Hence, SoTGraphScene contains the Graph object and handles all communications with it, while SoTGraphView handles the events occurring on the Qt items by overriding PySide QGraphicsView events methods. MainWindow holds the various widgets: SoTGraphView, toolbars, a status bar and side panels (more details in the following section: ‘Other widgets’).

At launch and when refreshing the graph, SoTGraphScene calls the Graph’s get_qt_items method, and every Qt item is added to the scene.

There are several levels of modifying the graph display, illustrated on Fig.9 and described in the following subsections thanks to examples of application.

![](https://github.com/justinefricou/sot-gui/blob/main/doc/img/sot-gui-architecture-level-modif.png)

Figure 9: Overview of SoT GUI architecture and the various levels of modifying the graph display


#### Example 1: refreshing the graph
When the kernel’s content has been modified, to refresh the graph display, the content of the Graph object is cleared and all the process of fetching data from the SoT, computing the graph layout with dot, generating Qt items and adding them to SoTGraphScene must be repeated.
Graph methods refresh_graph_data, generate_qt_items and get_qt_items are called by SoTGraphView.

#### Example 2: creating a cluster
In this case, new data from the SoT does not have to be fetched: a Cluster object is added to the Graph object, DotDataGenerator will generate new DOT code, taking into account this new cluster. A new layout will be generated and new Qt items will be displayed.
Graph methods add_cluster, generate_qt_items and get_qt_items are called by SoTGraphView.

#### Example 3: filtering entities (not yet implemented)
If entities were to be filtered by name, type, etc, the content of the Graph object would not be impacted, but only the filtered elements would be added to the DotDataGenerator in order to compute a new layout, using only these elements. New Qt items would be created according to the new layout and added to SoTGraphView to be displayed.
A variation of Graph method update_display, which would allow the use of a filter, would be called by SoTGraphView.

#### Example 4: highlighting a graph element
Graph elements can be highlighted, for instance, when they are selected. For this, there is no need to create new Qt items: the highlighted element’s Qt item, contained in the Graph object, can be modified, and SoTGraphScene will automatically update the display.
The Qt item of the GraphElement is modified thanks to PySide methods setPen or setBrush.

### Other widgets
#### The status bar
ConnectionStatusBar inherits PySide QStatusBar. It monitors the status of the connection to the kernel and displays it:
- ‘Connected’: the SOTClient object in DynamicGraphCommunication is connected to a running kernel.
- ‘No kernel detected’: SOTClient could not detect any running kernel using the configured ports. 
- ‘Reconnection available’: a new kernel has been detected, a connection can be attempted.

At init, ConnectionStatusBar launches a thread in which the connection status is checked every x amount of time, thanks to DynamicGraphCommunication is_kernel_alive method. This thread is closed when the ConnectionStatusBar object is destroyed.

If the connection was lost and a kernel is detected again, this means the client must connect to the new kernel. This information is stored in the _reconnection_needed attribute.
If this attribute is set to True or if there is no connection, the user will not be able to refresh the graph until a successful reconnection. For this, ConnectionStatusBar has a reconnection_needed method, which returns True or False.


#### The ‘clusters panel’
The ClustersPanel class inherits PySide QDockWidget. It displays a list of the existing clusters thanks to a QListWidget.
It is created and added to MainWindow at launch, and hidden until an event triggers its appearance.

QAction objects are added to this QListWidget: they correspond to the options of the context menu, which opens when right-clicking on an item of the list. These options are:
- ‘delete’, which deletes the cluster and updates the graph display accordingly
- ‘show information’, which opens the info panel to show more information on the cluster
When the user clicks on one of these options, the text of the right-clicked QListWidgetItem (i.e the label of the cluster) is used to retrieve the Cluster object and apply the action chosen by the user to this cluster. This is why two clusters cannot have the same label.


#### The ‘info panel’
The InfoPanel class inherits PySide QDockWidget. It displays a graph element’s information, and can be opened by clicking on the element, or via the clusters panel.
It is created and added to MainWindow at launch, and hidden until an event triggers its appearance.

Every type of GraphElement having specific information to display, InfoPanel has a set of methods which format an element’s data into a dictionary: _get_entity_node_data, _get_input_node_data, _get_port_data, etc.
This dictionary can then be used by the display_element_info method to generate QLabels (for text) or QTableWidgets (for tables) and add them to a QVBoxLayout.
InfoPanel contains a resizable QScrollArea. In this scroll area is a QWidget containing this QVBoxLayout. This makes the InfoPanel scrollable and resizable.

### Tests
Pytest is used for unit tests and functional tests.

The TestQtItems class runs functional tests.
It launches a Qt application and a kernel, and creates a graph on the kernel for each test case. It then checks how many Qt items were created from the graph.
Every step is thus tested, from communicating with the kernel to the Qt item creation. Only the display of these Qt items and the user interactions are not tested.
