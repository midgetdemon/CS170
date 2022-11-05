# Throughout this code, I have comments explaining active code and I have comments of other ways I wrote functions/code. I kept going back 
# and forth because my program kept failing and I thought it was a problem with something I wrote. Turns out, I just forgot to indent
# one of my functions and so it never added anything to the queue after removing the first node. >:(( 

import copy as puzzleCopy #copy class to perform deepcopy for expand functions 

import heapq #priority queue, heapify will convert to heap order (min to max), to insert use heappush(heap, ele), to pop use heappop (heap)

import time #to determine time the algorithm takes 

from functools import total_ordering #part of Python 3, need in order to perfom comparison operators for heap 

# this class represents the nodes (pieces) on our search tree as we evaluate the puzzle
@total_ordering
class Piece:    
    def __init__ (self, puzzle, g_n, h_n):
        self.state = puzzle #the actual puzzle 
        self.g_n = g_n #depth 
        self.h_n = h_n # heuristic 
        # f(n) = g(n) + h(n) 
        # estimated cost of the cheapest solution that goes through node n (f(n)) = 
        # cost to get to a node or depth (g(n)) + estimated distance to the goal or heuristic (h(n))
        self.f_n = self.h_n + self.g_n # the total cost for the A-star function 

    #def puzzlestate(self, puzzle):
        #self.state = puzzle 

    def __eq__ (self, other):
        return self.f_n == other.f_n

    def __lt__ (self, other):
        return self.f_n < other.f_n

    def __le__ (self, other):
        return self.f_n <= other.f_n


# if we adjust the size of the puzzle for more pieces, we need to change the range here as well 
def printPuzzle(puzzle): 
    print("The best state to expand with a g(n) = ", puzzle.g_n, "and h(n) = ", puzzle.h_n, "is...")
    print(puzzle.state[0][0], puzzle.state[0][1], puzzle.state[0][2])
    print(puzzle.state[1][0], puzzle.state[1][1], puzzle.state[1][2])
    print(puzzle.state[2][0], puzzle.state[2][1], puzzle.state[2][2])


#Below are the built in puzzles (provided by Dr. Eamonn Keogh)

level1 = [[1, 2, 3], [4, 5, 6], [7, 8, 0]] #depth 0

level2 = [[1, 2, 3], [4, 5, 6], [0, 7, 8]] #depth 2

level3 = [[1, 2, 3], [5, 0, 6], [4, 7,8]] #depth 4

level4 = [[1, 3, 6], [5, 0, 2], [4, 7, 8]] #depth 8

level5 = [[1, 3, 6], [5, 0, 7], [4, 8, 2]] #depth 12

level6 = [[1, 6, 7], [5, 0, 3], [4, 8, 2]] #depth 16

level7 = [[7, 1, 2], [4, 8, 5], [6, 3, 0]] #depth 20

level8 = [[0, 7, 2], [4, 6, 1], [3, 5, 8]] #depth 24

goalstate = [[1, 2, 3], [4, 5, 6], [7, 8, 0]] 

#This main function prompts the user and also transitions into the rest of the program
def main ():
    puzzle_mode = input("Lets solve an Eight Puzzle. Type 1 to test a built in puzzle or type 2 to input your own." + '\n')
    if puzzle_mode == "1": 
        startTime = time.time() 
        selectAlgorithm(selectPuzzle()) # first we select the puzzle (1-8), then we select the algorithm to solve it (1-3)
        endTime = time.time() 
        print("The search for this puzzle took {} seconds.".format(endTime - startTime))

    if puzzle_mode == "2":
        print("Enter your puzzle, using a zero to represent the blank. " + "the numbers with a space. Enter only when finished." + '\n')
        rowOne = input ("Enter the first row: ")
        rowTwo = input ("Enter the second row: ")
        rowThree = input("Enter the third row: ")

        # the split function separates the numbers into strings in a list (splitting at space)
        rowOne = rowOne.split() 
        rowTwo = rowTwo.split()
        rowThree = rowThree.split()

        # now we take each string and cast as an int 
        # if we want to use a bigger custom puzzle, we need to adjust the range here and add more row variables accordingly
        for k in range (0,3): 
            rowOne[k] = int(rowOne[k])
            rowTwo[k] = int(rowTwo[k])
            rowThree[k] = int(rowThree[k])
        
        # putting all the mini arrays together to make one puzzle 
        custompuzzle = [rowOne, rowTwo, rowThree]
        print("Your puzzle looks like the following: " + '\n')
        printPuzzle(custompuzzle)

        # pushing the custom puzzle to the select algorithm function to choose our search 
        startTime = time.time() 
        selectAlgorithm(custompuzzle)
        endTime = time.time() 
        print("The search for this puzzle took {} seconds.".format(endTime - startTime))
        
        return 


#returns the correct built in puzzle to the selectAlgorithm function, correlating to choice 1 in driver function
def selectPuzzle():  
    difficulty = input("Select the difficulty/level of puzzle to solve from 1 to 8." + '\n')
    if difficulty == "1":
        print("Level 1 selected." + '\n')
        return level1
    if difficulty == "2":
        print("Level 2 selected." + '\n')
        return level2
    if difficulty == "3":
        print("Level 3 selected." + '\n') 
        return level3
    if difficulty == "4":
        print("Level 4 selected." + '\n')
        return level4
    if difficulty == "5":
        print("Level 5 selected." + '\n')
        return level5
    if difficulty == "6":
        print("Level 6 selected." + '\n')
        return level6
    if difficulty == "7":
        print("Level 7 selected." + '\n')
        return level7
    if difficulty == "8":
        print("Level 8 selected." + '\n')
        return level8
    return 

#This is for selecting the algorithm to solve the puzzle 
def selectAlgorithm(puzzle): 
    algorithm = input("Select your search algorithm. + '\n' + Type 1 for Uniform Cost Search (A* with zero heuristic), 2 for A* with Misplaced Tile Heuristic, "
                "or 3 for A* with the Manhatthan Distance Heuristic." + '\n')
    if algorithm == "1":
        generalSearch(puzzle, 0) # A* with h(n) = 0
    if algorithm == "2":
        generalSearch(puzzle, 1) # A* with h(n) = misplaced tile 
    if algorithm == "3":
       generalSearch(puzzle, 2) # A* with h(n) = manhattan distance 


# main driver function 
def generalSearch(puzzle, heuristic): 
    heapqueue = [] # current queue 
    nodecount = 0 # number of nodes visited or expanded 
    maxqueuesize = 0 # max size of the queue    

    #startnode = Piece()
    #startnode.puzzlestate(puzzle)
    #startnode.g_n = 0 

    # creating a new node with our puzzle, initial depth is 0 and heuristic cost is h_n depending on the algorithm
    if heuristic == 0:
        startnode = Piece(puzzle, 0, 0)
        #startnode.h_n = 0 
    if heuristic == 1:
        h_n = misplacedTileHeurisitc(puzzle)
        startnode = Piece(puzzle, 0, h_n)
        #startnode.h_n = misplacedTileHeurisitc(puzzle)
    if heuristic == 2:
        h_n = manhatthanDistanceHeuristic(puzzle)
        startnode = Piece(puzzle, 0, h_n)
        #startnode.h_n = manhatthanDistanceHeuristic(puzzle)

    # we are pushing our root or start node (the initial state) into the queue 
    heapq.heappush(heapqueue, startnode)

    #heapqueue.append(startnode)
    #heapq.heapify(heapqueue, startnode) #inserting the initial state into the current heap

    print("Beginning expansion" + '\n')
    printPuzzle(startnode)

    goalreached = False
    while goalreached == False:
        #print ("The length of the queue is... ")
        #print (len(heapqueue))
        #maxqueuesize = max(len(heapqueue), maxqueuesize)
        
        if len(heapqueue) == 0: # there should at least be starting node in current queue
            print("Failure for puzzle search") 
            return 

        #print("Beginning expansion" + '\n')
        #printPuzzle(startnode)
        
        #heapq.heapify(heapqueue)

        #currentnode = Piece() 
        #currentnode.h_n = heapqueue[0].h_n
        #currentnode.g_n = heapqueue[0].g_n
        #currentnode.state = heapqueue[0].state
       
        #print("Starting pop" + '\n')

        # We are popping our current node so that we may expand the puzzle or check if its the goal state  
        currentnode = heapq.heappop(heapqueue)
        #print("finished pop" + '\n')
        printPuzzle(currentnode)

        #print ("The length of the queue after pop is... ")
        #print (len(heapqueue))

        # Checking if we reached the goal state by comparing the puzzle associated with our current node to the puzzle defined in the goal state 
        # If so, we print a bunch of information  
        if goalStateCheck(currentnode):
            goalreached = True 
            print("Goal state reached." + '\n')
            printPuzzle(currentnode)
            print("Solution depth was " + str(currentnode.g_n) + '\n')
            print("Number of nodes expanded was " + str(nodecount) + '\n')
            print("Max queue size was " + str(maxqueuesize) + '\n')
        else:
            #print("staring expansion" + '\n')
            
            # Calling the expansion function to basically return a list of the nodes in the puzzle from the current node and the number of nodes we have expanded
            subpuzzle, nodecount = expandNode(currentnode, nodecount)
            #print("finished expansion" + '\n')
            
            # Updating the heuristics, depth, and total cost for all the nodes 
            for k in range(len(subpuzzle)):
                if heuristic == 0:
                    subpuzzle[k].h_n = 0
                if heuristic == 1:
                    subpuzzle[k].h_n = misplacedTileHeurisitc(subpuzzle[k].state)
                    subpuzzle[k].f_n = subpuzzle[k].h_n + subpuzzle[k].g_n
                if heuristic == 2:
                    subpuzzle[k].h_n = manhatthanDistanceHeuristic(subpuzzle[k].state)
                    subpuzzle[k].f_n = subpuzzle[k].h_n + subpuzzle[k].g_n 

                # Pushing the new node back into the queue 
                heapq.heappush(heapqueue, subpuzzle[k])
                #print ("The length of the queue after 1 iteration is... ")
                #print (len(heapqueue))

            # if the length of the queue is exceeding the current max, we want to update the count 
            if len(heapqueue) > maxqueuesize:
                maxqueuesize = len(heapqueue)

    return 

# This heuristic basically sums up the number of misplaced tiles within a puzzle 
def misplacedTileHeurisitc(puzzle): 
    misplacedcount = 0
    #for x in range(len(puzzle)):
    for x in range(3): 
        #for y in range(len(puzzle)):
        for y in range(3):
            if puzzle[x][y] != 0: 
                if puzzle[x][y] != goalstate[x][y]: 
                    misplacedcount += 1
    return misplacedcount

# This heuristic basically sums up how far each misplaced tile is from their goal state 
# manhatthan distance formula between (x1, y1) and (x2, y2) is |x1 - x2| + |y1 - y2|
# above formula from geeksforgeeks.org 
def manhatthanDistanceHeuristic(puzzle): #CHANGE CODE 
    distancecount = 0 
    for k in range (0, 8):
        #for x in range(len(puzzle)):
        for x in range(3):
            #for y in range(len(puzzle)):
            for y in range(3):
                if puzzle[x][y] == k:
                    currentrow = x
                    currentcolumn = y
                if goalstate[x][y] == k:
                    goalrow = x
                    goalcolumn = y
        distancecount += (abs(currentrow - goalrow) + abs(currentcolumn - goalcolumn))
    
    return distancecount 

# This function expands each node (puzzle piece) by determing if it can go left, right, up, or down and then returns a new puzzle list plus how many nodes it has expanded 
def expandNode(currentNode, nodecount): 
    expandlist = []
    g_n = currentNode.g_n + 1 # updating depth as we go 
    
    # We are finding the blank tile and recording it 
    zerorow = 0
    zerocol = 0
    for k in range(3):
        for n in range(3):
            if currentNode.state[k][n] == 0:
                zerorow = k
                zerocol = n

    # Checking if we can our current tile left and doing so if possible 
    if zerocol != 0:
        moveLeft = puzzleCopy.deepcopy(currentNode.state)
        moveLeft[zerorow][zerocol] = moveLeft[zerorow][zerocol - 1]
        moveLeft[zerorow][zerocol - 1] = 0
        
        #leftPiece = Piece()
        #leftPiece.h_n = 0
        #leftPiece.g_n = g_n
        #leftPiece.puzzlestate(moveLeft)
        leftPiece = Piece(moveLeft, g_n, 0)
        
        expandlist.append(leftPiece)
        nodecount += 1

    # Checking if we can our current tile right and doing so if possible 
    if zerocol != 2:
        moveRight = puzzleCopy.deepcopy(currentNode.state)
        moveRight[zerorow][zerocol] = moveRight[zerorow][zerocol + 1]
        moveRight[zerorow][zerocol + 1] = 0
        
        #rightPiece = Piece()
        #rightPiece.h_n = 0
        #rightPiece.g_n = g_n
        #rightPiece.puzzlestate(moveRight)
        rightPiece = Piece(moveRight, g_n, 0)
        
        expandlist.append(rightPiece)
        nodecount += 1

    # Checking if we can our current tile up and doing so if possible 
    if zerorow != 0:
        moveUp = puzzleCopy.deepcopy(currentNode.state)
        moveUp[zerorow][zerocol] = moveUp[zerorow - 1][zerocol]
        moveUp[zerorow - 1][zerocol] = 0
        
        #upPiece = Piece()
        #upPiece.h_n = 0
        #upPiece.g_n = g_n
        #upPiece.puzzlestate(moveUp)
        upPiece = Piece(moveUp, g_n, 0)
        
        expandlist.append(upPiece)
        nodecount+= 1

    # Checking if we can our current tile down and doing so if possible 
    if zerorow != 2:
        moveDown = puzzleCopy.deepcopy(currentNode.state)
        moveDown[zerorow][zerocol] = moveDown[zerorow + 1][zerocol]
        moveDown[zerorow + 1][zerocol] = 0
        
        #downPiece = Piece()
        #downPiece.h_n = 0
        #downPiece.g_n = g_n
        #downPiece.puzzlestate(moveDown)
        downPiece = Piece(moveDown, g_n, 0)
        
        expandlist.append(downPiece)
        nodecount += 1

    #Node count is the number of nodes we've expanded 
    return expandlist, nodecount

def goalStateCheck(somepuzzle):
    return somepuzzle.state == goalstate 

if __name__ == '__main__': 
    main() 

