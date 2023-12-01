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
    initGUI(ly, AStar, MSTHeuristic)