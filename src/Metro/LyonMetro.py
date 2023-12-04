import igraph as ig
import pandas as pd
import os

'''
This file only holds a function for retrieving the Lyon Metro graph!
'''

'''
(private) Function for getting a list of tuples from two lists (cartesian product)
'''
def __listOfTuples(l1 : list, l2 : list) -> list:
    return list(map(lambda x, y:(x,y), l1, l2))

'''
(private) Function for connecting two stations s1 and s2 with its correspondent weight
'''
def __conex(s1 : str, s2 : str, weight : float, connections : list, weights : list):
    if((s1,s2)not in connections and (s2,s1)not in connections):
        connections.append((s1,s2))
        weights.append(weight)
    return

'''
Function for retrieving the graph
'''
def getMetro():
    LyonMetro: ig.Graph = ig.Graph() # We create an empty graph to start with

    # Now, we read the coordinates csv (this will be useful for the euclidean distance heuristic)
    # This csv contains the (lat, long) irl coordinates of every station
    coordsPath = os.path.join(os.path.dirname(__file__),"coords.csv")
    coords : pd.DataFrame = pd.read_csv(coordsPath,delimiter=",")

    # First, we read the csv delimited by ";"
    csvPath = os.path.join(os.path.dirname(__file__),"lyoncsv.csv")
    lyonDF = pd.read_csv(csvPath,delimiter =";")

    # We create a list with the names of all the stations
    names = list(lyonDF.columns[1:])

    # We create the vertices of the graph:
    LyonMetro.add_vertices(len(names))

    # We add the names of the stations (as an attribute of the vertices)
    LyonMetro.vs["name"] = names

    # We add the coordinates to the stations as attributes
    # (We need to do it in a for loop because the coords csv is not in the same order as our vertices)
    for vertex in LyonMetro.vs:
        vertex["lat"]  = coords["Lat"].loc[coords["Name"] == vertex["name"]].values[0]
        vertex["long"] = coords["Long"].loc[coords["Name"] == vertex["name"]].values[0]

    # Connections list
    connections = []

    # Weights list
    weights = []

    # Iterate through all the rows and columns of the dataframe calling conex() 
    for station in lyonDF.columns[1:]:
        tuples = __listOfTuples(names,lyonDF[station])
        for tup in tuples:
            if tup[1]!=0:
                __conex(station,tup[0],tup[1], connections, weights)

    # We add the connections to the graph
    LyonMetro.add_edges(connections)

    # We add the weights to the graph (as an attribute of the edge)
    LyonMetro.es["weight"]= weights

    return LyonMetro