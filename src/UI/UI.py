import pygame,sys
import time
import os
import igraph as ig
from typing import Callable, Dict, List, Tuple

'''
This file only contains a function for initializing and handling the GUI 
'''

'''
Method that initializes the GUI. It takes as an argument the Lyon Metro graph, an informed-search pathfinding algorithm,
and a heuristic (for the algorithm)
'''
def initGUI(graph : ig.Graph, algorithm : Callable[[ig.Graph, Callable, str, str], List[str]], 
            heuristic : Callable[[ig.Graph, ig.Vertex, ig.Vertex, List[ig.Vertex], Dict[ig.Vertex, ig.Vertex]], float]):
    
    # List with the name of the stations
    names : List[str] = list(graph.vs["name"])
    
    # List with the coords of the metro stations (in the drawing plane)
    coords : List[Tuple[int]] = [(572, 240), (508, 226), (469, 216), (428, 205), (388, 194), (360, 186), (306, 190), (275, 193), (238, 197), (197, 206), (198, 230), (184, 268), (167, 295), (157, 320), (106, 526), (175, 463), (188, 432), (209, 382), (224, 342), (246, 290), (250, 258), (289, 238), (298, 211), (184, 85), (159, 138), (178, 160), (195, 181), (62, 123), (65, 157), (66, 210), (154, 250), (228, 280), (280, 308), (323, 330), (350, 343), (386, 359), (410, 379), (418, 442), (419, 494), (422, 584)]

    pygame.init()

    # Metro map size
    size = (600,607)

    # Screen object for display in screen
    screen = pygame.display.set_mode(size)

    # Images:

    # We first get the path to the images folder

    #os.chdir("..") # Decomment only if running from console!

    img_path = os.path.join(os.getcwd() + "\\img")

    print(img_path)

    # Lyon Metro map image
    metroMap = pygame.image.load(os.path.join(img_path, "map.png")).convert()

    # Start button
    startButton = pygame.image.load(os.path.join(img_path, "start.png")).convert_alpha()
    # We scale it down
    startButton = pygame.transform.scale(startButton, (100, 50))
    # We get the rect of the start button (for collision detection)
    startButtonRect = startButton.get_rect()
    # Position where the button will be blitted
    startButtonPos = (460,70)
    # We move the start button rect so it falls on top of the image
    startButtonRect = startButtonRect.move(startButtonPos)

    # Reset button
    resetButton = pygame.image.load(os.path.join(img_path, "reset.png")).convert_alpha()
    # We scale it down
    resetButton = pygame.transform.scale(resetButton, (100, 50))
    # Position where the button will be blitted
    resetButtonPos = (460,70)
    # We get the rect of the start button (for collision detection)
    resetButtonRect = resetButton.get_rect()
    # We move the reset button rect to lay on top of the image
    resetButtonRect = resetButtonRect.move(resetButtonPos)

    # Now we blit the images to the screen
    screen.blit(metroMap, (0, 0))
    screen.blit(startButton, (460, 70))

    # We set the text font
    font = pygame.font.Font('freesansbold.ttf', 25)

    # We render the texts
    text1 = font.render('Seleccione un origen', True, (0,0,0), (255,255,255))
    text2 = font.render('Seleccione un destino', True, (0,0,0), (255,255,255))
    text3 = font.render('Mostrando ruta...', True, (0,0,0), (255,255,255))

    # We update the screen
    # (flip updates the whole surface)
    pygame.display.flip()

    # UI LOOP
    phase=0
    while True:
        # phase 0: Start button hasnt been clicked
        if phase==0:
            for event in pygame.event.get():

                # If theres a click:
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    # We check if the click was in the start button
                    if startButtonRect.collidepoint(pos): # This checks if the click was inside the rectangle of the image

                        # Update the screen
                        # (blit draws an image on top of another)
                        screen.blit(metroMap, (0, 0))
                        screen.blit(text1, (300,60))

                        # We draw the circles in the metro stations
                        for i in coords:
                            pygame.draw.circle(screen,(0,0,0),i,6)
                            pygame.draw.circle(screen,(255,255,255),i,3)
                        pygame.display.flip()

                        # Phase change
                        phase=1

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

        # phase 1: Start button has been clicked. We now need to select an origin
        elif phase==1:
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONUP:
                        pos = pygame.mouse.get_pos()

                        # We iterate through all the coords
                        for i in coords:
                            # If click distance to the ith-station is less than 5, we detect a collision
                            if abs(i[0]-pos[0])<=6 and abs(i[1]-pos[1])<=6:

                                # Save origin station
                                origin = names[coords.index(i)]
                                # Origin coords
                                coordsOrigin = i
                                # Update the screen
                                screen.blit(metroMap, (0, 0))
                                screen.blit(text2, (300,60))

                                # We redraw the station points, except for the origin
                                for o in coords:
                                    pygame.draw.circle(screen,(0,0,0),o,6)
                                    pygame.draw.circle(screen,(255,255,255),o,3)

                                # We redraw the origin in a different style
                                pygame.draw.circle(screen,(0,0,0),i,7)
                                pygame.display.flip()

                                # Phase change
                                phase =2
                                break
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

        # phase 2: We now need to select a destiny
        elif phase==2:
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONUP:
                        pos = pygame.mouse.get_pos()
                        for i in coords:
                            # Collision detection
                            if abs(i[0]-pos[0])<=6 and abs(i[1]-pos[1])<=6:

                                # Save destiny station
                                destiny = names[coords.index(i)]
                                # Destiny coords
                                coordsDestiny = i
                                # Update the screen
                                screen.blit(metroMap, (0, 0))

                                # We redraw the station points, except for the destiny
                                for o in coords:
                                    pygame.draw.circle(screen,(0,0,0),o,6)
                                    pygame.draw.circle(screen,(255,255,255),o,3)

                                # We redraw the origin and the destiny in a different style
                                pygame.draw.circle(screen,(0,0,0),coordsOrigin,7)
                                pygame.draw.circle(screen,(0,0,0),coordsDestiny,7)

                                screen.blit(text3, (300,60))
                                pygame.display.flip()

                                # Phase change
                                phase=3

                                # Now we call the algorithm.
                                # It returns an intermediatePath (the steps taken by the algorithm)
                                # and a route (the final, optimal route)
                                intermediatePath, route = algorithm(graph, heuristic, origin, destiny)

                                break
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

        # phase 3: Show the algorithm steps
        elif phase==3:
            for event in pygame.event.get():
                 if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            # Draw lights until all the stations are drawn.
            # In this loop we show the intermidiate steps of the algorithm
            for station in intermediatePath:
                time.sleep(0.2) # Time between drawings of stations
                pygame.draw.circle(screen,(255, 51, 153),coords[names.index(station)],7)
                pygame.draw.circle(screen,(0,0,0),coords[names.index(station)],3)
                pygame.display.flip()
            
            # phase change
            phase=4
        
        # phase 4: Display reset button. If clicked, go to phase 1
        elif phase==4:
            # We reset the drawings
            screen.blit(metroMap, (0, 0))
            
            # We draw the (final) path
            for station in route:
                pygame.draw.circle(screen,(255, 255, 0),coords[names.index(station)],7)
                pygame.draw.circle(screen,(0,0,0),coords[names.index(station)],3)
            
            # We draw the reset button
            screen.blit(resetButton, (460, 70))

            # We update the screen
            pygame.display.flip()

            # We are now going to check if the reset button has been clicked
            for event in pygame.event.get():
                # If theres a click:
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    # We check if the click was in the reset button
                    if resetButtonRect.collidepoint(pos): # This checks if the click was inside the rectangle of the image
                        # We reset the GUI
                        screen.blit(metroMap, (0, 0))
                        screen.blit(startButton, (460, 70))
                        pygame.display.flip()
                        phase=0
                
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()