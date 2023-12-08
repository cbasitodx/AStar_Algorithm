from AStar.AStar import *
from Metro.LyonMetro import *
from UI.UI import *

'''
Main file. This is the file that should be executed
'''
if __name__ == "__main__":
    
    # First we get the Lyon Metro graph
    ly = getMetro()

    # Now, we deploy the GUI
    initGUI(ly, AStar, euclideanDistanceHeuristic) # NOTE: For changing the heuristic, just change the third argument of this function!! Nothing more is needed