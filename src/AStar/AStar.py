import igraph as ig
from typing import Callable, Dict, List, Tuple
from copy import deepcopy

'''
This file contains a generalistic A* algorithm, and a MST heuristic
'''

'''
(auxiliar) Function that reconstructs the path from 'current' to 'start' node and dictionary indicating 
the "parent" node of each node in the path.
The path is a list "path" that contains IN ORDER (from the starting vertex to the finish vertex) the names
of the vertices from the path
'''
def getPath(cameFrom : Dict[ig.Vertex, ig.Vertex], current : ig.Vertex, start : ig.Vertex) -> List[str]:
    path = [current["name"]]
    nextVertexInPath = current
    while nextVertexInPath != start:
        # Insert at the start of the path
        path.insert(0, (cameFrom[nextVertexInPath])["name"])
        
        # Get the "parent" node
        nextVertexInPath = cameFrom[nextVertexInPath]
    
    return path

'''
Minimum Spanning Tree (MST) heuristic. It takes a graph, a starting vertex, the current vertex, and a cameFrom dictionary.
With these elements, it obtains the path from "start" to "current", excludes it from the graph, and computes the MST.
It then returns the sum of the weights of that MST
'''
def MSTHeuristic(graph : ig.Graph, start : ig.Vertex, current : ig.Vertex, openSet : List[ig.Vertex], cameFrom : Dict[ig.Vertex, ig.Vertex]):

    # First, we get the current path
    currentPath = getPath(cameFrom, current, start)

    # Now we retrieve the edges of the current path
    edges : List[Tuple[str, str]] = [(currentPath[i-1], currentPath[i]) for i in range(1,len(currentPath))]

    # Now, we create a clone of the graph
    g : ig.Graph = deepcopy(graph) # Since the graph is not too big, this shouldn't be very time expensive

    # We eliminate the edges from the copied graph
    g.delete_edges(edges)

    # Now, we get the Minimum Spanning Tree (MST)
    mst = g.spanning_tree(weights=g.es["weight"], return_tree=True)

    # Finally, we get the sum of the weights in edges of the mst
    weight_sum = sum(edge["weight"] for edge in mst.es)

    return weight_sum

'''
A* algorithm

@Params:
    * graph: weighted undirected graph to be traversed. VERTICES **MUST** INCLUDE AN ATTRIBUTE 'name', WHERE EACH NAME IS **UNIQUE**.
             EDGES **MUST** ALSO INCLUDE AN ATTRIBUTE WEIGHT
    * heuristic: heuristic function. Its a function depending on the graph, the starting vertex, the current vertex, 
                 openSet list and cameFrom dict (this is made like this so we can generalize to any heuristic function. 
                 Any possible heuristic can only be dependent on this values)
    * start_vertex: 'name' attribute of the starting vertex
    * end_vertex: 'name' attribute of the goal vertex
'''
def AStar(graph : ig.Graph, heuristic : Callable[[ig.Graph, ig.Vertex, ig.Vertex, List[ig.Vertex], Dict[ig.Vertex, ig.Vertex]], float], start_vertex : str, end_vertex : str) -> Tuple[List[str], List[str]]:

    # TODO: ANADIR COMPROBACIONES INICIALES DE Q LOS NOMBRES NO SON IGUALES ETC ETC....

    # This is a list that has all the nodes (IN ORDER) visited by the algorithm
    intermediatePath : List[str] = []

    # We first obtain the starting vertex and the goal vertex as a igraph Vertex object
    start : ig.Vertex = graph.vs.find(name=start_vertex)
    goal  : ig.Vertex = graph.vs.find(name=end_vertex) 

    # Set of discovered nodes that can be (re) explored
    openSet : List[ig.Vertex] = [start]

    # For a vertex 'n', cameFrom[n] is the node preceding it on the less expensive path from the start
    cameFrom : Dict[ig.Vertex, ig.Vertex] = dict()

    # The gScore of a node makes reference to the cost of the cheapest path from 'start' to the node
    # We implement the gScore function as a dictionary {name(string) : gScore}
    gScore : Dict[ig.Vertex, float] = {v : float('inf') for v in graph.vs} # When starting, all the nodes have an infinite gScore
    gScore[start] = 0 # The gScore of the starting node is 0

    # The fScore of a node tells us "how good" is the best path to the end if it goes through this node
    fScore : Dict[ig.Vertex, float] = {v : float('inf') for v in graph.vs} # When starting, al nodes have an infinite fScore
    fScore[start] = heuristic(graph, start, start, openSet, cameFrom)

    # While the openSet is not empty...
    while len(openSet) != 0:
        
        # Node that we are going to expand. Its the one in the openSet with the lowest fScore value
        current : ig.Vertex = min(openSet, key=fScore.get) # This gets the minimum node (key) in the dict fScore sorting by the keys (fScore.get is a method of dict that returns the value of a given key)

        intermediatePath.append(current["name"])

        if current == goal: 
            
            # Final, optimal route        
            finalRoute = getPath(cameFrom, current, start)
            
            return intermediatePath, finalRoute

        # We remove the node we are expanding from the openSet (is the same as adding to a "CLOSED LIST")
        openSet.remove(current)

        # Now, we expand the node:
        adjacent = graph.neighbors(current['name']) # Iterable object of the neighbors ID of the current vertex 
        
        for neigh in adjacent:
            
            # We get the weight of the edge connecting 'current' and 'neighbor'
            neighbor = graph.vs[neigh] # Since I only have the ID, I need to get the ig.Vertex object
            edge = graph.es[graph.get_eid(current['name'], neighbor['name'])] # We first get the edge connecting 'current' and 'neighbor'
            weight = edge['weight']

            # We calculate the new gScore for each neighbor. If its less than the one it had, then that means we found a better path to the neighbor node!
            # In that case, we update said neighbor node
            new_gScore = gScore[current] + weight
            
            if new_gScore < gScore[neighbor]:
                # We update the neighbor information with the new shortest path that goes through it
                cameFrom[neighbor] = current
                gScore[neighbor] = new_gScore
                fScore[neighbor] = new_gScore + heuristic(graph, start, neighbor, openSet, cameFrom)

                # If the neighbor wasnt in the openSet, we add it (so we can keep exploring the graph through it)
                if neighbor not in openSet:
                    openSet.append(neighbor)
    
    return [] # If we didnt find a path, we return an empty list symbolizing that there is no path