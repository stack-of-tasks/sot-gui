# sot-gui

This project is a Graphical User Interface for the Stack of Tasks. It allows the user to display the control graph and interact with this display to make an exhaustive and readable representation of the SoT: zoom and move on the graph, group nodes, show more information on a graph element, etc.

SoT GUI works as a client for a sot-ipython-connection kernel running on a robot processor and containing the SoT. It only allows to interact with a display of the graph: it does not modify the graph inside the kernel.


### Install
TODO


### Main features

#### Zooming in and moving on the graph
To zoom in or out on the graph, use the mouse wheel.
You can move on the graph by dragging or by using the scroll bars.

![](https://github.com/stack-of-tasks/sot-gui/blob/main/doc/justine_fricou_04-04-2022_05-08-2022/zoom.gif)

#### Clusters
SoT GUI allows you to group entities into one single node to make the graph more readable.

##### To create a cluster:
1. Click on ‘Create cluster’. This will show the clusters toolbar, to complete the group creation or cancel it.
2. Select the nodes to group by clicking on them.
A cluster must contain at least two nodes, and only directly linked nodes (i.e each node in the cluster is a child node or parent node of at least one other node of the cluster).
A cluster can contain entities or fixed values. The possibility of clusters containing clusters should be added in the future.
3. Click on ‘Confirm cluster’ to complete the creation.
4. Enter a label for the node: it can contain any character, but two nodes cannot have the same label.

##### To delete a cluster:
1. Click on ‘Manage clusters’ to open the clusters panel.
2. Right-click on the label of the cluster you want to delete.
3. Click on the ‘Delete’ option.

##### To display information on a cluster:
1. Click on ‘Manage clusters’ to open the clusters panel.
2. Right-click on the label of the cluster.
3. Click on the ‘Display informations’ option to open the info panel.

![](https://github.com/stack-of-tasks/sot-gui/blob/main/doc/justine_fricou_04-04-2022_05-08-2022/clusters.gif)


#### Displaying information on an element
You can display more information on a graph element (fixed value / entity / cluster / port / edge) by clicking on it to open the info panel.
Depending on the type of element, various data will be shown, such as its name, type, value, last execution time, cluster, signals, etc.

![](https://github.com/stack-of-tasks/sot-gui/blob/main/doc/justine_fricou_04-04-2022_05-08-2022/element_info_panel.gif)

#### Refresh / reconnect
When the content of the SoT has been modified or recomputed, the display of the graph can be refreshed.
To do this, simply click on the ‘Refresh’ button.

When the kernel has been stopped, and a new one has been launched, click on the ‘Reconnect’ button to connect to the new kernel. To display the new graph, you will have to click on the ‘Refresh’ button, as the refresh is not automatic.

Alternatively, you can click on the ‘Refresh’ button before reconnecting: a message box will appear, indicating that you need to connect to the new kernel before refreshing the graph. Click ‘Yes’, and SoT GUI will reconnect before refreshing automatically.

![](https://github.com/stack-of-tasks/sot-gui/blob/main/doc/justine_fricou_04-04-2022_05-08-2022/refresh_reconnect.gif)

#### Connection status
You can check the status of the connection with the kernel at any time thanks to the status bar at the bottom of the window. There are three cases:
- ‘Connected’: SoT GUI is connected to a running kernel.
- ‘No kernel detected’: SoT GUI could not detect any running kernel using the configured ports.
- ‘Reconnection available’: a new kernel has been detected, SoT GUI can launch a connection.

