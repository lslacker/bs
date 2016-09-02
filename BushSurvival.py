#!/usr/bin/env python
# pylint: disable=E1101, C0301, W0603

""" 

Bush Survival v0.9 - 14-07-2015
by Shaun Hedrick

A text based cross platform game written in Python 2.7

Based on a game I played in the 80's

Requires UniCurses on *nix
Windows also requires PDCurses.dll as well as UniCurses

"""

from unicurses import *
import random
import os, sys
import math
import subprocess
from time import sleep

def add_food(add, value):
    """ Add food and checks we dont go over maxval """
    global HUNGERVAL

    if add == True:
        HUNGERVAL = HUNGERVAL + value
        if HUNGERVAL > 150:
            HUNGERVAL = 150
    else:
        HUNGERVAL = HUNGERVAL - value

def add_strength(add, value):
    """ Add strength and checks we dont go over maxval """
    global STRENGTHVAL

    if add == True:
        STRENGTHVAL = STRENGTHVAL + value
        if STRENGTHVAL > 150:
            STRENGTHVAL = 150
    else:
        STRENGTHVAL = STRENGTHVAL - value

def clearscreen():
    """ Determines OS.  Issues Clear Screen command for OS """
    if os.name == 'nt':
        os.system('cls')
    elif os.name == 'posix':
        os.system('clear')
    else:
        print "Untested OS.  Please tell the developer you're on: %s" % os.name 
        sys.exit(0)

def show_movement(show_this_menu, flash):
    """ Shows the movement options, these are always static """
    if show_this_menu:
        for i in range(0, 6):
            if i != flash:
                mvaddstr(i + 7, 1, MOVES[i], color_pair(OPTIONS_COLOUR) | A_BOLD)
            else:
                mvaddstr(i + 7, 1, MOVES[i], color_pair(RED) | A_BOLD)
                refresh()
    else:
        for i in range(0, 6):
            mvaddstr(i + 7, 1, SHORT_BLANK, color_pair(BLACK) | A_BOLD)

def show_action(show_this_menu, flash):
    """ Shows action options """
    if show_this_menu:
        for i in range(0, 6):
            if i != flash:
                mvaddstr(i + 7, 15, ACTIONS[i], color_pair(OPTIONS_COLOUR) | A_BOLD)
            else:
                mvaddstr(i + 7, 15, ACTIONS[i], color_pair(RED) | A_BOLD)
                refresh()

    else:
        for i in range(0, 6):
            mvaddstr(i + 7, 15, SHORT_BLANK, color_pair(BLACK) | A_BOLD)

def show_fight(show_this_menu, flash):
    """ Shows fight options """
    if show_this_menu:
        for i in range(0, 6):
            if i != flash:
                mvaddstr(i + 7, 29, FIGHT_ACTIONS[i], color_pair(OPTIONS_COLOUR) | A_BOLD)
            else:
                mvaddstr(i + 7, 29, FIGHT_ACTIONS[i], color_pair(RED) | A_BOLD)
                refresh()
    else:
        for i in range(0, 6):
            mvaddstr(i + 7, 29, SHORT_BLANK, color_pair(BLACK) | A_BOLD) 

def show_special(show_this_menu, flash):
    """ Shows action options """
    if show_this_menu:
        for i in range(0, 6):
            if i != flash:
                mvaddstr(i + 7, 43, SPECIAL_WITH_MOVE[i], color_pair(OPTIONS_COLOUR) | A_BOLD)
            else:
                mvaddstr(i + 7, 43, SPECIAL_WITH_MOVE[i], color_pair(RED) | A_BOLD)
                refresh()

    else:
        for i in range(0, 6):
            mvaddstr(i + 7, 43, SHORT_BLANK, color_pair(BLACK) | A_BOLD)

def process_context(command):
    """ Switches the context for the user """
    global MOVEMENT
    global ACTION
    global FIGHT
    #global CURRENT_OPTIONS

    enemy = ENEMY_LIST[ZERO_BASE_PLYR_POS] # Check for enemies at the new location
    
    if HAS_COMPASS:
        DISCOVERED[ZERO_BASE_PLYR_POS] = "Y"

    if enemy != 4:
        MOVEMENT = False
        ACTION = False
        FIGHT = True
        show_action(False, 10)
        show_movement(False, 10)
        show_special(False, 10)
        show_fight(True, 10)
        fight(enemy, command)

    elif MOVEMENT:
        MOVEMENT = False
        ACTION = True
        FIGHT = False
        show_fight(False, 10)
        show_movement(False, 10)
        show_special(False, 10)
        show_action(True, 10)

    else:
        MOVEMENT = True
        ACTION = False
        FIGHT = False
        show_fight(False, 10)
        show_action(False, 10)
        show_movement(True, 10)
        show_special(True, 10)

    #clear_messages(0)
    update_player_on_map()


def add_score(score):
    """ Add score and updates display """
    global SCORE
    SCORE = SCORE + score
    # update the display
    mvaddstr(1, 2, "Score:", color_pair(HEADING_COLOUR) | A_BOLD)
    mvaddstr(1, 9, "%d" % SCORE, color_pair(TEXT_COLOUR) | A_BOLD)

def show_ground_feature():
    """ Displays the surrounding of the player """
    ground_description_int = GROUND_FEATURES_LIST[ZERO_BASE_PLYR_POS]
    mvaddstr(16, 3, GROUND_DESCRIPTIONS.get(ground_description_int), color_pair(GROUND_FEATURES_COLOUR) | A_BOLD)

def add_move():
    """ Updates total move count """
    global TOTAL_MOVES
    TOTAL_MOVES = TOTAL_MOVES + 1
    mvaddstr(1, 16, "Moves:", color_pair(HEADING_COLOUR) | A_BOLD)
    mvaddstr(1, 23, "%d" % TOTAL_MOVES, color_pair(TEXT_COLOUR) | A_BOLD)

def change_weapon(weapon):
    """ Changes the primary weapon display """
    mvaddstr(1, 30, "Weapon:                    ", color_pair(HEADING_COLOUR) | A_BOLD)
    mvaddstr(1, 38, "%s" % weapon, color_pair(TEXT_COLOUR) | A_BOLD)

def update_hunger(flash):
    """ Updates hunger display """
    mvaddstr(3, 2, "Hunger:", color_pair(HEADING_COLOUR) | A_BOLD)
    if flash:
        mvaddstr(3, 10, "%s" % HUNGER, color_pair(WARNING_COLOUR) | A_BOLD | A_BLINK)
    else:
        mvaddstr(3, 10, "%s" % HUNGER, color_pair(HUNGER_COLOUR) | A_BOLD)

def update_strength(flash):
    """ Updates strength display """
    mvaddstr(3, 30, "Strength:", color_pair(HEADING_COLOUR) | A_BOLD)
    if flash:
        mvaddstr(3, 40, "%s" % STRENGTH, color_pair(WARNING_COLOUR) | A_BOLD | A_BLINK)
    else:
        mvaddstr(3, 40, "%s" % STRENGTH, color_pair(STRENGTH_COLOUR) | A_BOLD)

def checkhealth(currentstrength, currenthunger):
    """ Does the health checks """
    global HUNGER
    global STRENGTH
    flash = False
    grizzly_text = ""

    if currentstrength <= 0:
        if FIGHT:
            if GRIZZLY_BEAR:
                grizzly_text = "grizzly "
            printmessage("The %sbear has killed you." % grizzly_text, 7, MAGENTA, 2)
        else:
            printmessage("You have died from severe exhaustion.", 5, RED, 2)
        die('tooweak')

    for i in range(0, 5):  
        strengthrange = (79, 59, 39, 19, 0)
        if currentstrength in range(strengthrange[i], strengthrange[i] + 20):
            STRENGTH = STRENGTH_TEXT[i]
        if currentstrength > 99:
            STRENGTH = STRENGTH_TEXT[0]
    if currentstrength <= 19: 
        flash = True
    update_strength(flash)
    flash = False # Make sure flash isnt incorrectly set for hunger too

    if currenthunger <= 0:
        printmessage("You have died from malnutrition.", 5, RED, 2)
        die('starved')

    for i in range(0, 5):  
        hungerrange = (79, 59, 39, 19, 0)
        if currenthunger in range(hungerrange[i], hungerrange[i] + 20): 
            HUNGER = HUNGER_TEXT[i]
        if currenthunger > 99:
            HUNGER = HUNGER_TEXT[0]
    if currenthunger <= 19: 
        flash = True
    update_hunger(flash)

def update_title_area(title):
    """ Updates title display """
    mvaddstr(12, 58, "%s" % title, color_pair(TITLE_COLOUR) | A_BOLD) 

def make_screen():
    """ Makes the map """
    # Draw the map
    
    # for i in range(1, 100000):
    #     c = random.randrange(0, 9)
    #     l = random.randrange(3, 6)
    #     w = random.randrange(3, 6)
    #     x = random.randrange(1,15)
    #     y = random.randrange(1, 15)
    #             drawbox(l, w, x, y, c)
    # drawbox(, 12, 0, 0, c)

    drawbox(2, 15, 0, 0)     # Score Box
    drawbox(2, 15, 14, 0)    # Moves box
    drawbox(2, 30, 28, 0)    # Weapon box
    drawbox(11, 23, 57, 0)   # Map box
    drawbox(2, 58, 0, 2)     # Hunger/Strength Area
    drawbox(2, 15, 0, 4)     # Movement Box
    drawbox(2, 15, 14, 4)    # Survival Box
    drawbox(2, 15, 28, 4)    # Battle Box
    drawbox(2, 16, 42, 4)    # Sepcial Box    
    drawbox(7, 15, 0, 6)     # Movement Options
    drawbox(7, 15, 14, 6)    # Survival Options
    drawbox(7, 15, 28, 6)    # Battle Options
    drawbox(7, 16, 42, 6)    # Special Options
    drawbox(2, 23, 57, 11)   # Little box under map
    drawbox(9, 80, 0, 13)    # Main message area

    # Add the intersectors
    mvaddch(0, 14, ACS_TTEE, color_pair(BORDER_COLOUR) | A_BOLD)
    mvaddch(0, 28, ACS_TTEE, color_pair(BORDER_COLOUR) | A_BOLD)
    mvaddch(0, 57, ACS_TTEE, color_pair(BORDER_COLOUR) | A_BOLD)
    mvaddch(2, 0, ACS_LTEE, color_pair(BORDER_COLOUR) | A_BOLD)
    mvaddch(2, 14, ACS_BTEE, color_pair(BORDER_COLOUR) | A_BOLD)
    mvaddch(2, 28, ACS_BTEE, color_pair(BORDER_COLOUR) | A_BOLD)
    mvaddch(2, 57, ACS_RTEE, color_pair(BORDER_COLOUR) | A_BOLD)
    mvaddch(4, 0, ACS_LTEE, color_pair(BORDER_COLOUR) | A_BOLD)
    mvaddch(4, 14, ACS_TTEE, color_pair(BORDER_COLOUR) | A_BOLD)
    mvaddch(4, 28, ACS_TTEE, color_pair(BORDER_COLOUR) | A_BOLD)
    mvaddch(4, 42, ACS_TTEE, color_pair(BORDER_COLOUR) | A_BOLD)
    mvaddch(4, 57, ACS_RTEE, color_pair(BORDER_COLOUR) | A_BOLD)
    mvaddch(6, 0, ACS_LTEE, color_pair(BORDER_COLOUR) | A_BOLD)
    mvaddch(6, 14, ACS_PLUS, color_pair(BORDER_COLOUR) | A_BOLD)
    mvaddch(6, 28, ACS_PLUS, color_pair(BORDER_COLOUR) | A_BOLD)
    mvaddch(6, 42, ACS_PLUS, color_pair(BORDER_COLOUR) | A_BOLD)
    mvaddch(6, 57, ACS_RTEE, color_pair(BORDER_COLOUR) | A_BOLD)
    mvaddch(11, 57, ACS_LTEE, color_pair(BORDER_COLOUR) | A_BOLD)
    mvaddch(11, 79, ACS_RTEE, color_pair(BORDER_COLOUR) | A_BOLD)
    mvaddch(13, 0, ACS_LTEE, color_pair(BORDER_COLOUR) | A_BOLD)
    mvaddch(13, 14, ACS_BTEE, color_pair(BORDER_COLOUR) | A_BOLD)
    mvaddch(13, 28, ACS_BTEE, color_pair(BORDER_COLOUR) | A_BOLD)
    mvaddch(13, 42, ACS_BTEE, color_pair(BORDER_COLOUR) | A_BOLD)
    mvaddch(13, 57, ACS_BTEE, color_pair(BORDER_COLOUR) | A_BOLD)
    mvaddch(13, 79, ACS_RTEE, color_pair(BORDER_COLOUR) | A_BOLD)

    # Draw static area titles
    mvaddstr(5, 3, "Movement", color_pair(HEADING_COLOUR) | A_BOLD)
    mvaddstr(5, 17, "Survival", color_pair(HEADING_COLOUR) | A_BOLD)
    mvaddstr(5, 32, "Battle", color_pair(HEADING_COLOUR) | A_BOLD)
    mvaddstr(5, 46, "Special", color_pair(HEADING_COLOUR) | A_BOLD)

    # Initialise other values
    add_score(0)
    add_move()
    show_movement(True, 10)
    show_special(True, 10)
    change_weapon("Swiss Army Knife")
    update_strength(False)
    update_hunger(False)
    update_title_area("  Bush Survival: Oz")


    for i in range(0, 100):  # need an extra number of both ends of the range

        DISCOVERED.append('N')
        #MAPLIST.append(str(i)) # Debug, prints numbers on the map
        MAPLIST.append('.') 
        
        # Add food
        if i in range(0, 54):
            FOOD_LIST.append(random.randrange(0, 4))
        if i == 54:
            FOOD_LIST.append(5) # Beef Jerky #1
        if i == 55:
            FOOD_LIST.append(5) # Beef Jerky #2
        if i in range(56, 100):
            FOOD_LIST.append(int(len(FOODTYPES) - 1)) # No food here

        # Add ground features
        if i in range(0, 10):
            GROUND_FEATURES_LIST.append(1) #
        if i in range(10, 20):
            GROUND_FEATURES_LIST.append(2) # 
        if i in range(20, 30):
            GROUND_FEATURES_LIST.append(3) # 
        if i in range(30, 40):
            GROUND_FEATURES_LIST.append(5) # 
        if i in range(40, 50):
            GROUND_FEATURES_LIST.append(6) # 
        if i in range(50, 60):
            GROUND_FEATURES_LIST.append(7) # 
        if i in range(60, 70):
            GROUND_FEATURES_LIST.append(8) # 
        if i in range(70, 80):
            GROUND_FEATURES_LIST.append(9) # Gum trees
        if i in range(80, 94):
            GROUND_FEATURES_LIST.append(10) # Water
        if i in range(94, 99):
            GROUND_FEATURES_LIST.append(11) # Big trees
        if i == 99:
            GROUND_FEATURES_LIST.append(12) # The ranger station

        # Add items
        if i in range(0, len(ITEMTYPES) - 1): # -1 cuts off the compass
            ITEM_LIST.append(i)
        if i in range(len(ITEMTYPES) - 1, 100):
            ITEM_LIST.append(int(len(ITEMTYPES) - 2)) # -2 = "None" No items here

        # Add bears and Ivan Milat
        if i in range(0, 16):
            ENEMY_LIST.append(1) # Bears # xxx change to 4 to disable bears
        if i == 16:
            ENEMY_LIST.append(2) # Grizzly Bear
        if i == 17:
            ENEMY_LIST.append(3) # Ivan Milat
        if i in range(18, 100):
            ENEMY_LIST.append(4) # No enemy here

    random.shuffle(FOOD_LIST)
    random.shuffle(ITEM_LIST)
    random.shuffle(ENEMY_LIST)
    random.shuffle(GROUND_FEATURES_LIST)
    build_compass_map()
    
    update_player_on_map()

    ITEM_LIST[ZERO_BASE_PLYR_POS] = int(len(ITEMTYPES) - 1) # Place compass at player start

def build_compass_map():
    """ Build the hidden compass map """

    for i in range(0, 100):
        # Add bears
        if ENEMY_LIST[i] == 1:
            HAS_COMPASS_MAP.append(COMPASS_DICT[3])
        # Add Grizzly bear
        elif ENEMY_LIST[i] == 2:
            HAS_COMPASS_MAP.append(COMPASS_DICT[4])
        # Add water spots
        elif GROUND_FEATURES_LIST[i] == 10:
            HAS_COMPASS_MAP.append(COMPASS_DICT[1])
        # Add Big Trees
        elif GROUND_FEATURES_LIST[i] == 11:
            HAS_COMPASS_MAP.append(COMPASS_DICT[2])
        # Add nothings
        else:
            HAS_COMPASS_MAP.append(COMPASS_DICT[5])

def update_player_on_map():
    """ Draws the whole map and calls get_map_line for the line """
    
    # Get's a constructed whole line from get_map_line()
    # Splits it and writes it one by one
    # Colours red if user has compass, and has previously discovered that position

    positions = (59, 61, 63, 65, 67, 69, 71, 73, 75, 77) # x coords of map tiles
    
    for i in range(1, 11):
        mapline = get_map_line(i)
  
        for mapdot in range(0, 10):                    # Split map line into 10 parts, and write them one by one
            whole_map_pos = ((i * 10) - 10) + mapdot   # Use i to iterate through all the map lines
            if DISCOVERED[whole_map_pos] == "Y":       # Fancy maths, works well for 10 x 10 grid
                mvaddstr(i, 59 + (mapdot * 2), mapline[mapdot], color_pair(DISCOVERED_MAP_COLOUR))
            else:
                mvaddstr(i, 59 + (mapdot * 2), mapline[mapdot], color_pair(MAP_COLOUR))        
        
        if LAST_LINE_HAD_PLYR: # Write the players avatar, and colour the players spot 
            mvaddstr(i, positions[ZBPP], "U", color_pair(PLAYER_COLOUR) | A_BOLD)

def get_map_line(line):
    """ Generates a map line and passes back to update_player_on_map() """
    global ZBPP 
    global LAST_LINE_HAD_PLYR
    positions = (0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100)
    mapline = ""

    startpos = positions[line - 1]
    endpos = positions[line]
    ZBPP = 0
    loopcount = 0
    LAST_LINE_HAD_PLYR = False

    for i in range(startpos, endpos):
        if HAS_COMPASS and DISCOVERED[i] == "Y":
            mapline = mapline + HAS_COMPASS_MAP[i]
        else:
            mapline = mapline + MAPLIST[i] 

        if i == ZERO_BASE_PLYR_POS:
            LAST_LINE_HAD_PLYR = True
            ZBPP = loopcount
        loopcount += 1 

    return mapline # pass the constructed mapline back

def user_exit():
    """ Processes user exit """
    global VALID_MOVE

    show_action(True, 5)
    printmessage("Are you sure you want to exit? (y/n)", 5, RED, 0)
    exitval = getch()
    if exitval == ord('y'):
        printmessage("The journey is too much for you.", 5, RED, 2)
        die('normalexit')
    else:
        clear_messages(0)
        show_action(True, 10)
        VALID_MOVE = False
        return False

def drawbox(length, width, xstart, ystart):
    """ Draws boxes to speed up initial dev time """
    # curses takes y,x not x,y
    # Make the top left corner
    mvaddch(ystart, xstart, ACS_ULCORNER, color_pair(BORDER_COLOUR) | A_BOLD)
    # Draw the top side
    for i in range(0, width - 1):
        mvaddch(ystart, xstart + 1 + i, ACS_HLINE, color_pair(BORDER_COLOUR) | A_BOLD)
    #Make the top right corner
    mvaddch(ystart, xstart + width - 1, ACS_URCORNER, color_pair(BORDER_COLOUR) | A_BOLD)
    # Draw the left side
    for i in range(1, length):
        mvaddch(ystart + i, xstart, ACS_VLINE, color_pair(BORDER_COLOUR) | A_BOLD)
    # Draw the right side
    for i in range(1, length):
        mvaddch(ystart + i, xstart + width - 1, ACS_VLINE, color_pair(BORDER_COLOUR) | A_BOLD)
    # Make the bottom left corner
    mvaddch(ystart + length, xstart, ACS_LLCORNER, color_pair(BORDER_COLOUR) | A_BOLD)
    # # Draw the bottom side
    for i in range(0, width - 1):
        mvaddch(ystart + length, xstart + 1 + i, ACS_HLINE, color_pair(BORDER_COLOUR) | A_BOLD)
    # # Make the bottom left corner
    mvaddch(ystart + length, xstart + width - 1, ACS_LRCORNER, color_pair(BORDER_COLOUR) | A_BOLD)
    refresh()        

def within_boundaries(move):
    """ make sure user is in the map boundaries, if not, disallow the move """
    if move == ord('w') and ZERO_BASE_PLYR_POS in range(0, 10):
        return False
    elif move == ord('s') and ZERO_BASE_PLYR_POS in range(90, 100):
        return False
    elif move == ord('a') and ZERO_BASE_PLYR_POS in range(0, 91, 10):
        return False
    elif move == ord('d') and ZERO_BASE_PLYR_POS in range(9, 100, 10):    
        return False
    else:
        return True

def move_player(direction):
    """ Moves the player on the map """
    global ZERO_BASE_PLYR_POS
    if direction == "north":
        ZERO_BASE_PLYR_POS -= 10
    elif direction == "south":
        ZERO_BASE_PLYR_POS += 10
    elif direction == "west":
        ZERO_BASE_PLYR_POS -= 1
    elif direction == "east":
        ZERO_BASE_PLYR_POS += 1
    
    sleep(0.5) # all moves have a 0.5 second delay
    
    show_ground_feature()

def processinput(command):
    """ Processes user input """
    global VALID_MOVE
    global UP_TREE

    if MOVEMENT:
        VALID_MOVE = False
        if command in (ord('w'), ord('a'), ord('s'), ord('d'), ord('u'), ord('r'), ord('h'),) and UP_TREE:
            printmessage("But you're up a tree, you must climb down first!", 5, RED, 2)
            show_movement(True, 10)
            return 
        if command == ord('w'): # Up
            if within_boundaries(command):
                show_movement(True, 0) # Highlight chosen option
                move_player("north")
            else:
                printmessage("The forest becomes impassable in this direction.", 2, GREEN, 0)
                printmessage("You wisely decide not to venture into it.", 3, GREEN, 0)
                clear_messages(2)
                return
        elif command == ord('s'): # Down
            if within_boundaries(command):
                show_movement(True, 2) # Highlight chosen option
                move_player("south")  
            else:
                printmessage("Woah!  One more step and you would have fallen down the", 2, GREEN, 0)
                printmessage("steep cliff face, to your death.  You stop short of suicide.", 3, GREEN, 0)
                clear_messages(2)
                return
        elif command == ord('a'): # Left
            if within_boundaries(command):
                show_movement(True, 1) # Highlight chosen option
                move_player("west")
            else:
                printmessage("You approach the face of the mountain.  The climb is almost", 2, GREEN, 0)
                printmessage("vertical.  Without climbing gear, there is no way to scale it.", 3, GREEN, 0)
                clear_messages(2)
                return
        elif command == ord('d'): # Right
            if within_boundaries(command):
                show_movement(True, 3) # Highlight chosen option
                move_player("east")
            else:
                printmessage("Passing through the dense foilage you almost trip on an exposed tree root", 2, GREEN, 0)
                printmessage("and fall into the crocodile infested river.  You carefully retreat.", 3, GREEN, 0)
                clear_messages(2)
                return
        elif command == ord('u'): # Up a tree
            show_movement(True, 4) # Highlight chosen option
            if GROUND_FEATURES_LIST[ZERO_BASE_PLYR_POS] != 11:
                printmessage("There are no trees here that you can climb.", 5, CYAN, 1)
                VALID_MOVE = False
                show_movement(True, 10)
                return
            else:
                climb_tree()
                show_movement(True, 10)
                return
            # Bug here, this shouldnt count as a move
        elif command == ord('j'): # Up a tree
            show_movement(True, 5) # Highlight chosen option
            if not UP_TREE:
                printmessage("But you're not up a tree!", 5, CYAN, 1)
                VALID_MOVE = False
                show_movement(True, 10)
                return
            else:
                if fifty_fifty() == 1:
                    printmessage("You safely climb down the tree.", 5, GREEN, 2)
                else:
                    printmessage("You slip, fall off the tree and land on your head!", 5, RED, 2)
                    add_strength(False, 10)
                UP_TREE = False
                show_movement(True, 10)
                VALID_MOVE = False # stop context from changing
                add_score(5)
                time_keeper(True)
                add_move()
                show_weather()
                show_ground_feature()
                return
        elif command == ord('r'): # Remain/Stay here
            show_special(True, 1)
            printmessage("You decide to stay put.", 5, CYAN, 1)
        elif command == ord('h'): # Heal
            show_special(True, 0)
            if GROUND_FEATURES_LIST[ZERO_BASE_PLYR_POS] == 10: # Fresh Water spot
                add_food(True, 5)
                add_strength(True, 5)
                printmessage("The fresh water satisfies your hunger as well, whilst you heal.", 5, MAGENTA, 0)
            else:
                add_strength(True, 5)
                printmessage("You stop and take the time to heal, your strength improves.", 5, MAGENTA, 0)
            if HAS_FIRST_AID_KIT:
                printmessage("Your First Aid Kit speeds your recovery!", 6, MAGENTA, 0)
                add_strength(True, 20)
            VALID_MOVE = False # stop context from changing
            clear_messages(2.5)
            add_score(10)
            time_keeper(True)
            show_special(True, 10) # reset the red highlighted option back to white
            add_move()
            show_weather()
            show_ground_feature()
            return # dont let context change for a heal
        else:
            # Do nothing but refresh the screen 
            VALID_MOVE = False
            if command == ord('p'): # Debug
                printdebug()
            return
        VALID_MOVE = True
        add_move()
        process_context("None")

    elif ACTION:
        if command == ord('f'): # Find Food
            show_action(True, 1)
            checkforfood(ZERO_BASE_PLYR_POS)
        elif command == ord('l'): # Look for items
            show_action(True, 0)
            checkforitems(ZERO_BASE_PLYR_POS)
        elif command == ord('h'):
            show_action(True, 2)
            show_hint()
        elif command == ord('i'): # show items
            show_action(True, 3)
            show_item_list()
            VALID_MOVE = False
            show_action(True, 10)
            return
        elif command == ord('y'): # Exit game
            show_action(True, 4)
            yell()
        elif command == ord('q'): # Exit game
            if not user_exit():
                return
        else:
            VALID_MOVE = False
            if command == ord('p'): # Debug
                printdebug()
            elif command == ord('c'): # Debug
                #clear_messages(0)
                pass
            return

        VALID_MOVE = True
        add_move()
        process_context("None")  

    elif FIGHT:
        if not command in (ord('f'), ord('o'), ord('r'), ord('s')): # Fight, Offer food, Run Away
            VALID_MOVE = False
            return
        else:
            process_context(command)

def climb_tree():
    """ Climbs the tree and shows the view """
    global UP_TREE
    westdesc = ""
    eastdesc = ""
    northdesc = ""
    southdesc = ""
    UP_TREE = True
    westinvalid = False
    eastinvalid = False
    northinvalid = False
    southinvalid = False


    printmessage("You climb the large tree to get a look at your surroundings.", 5, MAGENTA, 2)

    if ZERO_BASE_PLYR_POS in range(0, 10):
        northinvalid = True
    if ZERO_BASE_PLYR_POS in range(90, 100):
        southinvalid = True
    if ZERO_BASE_PLYR_POS in range(0, 91, 10):
        eastinvalid = True
    if ZERO_BASE_PLYR_POS in range(9, 100, 10):
        westinvalid = True
    
    if not westinvalid: 
        westpos = GROUND_FEATURES_LIST[ZERO_BASE_PLYR_POS - 1]
        if HAS_COMPASS: 
            DISCOVERED[ZERO_BASE_PLYR_POS + 1] = "Y"
        if westpos == 10: # Water
            westdesc = TREE_VIEWS[2]
        else:
            westdesc = TREE_VIEWS[1]

        westpos = ENEMY_LIST[ZERO_BASE_PLYR_POS - 1]
        if westpos == 1:
            westdesc = TREE_VIEWS[3]
        elif westpos == 2:
            westdesc = TREE_VIEWS[4]
    else:
        westdesc = TREE_VIEWS[5]

    if not eastinvalid:
        eastpos = GROUND_FEATURES_LIST[ZERO_BASE_PLYR_POS + 1]
        if HAS_COMPASS:
            DISCOVERED[ZERO_BASE_PLYR_POS - 1] = "Y"
        if eastpos == 10: # Water
            eastdesc = TREE_VIEWS[2]
        else:
            eastdesc = TREE_VIEWS[1]

        eastpos = ENEMY_LIST[ZERO_BASE_PLYR_POS + 1]
        if eastpos == 1:
            eastdesc = TREE_VIEWS[3]
        elif eastpos == 2:
            eastdesc = TREE_VIEWS[4]
    else:
        eastdesc = TREE_VIEWS[6]


    if not northinvalid:
        northpos = GROUND_FEATURES_LIST[ZERO_BASE_PLYR_POS - 10]
        if HAS_COMPASS:
            DISCOVERED[ZERO_BASE_PLYR_POS - 10] = "Y"
        if northpos == 10: # Water
            northdesc = TREE_VIEWS[2]
        else:
            northdesc = TREE_VIEWS[1]

        northpos = ENEMY_LIST[ZERO_BASE_PLYR_POS - 10]
        if northpos == 1: # bear
            northdesc = TREE_VIEWS[3]
        elif northpos == 2: # grizzly
            northdesc = TREE_VIEWS[4]
    else:
        northdesc = TREE_VIEWS[7]


    if not southinvalid:
        southpos = GROUND_FEATURES_LIST[ZERO_BASE_PLYR_POS + 10]
        if HAS_COMPASS:
            DISCOVERED[ZERO_BASE_PLYR_POS + 10] = "Y"
        if southpos == 10: # Water
            southdesc = TREE_VIEWS[2]
        else:
            southdesc = TREE_VIEWS[1]

        southpos = ENEMY_LIST[ZERO_BASE_PLYR_POS + 10]
        if southpos == 1: # bear
            southdesc = TREE_VIEWS[3]
        elif southpos == 2: # grizzly
            southdesc = TREE_VIEWS[4]
    else:
        southdesc = TREE_VIEWS[8]

    clear_messages(0)
    printmessage("West:  " + westdesc, 2, GREEN, 0)
    printmessage("East:  " + eastdesc, 3, YELLOW, 0)
    printmessage("North: " + northdesc, 4, CYAN, 0)
    printmessage("South: " + southdesc, 5, MAGENTA, 0)
    #show_movement(True, 10)
    update_player_on_map()
    pause_for_keypress()
    clear_messages(0)

def show_hint():
    """ Shows game hints """
    global NUM_HINTS

    if NUM_HINTS == 2:
        printmessage("Sorry, only 2 hints per game!", 5, CYAN, 1)
    else:
        i = random.randrange(0, len(HINT_LIST))
        printmessage("Hint: " + HINT_LIST[i], 5, MAGENTA, 2)
        NUM_HINTS += 1

def yell():
    """ Yells and ends game if at the ranger ranch location """
    ground_description_int = GROUND_FEATURES_LIST[ZERO_BASE_PLYR_POS]
    if ground_description_int != 12:
        printmessage("You yell, but nobody hears you.", 5, CYAN, 1)
    else:
        printmessage("You have found the ranger, amd won the game!", 5, GREEN, 3)
        die("ranger")

def show_item_list():
    """ Shows the items the user has in the main window """
    # 3 items per line
    line = []
    linecounter = 0
    item_string = ""
    counter = 0
    text_spacer = 20
    clear_messages(0)

    for i in range(0, len(ITEMS)):
        space = text_spacer - len(ITEMS[i])
        item_string = item_string + ITEMS[i] + (' ' * space)
        counter += 1
        if counter == 3:
            line.append(item_string)
            linecounter += 1
            item_string = ""
            counter = 0
    if counter < 3:
        line.append(item_string)

    for i in range(0, linecounter + 1):
        printmessage(line[i], i + 1, MAGENTA, 0)
    clear_messages(3)

def force_move():
    """ Forces a move up or down when running away from an enemy """
    if ZERO_BASE_PLYR_POS in range(0, 10):
        # we cant go up, so go down
        move_player("south")
    else:
        move_player("north")

def fifty_fifty():
    """ 0 = no 1 = yes """
    chance = random.randrange(0, 2)
    return chance

def one_in_three():
    """ 0, 2 = no, 1 = yes """
    chance = random.randrange(0, 3)
    return chance

def one_in_four():
    """ 0, 2, 3 = no, 1 = yes """
    chance = random.randrange(0, 4)
    return chance

def printdebug():
    """ Prints some debug """
    printmessage("ITEM_LIST Count: %d FOOD_LIST Count %d" % (len(ITEM_LIST), len(FOOD_LIST)), 1, BLUE, 0)
    printmessage("ITEMTYPES Count: %d ENEMY Count: %d" % (len(ITEMTYPES), len(ENEMY_LIST)), 2, BLUE, 0)
    printmessage("ZB: %s" % ZERO_BASE_PLYR_POS, 3, BLUE, 0)
    printmessage("HAS_FLASHLIGHT: %s HAS_RAINCOAT %s" % (str(HAS_FLASHLIGHT), str(HAS_RAINCOAT)), 4, BLUE, 0)
    printmessage("HAS_WATCH: %s HAS_FIRST_AID_KIT %s" % (str(HAS_WATCH), str(HAS_FIRST_AID_KIT)), 5, BLUE, 0)
    printmessage("STRENGTH: %d HUNGER: %d" % (STRENGTHVAL, HUNGERVAL), 6, BLUE, 0)
    printmessage("NICE_WEATHER: %s" % NICE_WEATHER, 7, BLUE, 0)
    printmessage("8", 8, BLUE, 0)


def checkforfood(curpos):
    """ Checks if there is food at the current position """
    if DARK and not HAS_FLASHLIGHT:
        printmessage("But you can't see a thing!", 5, MAGENTA, 2) # was 2
        return

    if FOOD_LIST[curpos] != 6:
        printmessage("You found some %s here." % FOODTYPES[FOOD_LIST[curpos]], 5, MAGENTA, 0) # was 2
        addnourishment(FOOD_LIST[curpos])
        FOOD_LIST[curpos] = (int(len(FOODTYPES) - 1)) 
        pause_for_keypress()
    else:
        printmessage("You scrounge around for food, but there is nothing edible here.", 5, CYAN, 2) # was 2


def checkforitems(curpos):
    """ Checks for items at the current position """
    if DARK and not HAS_FLASHLIGHT:
        printmessage("But you can't see a thing!", 5, MAGENTA, 2) # was 2
        return

    if ITEM_LIST[curpos] != int(len(ITEMTYPES) - 2): # if the item at curpos isnt 'None'
        printmessage("You found a %s!" % ITEMTYPES[ITEM_LIST[curpos]], 5, MAGENTA, 0)
        add_score(50)
        additemtoinventory(ITEM_LIST[curpos]) # funtion removes item from map
        pause_for_keypress()
    else:
        printmessage("You look around, and find nothing", 5, CYAN, 2)


def reset_fight():
    """ Resets values after a fight """
    global FIGHT
    global BEARSTRENGTHVAL
    global MOVEMENT
    global ACTION
    global VALID_MOVE
    global FIGHTMOVES
    global GRIZZLY_BEAR

    FIGHT = False
    #ENEMY_LIST[ZERO_BASE_PLYR_POS] = len(ENEMY_LIST) # Last item is always None
    ENEMY_LIST[ZERO_BASE_PLYR_POS] = 4
    FIGHTMOVES = 0
    VALID_MOVE = True
    BEARSTRENGTHVAL = 100
    MOVEMENT = False
    ACTION = True
    GRIZZLY_BEAR = False
    process_context("None")


def fight(enemy, command):
    """ Manages the fight """
    global FIGHTMOVES
    global BEARSTRENGTHVAL
    global GRIZZLY_BEAR

    grizzly_text = "" # debug
    clear_messages(0) # Should clear weather and ground descrptions
    update_player_on_map() # fix for screen not updating before messages displayed
    refresh()

    if enemy == 2: # Set special variables for the grizzly
        GRIZZLY_BEAR = True
        BEARSTRENGTHVAL = 200
        grizzly_text = "grizzly "
        enemy = 1

    if enemy == 1: # Bears
        if FIGHTMOVES == 0:
            if GRIZZLY_BEAR:
                printmessage("Oh no!  It's the ferocious grizzly bear!", 1, RED, 0)
                printmessage("He's big and mean, and looks really mad!!", 2, RED, 0) # Needs fight development
            else:
                printmessage("Suddenly, without warning, a bear jumps out", 1, RED, 0) 
                printmessage("from behind a tree and attacks you!", 2, RED, 0)
            #clear_messages(2)
            sleep(0.5) # slight delay before revealing who gets first hit
            if HAS_BEARTRAP:
                BEARSTRENGTHVAL = BEARSTRENGTHVAL - 50
                printmessage("But the bear gets caught in your bear trap, it worked like a charm!", 4, MAGENTA, 0)
            elif fifty_fifty() == 1: # Who gets the first hit?
                printmessage("But, you hit him first with your %s!" % ITEMS[0], 4, RED, 0)
                BEARSTRENGTHVAL = BEARSTRENGTHVAL - weapon_strength(ITEMS[0])
            else:
                printmessage("And, he hits you with his big paws first!", 4, RED, 0)
                add_strength(False, 20)
            #printmessage("                          Get ready to rumble!", 8, RED, 0)
            pause_for_keypress()
        else:
            #clear_messages(0)
            pass

        if FIGHTMOVES >= 0:
            FIGHTMOVES = FIGHTMOVES + 1
            printmessage("Fight moves: %d" % FIGHTMOVES, 1, YELLOW, 0)
            if command == ord('f'):
                if fifty_fifty() == 1: # Hit
                    printmessage("The %sbear swiped at you, and hit!" % grizzly_text, 3, RED, 0)
                    add_strength(False, 20)
                else:
                    printmessage("The %sbear swipes at you, but misses!" % grizzly_text, 3, BLUE, 0)
                if fifty_fifty() == 1: # Hit
                    printmessage("You attack the %sbear with your %s, and hit!" % (grizzly_text, ITEMS[0]), 5, RED, 0)
                    BEARSTRENGTHVAL = BEARSTRENGTHVAL - weapon_strength(ITEMS[0])
                    add_score(25)
                    if BEARSTRENGTHVAL <= 0:
                        clear_messages(0)
                        if GRIZZLY_BEAR:
                            printmessage("You've done it.  You've killed the famous grizzly bear!", 3, GREEN, 3)
                            printmessage("The fight has left you damaged, but you'll survive.", 4, GREEN, 3)
                        else:
                            printmessage("You've managed to kill a wild bear!  Well done!", 3, GREEN, 2)
                        HAS_COMPASS_MAP[ZERO_BASE_PLYR_POS] = COMPASS_DICT[6] # dead bear
                        add_score(250)
                        reset_fight()
                else:
                    printmessage("You try to attack the bear, but you miss!.", 5, BLUE, 0)
            elif command == ord('o'):
                if fifty_fifty() == 1:
                    if fifty_fifty() == 1:
                        clear_messages(0)
                        printmessage("The bear takes the food, and you manage to escape!", 5, GREEN, 1)
                        add_food(False, 15)
                        add_score(150)
                        force_move()
                        reset_fight()
                    else:
                        printmessage("The bear takes the food, but he wants more!", 5, MAGENTA, 1)
                        add_food(False, 15)
                else:
                    printmessage("You offer the bear some food, but he ignores you!", 3, CYAN, 0)
                    if one_in_three() == 1:
                        printmessage("He then takes a swipe at you, and hits!", 5, RED, 0)
                        add_strength(False, 20)
                    else:
                        printmessage("He then takes a swipe at you, but misses!", 5, BLUE, 0)

            elif command == ord('r'):
                if one_in_four() == 1:
                    printmessage("You manage to run away!", 5, GREEN, 1)
                    # Check where we can go
                    clear_messages(0)
                    force_move()
                    reset_fight()
                else:
                    printmessage("You try to run away, but the %sbear stops you, with his claws!" % grizzly_text, 5, RED, 0)
                    add_strength(False, 15)

            elif command == ord('s'):
                print_fight_status()

    elif enemy == 3: # Ivan Milat
        printmessage("Oh no, Ivan Milat has found you....", 5, RED, 3)
        die("ivanmilat")


def print_fight_status():
    """ shows the status of the fight """
    printmessage("You're fighting with a %s" % ITEMS[0], 3, RED, 0)
    printmessage("You feel like you're %s" % get_strength_text(STRENGTHVAL), 4, GREEN, 0)
    printmessage("The bear looks like he is %s" % get_strength_text(BEARSTRENGTHVAL), 5, MAGENTA, 0)
    printmessage("Your food supply is %s" % get_hunger_text(HUNGERVAL), 6, YELLOW, 0)

def get_strength_text(currentstrength):
    """ Takes a number and returns the strength text """
    for i in range(0, 5):  
        strengthrange = (79, 59, 39, 19, 0)
        if currentstrength in range(strengthrange[i], strengthrange[i] + 20):
            strength = STRENGTH_TEXT[i]
        if currentstrength > 99:
            strength = STRENGTH_TEXT[0]

    return strength

def get_hunger_text(currenthunger):
    """ Takes a number and returns the hunger text """
    for i in range(0, 5):  
        hungerrange = (79, 59, 39, 19, 0)
        if currenthunger in range(hungerrange[i], hungerrange[i] + 20): 
            hunger = HUNGER_VALUES[i]
        if currenthunger > 99:
            hunger = HUNGER_VALUES[0]

    return hunger

def weapon_strength(weapon):
    """ Returns the weapon strength of the current weapon """
    weapon_strength_int = WEAPON_STRENGTHS[weapon]
    #print weapon_strength_int
    return weapon_strength_int

def additemtoinventory(item):
    """ Adds an item to the inventory displayed to the user """
    global ITEM_COUNT
    for i in range(0, 10): # first 10 items are weapons, (this code sux, need a better way of doing this)
        if ITEMTYPES[ITEM_LIST[ZERO_BASE_PLYR_POS]] == ITEMTYPES[i]: 
            cur_weapon_strength = WEAPON_STRENGTHS[ITEMS[0]]
            new_weapon_strength = WEAPON_STRENGTHS[ITEMTYPES[i]]
            if new_weapon_strength > cur_weapon_strength:
                change_weapon(ITEMTYPES[i])
                ITEMS[0] = ITEMTYPES[i] # 'overwrite' the main weapon with the new one
                remove_item_from_map()
                return # exit here if item is weapon
            else:
                remove_item_from_map()
                return # remove the inferior weapon from the map and return
    ITEMS.append(ITEMTYPES[item])
    ITEM_COUNT = len(ITEMS)
    remove_item_from_map()

def remove_item_from_map():
    """ Removes an item from the map """  
    ITEM_LIST[ZERO_BASE_PLYR_POS] = int(len(ITEMTYPES) - 2) # Replaces item with the "None" item


def addnourishment(foodint):
    """ Increases hunger, different values for different foods """

    if foodint == 0: # Apples
        hungeradd = APPLES
    if foodint == 1: # Berries
        hungeradd = BERRIES
    if foodint == 2: # Grapes
        hungeradd = GRAPES
    if foodint == 3: # Bananas
        hungeradd = BANANAS
    if foodint == 4: # Chocolate
        hungeradd = CHOCOLATE
    if foodint == 5: # Beef Jerky
        hungeradd = BEEF_JERKY

    add_food(True, hungeradd)
    add_score(20)

def clear_messages(timeout): # Gets called from main program loop
    """ Clears all active messages """
    
    message = ' ' * 78 # Blank String
    if timeout > 0:
        sleep(timeout)

    for i in range(1, 9):
        mvaddstr(i + 13, 1, message, color_pair(BLACK))
    refresh()

def printmessage(message, line, colour, timeout):
    """ Prints a message to the message area """
    blank_line = ' ' * 76 # Blank String

    if timeout > 0: # No timeout
        mvaddstr(line + 13, 3, blank_line, color_pair(BLACK))
        mvaddstr(line + 13, 3, message, color_pair(colour) | A_BOLD)
        refresh()
        sleep(timeout)
        mvaddstr(line + 13, 3, blank_line, color_pair(BLACK))
        refresh()
    else:
        mvaddstr(line + 13, 3, blank_line, color_pair(BLACK))
        mvaddstr(line + 13, 3, message, color_pair(colour) | A_BOLD)
        refresh()

def die(typeofdeath):
    """ Prints a varity of exit messages after the game is over """
  
    nocbreak() 
    #keypad(0)
    echo()
    endwin()
    clearscreen()
    if GRIZZLY_BEAR:
        grizzly_text = "grizzly "
    else:  
        grizzly_text = ""

    if typeofdeath == 'starved':
        print "\nYou starved to death.  You didnt eat, so now you will be eaten.\n"
    elif typeofdeath == 'tooweak':
        if FIGHT:
            print "\nThe %sbear has mauled you to death.  Perhaps you should think about going" % grizzly_text
            print "into a fight when you feel stronger, or use a better weapon...\n"
        else:
            print "\nYou are too weak to go on.  You cower on the ground and become forest food.\n"
    elif typeofdeath == 'normalexit':
        print "\nGoodbye for now, the terrors of the outback will be waiting for you....\n"
    elif typeofdeath == 'ivanmilat':
        print "\nIvan Milat stabs you in the back with a large knife.\n"
        print "You are paralised, and cannot stop him from dragging you out of the\n"
        print "forest, and taking you away to an undisclosed location.  You're so dead.\n"
    elif typeofdeath == "ranger":
        print "\nCongratulations!  You found the ranger station.  You are finally safe.\n"
        print "You explain your situation to the ranger, who phones the police and has you\n"
        print "taken to the local hospital for observation.  Your ordeal is finally over.\n"
        add_score(2000)
    

    print "Total moves: %d\n" % TOTAL_MOVES 
    print "Your score : %d\n" % SCORE
    print "Your rank  : %s\n" % get_rank(SCORE)
    sys.exit(0)

def get_rank(score):
    """ Checks score and returns rank """
    if score in range(0, 500):
        return RANKTYPES[0]
    elif score in range(500, 1500):
        return RANKTYPES[1]
    elif score in range(1500, 2000):
        return RANKTYPES[2]
    elif score in range(2000, 2500):
        return RANKTYPES[3]
    elif score in range(2500, 3000):
        return RANKTYPES[4]
    elif score in range(3000, 4000):
        return RANKTYPES[5]
    elif score in range(4000, 5500):
        return RANKTYPES[6]
    elif score > 5500:
        return RANKTYPES[7]

def time_keeper(addhour):
    """ Manages time """
    global TIME 
    global DAY
    global NICE_WEATHER

    if addhour:
        TIME += 1
    if TIME == 24:
        TIME = 0
        DAY += 1
        if fifty_fifty() == 1:
            NICE_WEATHER = False
        else:
            NICE_WEATHER = True
    if HAS_WATCH:
        update_title_area(" Day: %d Time: %d:00  " % (DAY, TIME))
    return TIME 

def show_weather():
    """ Displays the weather """
    if NICE_WEATHER:
        weather_description = NICE_WEATHER_DESCRIPTIONS.get(get_weather_with_time(time_keeper))
        weather_colour = NICE_WEATHER_COLOUR
    else:
        weather_description = BAD_WEATHER_DESCRIPTIONS.get(get_weather_with_time(time_keeper))
        weather_colour = BAD_WEATHER_COLOUR
    
    mvaddstr(14, 3, weather_description, color_pair(weather_colour) | A_BOLD)

def get_weather_with_time(time):
    """ Passes back time int """
    global DARK

    if TIME in range(6, 9):
        DARK = False
        return 1
    elif TIME in range(9, 13):
        return 2
    elif TIME in range(13, 16):
        return 3
    elif TIME in range(16, 19):
        if HAS_RAINCOAT:
            return 4
        else:
            if not NICE_WEATHER:
                add_strength(False, 10)
            return 5

    elif TIME in range(19, 22):
        if HAS_RAINCOAT:
            return 7
        else:
            if not NICE_WEATHER:
                add_strength(False, 10)
            return 6

    else: # 9 - 6am
        DARK = True
        if HAS_FLASHLIGHT:
            return 9
        else:
            return 8 

def process_items():
    """ checks what items player has and adjusts variables """
    global HAS_WATCH
    global HAS_FIRST_AID_KIT
    global HAS_FLASHLIGHT
    global HAS_RAINCOAT
    global HAS_COMPASS
    global HAS_BEARTRAP

    if "Watch" in ITEMS:
        HAS_WATCH = True
    if "First Aid Kit" in ITEMS:
        HAS_FIRST_AID_KIT = True
    if "Flashlight" in ITEMS:
        HAS_FLASHLIGHT = True
    if "Raincoat" in ITEMS:
        HAS_RAINCOAT = True
    if "Compass" in ITEMS:
        HAS_COMPASS = True
    if "Bear Trap" in ITEMS:
        HAS_BEARTRAP = True

    # Stupid little hack to provide 'immediate updates/effect' of having the below items
    if HAS_WATCH:
        update_title_area(" Day: %d Time: %d:00  " % (DAY, TIME))
    if HAS_COMPASS:
        DISCOVERED[ZERO_BASE_PLYR_POS] = "Y"

def pause_for_keypress():
    """ Prints a message and waits for a keypress """
    
    printmessage("                    << Press any key to continue >>", 7, BLUE, 0)
    getch()
    clear_messages(0)
    
def intro():
    """ The intro """






def main():
    """ Main program loop """

    # Draw the screen
    make_screen()   
    show_ground_feature()
    show_weather()
    #display_weather()
    
    #subprocess.Popen(['afplay', 'bear.wav'])


    while True:

        # Get user input
        keypress = getch()
        processinput(keypress)

        # Set the below values to zero for God Mode.
        hunger_penalty = 3
        strength_penalty = 5

        if VALID_MOVE == True:
            if MOVEMENT == False: # means move just happened?
                if not FIGHT:
                    add_food(False, hunger_penalty)
                    add_strength(False, strength_penalty)
                add_score(5)
            else:
                # Decrease hunger penalty by half when not moving
                add_food(False, (hunger_penalty / 2))
                add_score(3)
            if not FIGHT:
                time_keeper(True)
                show_weather()
                show_ground_feature()

        process_items()
        checkhealth(STRENGTHVAL, HUNGERVAL)

        # Deliberate delay between moves to slow the game a little
        #time.sleep(0.8) 
        
        #clear_messages() # experimental
        refresh()
        # Process move
        # Process the current map tile
        # Process any fights
        # Process strength
        # Process hunger
#-----------------------------------------------------------------

stdscr = initscr()
start_color()
curs_set(False)
noecho()
#resizeterm(24, 80)

init_pair(1, COLOR_BLACK, COLOR_BLACK) # Black
init_pair(2, COLOR_RED, COLOR_BLACK) # Red
init_pair(3, COLOR_GREEN, COLOR_BLACK) # Green
init_pair(4, COLOR_YELLOW, COLOR_BLACK) # Yellow
init_pair(5, COLOR_BLUE, COLOR_BLACK) # Blue
init_pair(6, COLOR_MAGENTA, COLOR_BLACK) # Magenta
init_pair(7, COLOR_CYAN, COLOR_BLACK) # Cyan
init_pair(8, COLOR_WHITE, COLOR_BLACK) # White

# COLOUR CONSTANTS
BLACK = 1
RED = 2
GREEN = 3
YELLOW = 4
BLUE = 5
MAGENTA = 6
CYAN = 7
WHITE = 8

# CUSTOMISE COLOURS
BORDER_COLOUR = BLACK
HEADING_COLOUR = YELLOW
TEXT_COLOUR = WHITE
MAP_COLOUR = GREEN
DISCOVERED_MAP_COLOUR = RED
TITLE_COLOUR = CYAN
WARNING_COLOUR = RED
STRENGTH_COLOUR = GREEN
HUNGER_COLOUR = GREEN
PLAYER_COLOUR = MAGENTA
OPTIONS_COLOUR = WHITE
GROUND_FEATURES_COLOUR = GREEN
NICE_WEATHER_COLOUR = YELLOW
BAD_WEATHER_COLOUR = CYAN

# Initialise variableso
HUNGER_TEXT = ("Well Nourished", "Peckish       ", "Hungry        ", "Starving      ", "Near Death    ", "Dead")
STRENGTH_TEXT = ("Very Strong", "Strong     ", "Weak       ", "Very Weak  ", "Near Death ", "Dead")
HUNGER_VALUES = ["Very Good", "Good", "Adequate", "Low", "Very Low"]
ITEMS = ["Swiss Army Knife"]
ITEM_COUNT = 1
MOVES = ["(W) North", "(A) West", "(S) South", "(D) East", "(U) Up", "(J) Down", "", "", ""]
ACTIONS = ["(L) Look", "(F) Find Food", "(H) Hint", "(I) Item List", "(Y) Yell", "(Q) Quit", "", "", ""]
FIGHT_ACTIONS = ["(F) Fight", "(O) Give Food", "(R) Run Away", "(S) Status", "", "", "", "", ""]
SPECIAL_WITH_MOVE = ["(H) Heal", "(R) Remain", "", "", "", "", "", "", ""]
FOODTYPES = ["apples", "berries", "grapes", "bananas", "chocolate", "beef jerky", "None"]
RANKTYPES = ["Forest Chump", "Deadbeat", "Pathetic Soul", "Apprentice Scout", "Scout", "Pathfinder" "Ranger", "Hunter", "Bushman", "Bush Jedi"]
CURRENT_OPTIONS = MOVES
ZERO_BASE_PLYR_POS = random.randrange(0, 100)
ZBPP = 0
START_POS = ZERO_BASE_PLYR_POS
STRENGTH = STRENGTH_TEXT[0]
HUNGER = HUNGER_TEXT[0]
FIGHTMOVES = 0
MOVEMENT = True
ACTION = False
FIGHT = False
STRENGTHVAL = 100
BEARSTRENGTHVAL = 100
HUNGERVAL = 100
VALID_MOVE = True
MESSAGE_LINE1 = ""
MESSAGE_LINE2 = ""
MESSAGE_LINE3 = ""
MESSAGE_LINE4 = ""
MESSAGE_LINE5 = ""
MESSAGE_LINE6 = ""
SHORT_BLANK = " " * 13
LONG_BLANK = " " * 76
APPLES = 10 
BERRIES = 10  
GRAPES = 10
BANANAS = 20
CHOCOLATE = 20
BEEF_JERKY = 50
LAST_LINE_HAD_PLYR = False
MAPLIST = []
HAS_COMPASS_MAP = []
ITEM_LIST = []
FOOD_LIST = []
DISCOVERED = []
ENEMY_LIST = []
GROUND_FEATURES_LIST = []
NICE_WEATHER = True
TIME = 6
DAY = 1
DARK = False
NUM_HINTS = 0
UP_TREE = False
GRIZZLY_BEAR = False
HAS_WATCH = False
HAS_FIRST_AID_KIT = False
HAS_FLASHLIGHT = False
HAS_RAINCOAT = False
HAS_COMPASS = False
HAS_BEARTRAP = False


# INITIAL VALIES
SCORE = 0
TOTAL_MOVES = 0
HUNGER = HUNGER_TEXT[0]
STRENGTH = STRENGTH_TEXT[0]

ITEMTYPES = [
    "Hunting Knife",
    "Hunting Knife",
    "Hunting Knife",
    "Wooden Club",
    "Wooden Club",
    "Lead Pipe",
    "Lead Pipe",
    "Two-Headed Axe",
    "Two-Headed Axe",
    "Rifle",
    "Raincoat", 
    "Flashlight", 
    "Box of matches", 
    "Bottle", 
    "Bag of firewood", 
    "Backpack", 
    "Shovel",
    "Watch",
    "Blanket",
    "Bear Trap",
    "Glass Bottle",
    "Cup",
    "First Aid Kit",
    "First Aid Kit",
    "Helmet",
    "Rope",
    "None",
    "Compass" # Special
]

WEAPON_STRENGTHS = {
    "Swiss Army Knife":5,
    "Hunting Knife":20,
    "Wooden Club":30,
    "Lead Pipe":40,
    "Two-Headed Axe":50,
    "Rifle":70
}

COMPASS_DICT = {
    1:"W", # Water
    2:"T", # Big Tree
    3:"B", # Bear
    4:"G", # Grizzly Bear
    5:"+", # Nothing of interest
    6:"b" # dead bear
}

# Ground Descriptions
GROUND_DESCRIPTIONS = {
    1:"There are lots of bushes here.                                      ",
    2:"The ground is muddy here.                                           ",
    3:"You hear the birds singing in the trees.                            ",
    4:"The unmistakable growl of a bear in the distance unsettles you.     ",
    5:"The forest is filled with pine trees.                               ",
    6:"You are surrounded in swamp land.                                   ",
    7:"Mosquitoes are buzzing everywhere.  You squash one biting you.      ",
    8:"The forest is full of vegetation.                                   ",
    9:"The forest is filled with gum trees.                                ",
    10:"There is a fresh water creek here, you stop to take a drink.       ",
    11:"There is a large tree here among the many that populate the forest.",
    12:"There is lots of buzzing here, sounds like a lot of bees.          "
}

NICE_WEATHER_DESCRIPTIONS = {
    1:"It is morning.  The sun is shining over the horizon.                ", # 6am
    2:"The sun continues to rise in the sky.                               ", # 9am
    3:"It must be afternoon.  The sun is passing over you.                 ", # 12pm
    4:"The sun is beginning to recede over the trees.                      ", # 3pm
    5:"The sun is beginning to recede over the trees.                      ", # 3pm
    6:"Dusk is setting in.  It is starting to get dark.                    ", # 6pm
    7:"Dusk is setting in.  It is starting to get dark.                    ", # 6pm
    8:"It is pitch black.  You cannot see a thing.                         ", # 9pm - 6am
    9:"It is pitch black.  But you can see, thanks to your flashlight!     "  # 9pm - 6am with flashlight
}

BAD_WEATHER_DESCRIPTIONS = {
    1:"It is a foggy morning, the sun isn't visible.                       ", # 6am
    2:"Rain clouds are congregating over your position.                    ", # 9am
    3:"A cold and sharp wind is accompanied by rain.  It is spitting rain! ", # 12pm
    4:"It is raining hard.  But your raincoat protects you!                ", # 3pm
    5:"It is raining hard.  You feel sick due to the moisture!             ", # 3pm
    6:"It is pouring with no end in sight! You feel sick due to moisture.  ", # 6pm
    7:"It is pouring with no end in sight, but your raincoat keeps you dry.", # 6pm
    8:"It is pitch black.  You cannot see a thing.                         ", # 9pm - 6am
    9:"It is pitch black.  But you can see, thanks to your flashlight!     "  # 9pm - 6am with flashlight
}

HINT_LIST = [
    "The park ranger likes to make his own fresh honey.                  ",
    "Finding fresh water helps with healing and hunger.                  ",
    "You are not the only person wandering the forest, be careful.       ",
    "Finding a way to see in the dark makes you much more productive.    ",
    "Harsh rain can make you cold, wet, and sick.  Find protection.      ",
    "The compass may be in the last place you'd think to look.           ",
    "The only way to kill your stalker is with a gun.                    ",
    "Beef jerky is the best source of nourishment out in the bush.       ",
    "Offering food to a bear is better than running away.                ",
    "Always climb the large trees.                                       ",
    "The ferocious grizzly bear is twice as strong as a regular bear.    "
]

TREE_VIEWS = {
    1:"A dense forest.",
    2:"A fresh water stream.",
    3:"An angry bear.",
    4:"The ferocious grizzly bear!",
    5:"A huge mountain.",
    6:"A crocodile infested river.",
    7:"An impassable forest.",
    8:"A steep cliff."
}


# Start main loop
intro()
main()


