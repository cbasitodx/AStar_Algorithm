import igraph as ig
from typing import Callable, Dict, List, Tuple
from copy import deepcopy
from geopy.distance import geodesic

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
Minimum Spanning Tree (MST) heuristic. It uses a graph, a starting vertex, the current vertex, and a cameFrom dictionary.
With these elements, it obtains the path from "start" to "current", excludes it from the graph, and computes the MST.
It then returns the sum of the weights of that MST
'''
def MSTHeuristic(graph : ig.Graph, start : ig.Vertex, goal : ig.Vertex, current : ig.Vertex, openSet : List[ig.Vertex], cameFrom : Dict[ig.Vertex, ig.Vertex]):

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
Djikstra Heuristic. It uses a graph, a starting vertex, a goal vertex, the current vertex, and a cameFrom dictionary.
With these elements, it obtains the minimum path from "start" to "current", excludes it from the graph, and computes the
minimum cost path from "current" to "goal" using the Djikstra algorithm. It returns the cost of this path
'''
def djikstraHeuristic(graph : ig.Graph, start : ig.Vertex, goal : ig.Vertex, current : ig.Vertex, openSet : List[ig.Vertex], cameFrom : Dict[ig.Vertex, ig.Vertex]):
    # First, we get the current path
    currentPath = getPath(cameFrom, current, start)

    # Now we retrieve the edges of the current path
    edges : List[Tuple[str, str]] = [(currentPath[i-1], currentPath[i]) for i in range(1,len(currentPath))]

    # Now, we create a clone of the graph
    g : ig.Graph = deepcopy(graph) # Since the graph is not too big, this shouldn't be very time expensive

    # We eliminate the edges from the copied graph
    g.delete_edges(edges)

    # Now, we get the shortest path from "current" to "goal" using Djikstra's algorithm
    edges_id = g.get_shortest_paths(current, to=goal, weights=g.es["weight"], output='epath', algorithm="djikstra")[0] # This function outputs a path of edges id with the format [[...]] (thats why we index at 0)
    edges = [g.es[id] for id in edges_id] # We now get the Vertex object from the graph
    weights = [e["weight"] for e in edges] # Finally, we get the weights from the Vertex objects
    return sum(weights)

'''
Euclidean Distance. It uses the current vertex and a goal vertex.
It extracts the (real) coordinates in format (lat,long) from this vertices and then computes the geodesic distance between this points in kilometers.
We do it like this so we can consider the curvature of the earth and not just an idealised line between points in a plane
'''
def euclideanDistanceHeuristic(graph : ig.Graph, start : ig.Vertex, goal : ig.Vertex, current : ig.Vertex, openSet : List[ig.Vertex], cameFrom : Dict[ig.Vertex, ig.Vertex]):
    return geodesic((current["lat"], current["long"]), (goal["lat"], goal["long"])).km


'''
A* algorithm

@Params:
    * graph: weighted undirected graph to be traversed. VERTICES **MUST** INCLUDE AN ATTRIBUTE 'name', WHERE EACH NAME IS **UNIQUE**.
             EDGES **MUST** ALSO INCLUDE AN ATTRIBUTE WEIGHT
    * heuristic: heuristic function. Its a function depending on the graph, the starting vertex, the end vertex, the current vertex, 
                 openSet list and cameFrom dict (this is made like this so we can generalize to any heuristic function. 
                 Any possible heuristic can only be dependent on this values)
    * start_vertex: 'name' attribute of the starting vertex
    * end_vertex: 'name' attribute of the goal vertex
'''
def AStar(graph : ig.Graph, heuristic : Callable[[ig.Graph, ig.Vertex, ig.Vertex, List[ig.Vertex], Dict[ig.Vertex, ig.Vertex]], float], start_vertex : str, end_vertex : str) -> Tuple[List[str], List[str]]:

    # For simplifying computations, if the origin is the same as the destiny just return the expected answer...
    if start_vertex == end_vertex : return [start_vertex], [start_vertex]

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
    fScore[start] = heuristic(graph, start, goal, start, openSet, cameFrom)

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
                fScore[neighbor] = new_gScore + heuristic(graph, start, goal, neighbor, openSet, cameFrom)

                # If the neighbor wasnt in the openSet, we add it (so we can keep exploring the graph through it)
                if neighbor not in openSet:
                    openSet.append(neighbor)
    
    return [],[] # If we didnt find a path, we return an empty list symbolizing that there is no path

#'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''#
#              IMPLEMENTATION WITH AN OPEN AND CLOSED SET...
#'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''#

#def AStar(graph : ig.Graph, heuristic : Callable[[ig.Graph, ig.Vertex, ig.Vertex, ig.Vertex, List[ig.Vertex], Dict[ig.Vertex, ig.Vertex]], float], start_vertex : str, end_vertex : str) -> Tuple[List[str], List[str]]:
#    
#    # For simplifying computations, if the origin is the same as the destiny just return the expected answer...
#    if start_vertex == end_vertex : return [start_vertex], [start_vertex]
#
#    # This is a list that has all the nodes (IN ORDER) visited by the algorithm
#    intermediatePath : List[str] = []
#
#    # We first obtain the starting vertex and the goal vertex as an igraph Vertex object
#    start : ig.Vertex = graph.vs.find(name=start_vertex)
#    goal  : ig.Vertex = graph.vs.find(name=end_vertex) 
#
#    # Set of discovered nodes that can be (re) explored
#    openSet : List[ig.Vertex] = [start]
#
#    # Set of discovered nodes that have already been explored
#    closedSet : List[ig.Vertex] = []
#
#    # For a vertex 'n', cameFrom[n] is the node preceding it on the less expensive path from the start    
#    cameFrom : Dict[ig.Vertex, ig.Vertex] = dict()
#
#    # The gScore of a node makes reference to the cost of the cheapest path from 'start' to the node
#    # We implement the gScore function as a dictionary {name(string) : gScore}
#    gScore : Dict[ig.Vertex, float] = {v : float('inf') for v in graph.vs} # When starting, all the nodes have an infinite gScore
#    gScore[start] = 0 # The gScore of the starting node is 0
#
#    # The fScore of a node tells us "how good" is the best path to the end if it goes through this node
#    fScore : Dict[ig.Vertex, float] = {v : float('inf') for v in graph.vs} # When starting, al nodes have an infinite fScore
#    fScore[start] = heuristic(graph, start, goal, start, openSet, cameFrom)
#
#    # While the openSet is not empty...
#    while(len(openSet) != 0):
#        
#        # Node that we are going to expand. Its the one in the openSet with the lowest fScore value
#        current : ig.Vertex = min(openSet, key=fScore.get)
#
#        if current == goal: 
#            
#            # We fill the intermediate path with the names of the vertices in the closed set (the closed set contains all the visited nodes IN ORDER)
#            intermediatePath = [vertex["name"] for vertex in closedSet]
#            finalRoute = getPath(cameFrom, current, start) 
#            return intermediatePath, finalRoute
#        
#        # We remove the node we are expanding from the openSet and add it to the closedSet
#        openSet.remove(current)
#        closedSet.append(current)
#
#        # Now, we expand the node:
#        adjacent = graph.neighbors(current['name']) # Iterable object of the neighbors ID of the current vertex
#
#        for neigh in adjacent:
#
#            # We get the weight of the edge connecting 'current' and 'neighbor'
#            neighbor : ig.Vertex = graph.vs[neigh] # Since I only have the ID, I need to get the ig.Vertex object
#            edge = graph.es[graph.get_eid(current['name'], neighbor['name'])] # We first get the edge connecting 'current' and 'neighbor'
#            weight = edge['weight']
#
#            # We calculate the new gScore for each neighbor. If its less than the one it had, then that means we found a better path to the neighbor node!
#            # In that case, we update said neighbor node
#            new_gScore = gScore[current] + weight
#
#            # If the neighbor node wasnt in the openSet nor in the closedSet, this means we havent explored it. 
#            # So, we add it to the openSet and update its values
#            if (neighbor not in openSet and neighbor not in closedSet):
#                openSet.append(neighbor)
#                cameFrom[neighbor] = current
#                gScore[neighbor] = new_gScore
#                fScore[neighbor] = new_gScore + heuristic(graph, start, goal, neighbor, openSet, cameFrom)
#
#            # In this case, the node has been explored, but we found a shorter path to it
#            # So, we update the neighbor information with the new shortest path that goes through it
#            elif (neighbor in openSet and new_gScore < gScore[neighbor]):
#                cameFrom[neighbor] = current
#                gScore[neighbor] = new_gScore
#                fScore[neighbor] = new_gScore + heuristic(graph, start, goal, neighbor, openSet, cameFrom)
#
#    return [],[]