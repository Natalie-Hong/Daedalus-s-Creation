import random
import copy
from minotaur import*

dtns = {'n':(0,1), 's':(0,-1), 'e':(1,0), 'w':(-1,0)}


def generateCoord(ptGrid, spacing):
    randRow = random.randint(0, len(ptGrid)-2)
    randCol = random.randint(0, len(ptGrid[randRow])-2)
    height = -40
    pt = ptGrid[randRow][randCol]
    x = pt[0] + spacing/2
    y = pt[1] - spacing/2
    z = pt[2] + height
    return (x, y, z)

def generatePosLst(pplLst, numPpl, ptGrid, spacing):
    while len(pplLst) < numPpl:
            pos = generateCoord(ptGrid, spacing)
            if pos not in pplLst:
                pplLst += [pos]

    return pplLst

def generateDoor(ptGrid, lstWallsOrig):

    pos, wall = doorPos(ptGrid, lstWallsOrig)
    print('in da door', pos, wall)
    return (pos, wall)


def doorPos(ptGrid, lstWallsOrig):
    lstWalls = copy.deepcopy(lstWallsOrig)
    wall = random.choice(['x', 'y'])
    print(wall)
    wallRand = random.randint(0,1)
    print('rand...', wallRand)
    if wall == 'x':
        xPos = random.randint(0,len(ptGrid[0])-1)
        y = random.randint(0, 1)
        if y == 1:
            y = (len(ptGrid[0])-1)
            #only get rid of right wall
        #if y = 0
        if y == xPos == 0:
            #if x, y = (0,0), only choose one wall
            print('here', lstWalls[xPos][y], wallRand)
            lstWalls[xPos][y][wallRand] = 2
            takeWall = lstWalls[xPos][y]
            print('takeWall', takeWall)
        elif y == xPos == len(ptGrid)-1:
            amount = random.randint(1, len(ptGrid)-1)
            xPos -= amount
            takeWall = [lstWalls[xPos][y][0], 2]
        elif xPos == 0 and y == len(ptGrid)-1:
            takeWall = [0,2]
        elif y == 0 and xPos == len(ptGrid)-1:
            takeWall = [2,0]
        else:
            takeWall = [lstWalls[xPos][y][0], 2]
        print('down takeWall', takeWall)

        return [(xPos,y), takeWall] 

    #if initially chose y
    else:
        yPos = random.randint(0,len(ptGrid)-1)
        x = random.randint(0, 1)
        if x == 1:
            x = (len(ptGrid)-1)
            #only get rid of down wall
        if x == yPos == 0:
            print('here', lstWalls[x][yPos], wallRand)
            lstWalls[x][yPos][wallRand] = 2
            takeWall = lstWalls[x][yPos]
            print('takeWall', takeWall)
        elif x == yPos == len(ptGrid)-1:
            amount = random.randint(1, len(ptGrid)-1)
            yPos -= amount
            takeWall = [2, lstWalls[x][yPos][1]]
        elif x == 0 and yPos == len(ptGrid)-1:
            takeWall = [0,2]
        elif yPos == 0 and x == (len(ptGrid)-1):
            takeWall = [2,0]

        else:
            takeWall = [2, lstWalls[x][yPos][1]]
        print('down takeWall', takeWall)

        return [(x,yPos), takeWall]

print(generateDoor([[(0, 400, 0), (100, 400, 0), (200, 400, 0), (300, 400, 0), \
    (400, 400, 0)], [(0, 300, 0), (100, 300, 0), (200, 300, 0), (300, 300, 0), \
    (400, 300, 0)], [(0, 200, 0), (100, 200, 0), (200, 200, 0), (300, 200, 0), \
    (400, 200, 0)], [(0, 100, 0), (100, 100, 0), (200, 100, 0), (300, 100, 0), \
    (400, 100, 0)], [(0, 0, 0), (100, 0, 0), (200, 0, 0), (300, 0, 0), (400, 0, 0)]],
[[[1, 1], [1, 1], [1, 0], [1, 0], [0, 1]], [[0, 1], [1, 1], [0, 0], [1, 0], [0, 1]], \
[[0, 1], [0, 0], [1, 0], [1, 0], [0, 1]], [[1, 1], [0, 0], [1, 1], [0, 0], [0, 1]], \
[[1, 0], [1, 0], [1, 0], [1, 0], [0, 0]]]))

def findClosestPt(playerPos):
    x = playerPos[0]//100*100 + 50
    y = playerPos[1]//100*100 + 50
    return (x, y, playerPos[2])

def findExitPos(exit, ptGrid, spacing):
    #exit is on bottom row
    if exit[1] == 0: 
        exitPosX = exit[0] + spacing/2
        exitPosY = spacing/2
    #exit is on top row
    elif exit[1] == spacing*(len(ptGrid)-1):
        if exit[0] == spacing*(len(ptGrid[0])-1):
            exitPosX = exit[0] - spacing/2
            exitPosY = exit[1] - spacing/2
        else: 
            exitPosX = exit[0] + spacing/2
            exitPosY = exit[1] - spacing/2
    #exit is on left col
    elif exit[0] == 0:
        exitPosX = exit[0] + spacing/2
        exitPosY = exit[1] - spacing/2

    #exit is on right col
    elif exit[0] == spacing*(len(ptGrid[0])-1):
        exitPosX = exit[0] - spacing/2
        exitPosY = exit[1] - spacing/2

    return (exitPosX, exitPosY)

def findPlayerPos(playerPos, spacing):
    x = (playerPos[0]//spacing) * spacing + spacing/2
    y = (playerPos[1]//spacing) * spacing + spacing/2
    return [x, y]


def findExit(playerPos, exitPos, ptGrid, lstWalls, spacing, path=None, dirL =None):
    if (playerPos[0], playerPos[1]) == (exitPos[0], exitPos[1]):
        return (path, dirL)
    if path == dirL == None:
        path = [playerPos]
        dirL = []
    for direc in dtns: 
        x, y = Minotaur.findPt(playerPos, ptGrid, direc, spacing)
        nxtPos = (playerPos[0] + dtns[direc][0]*spacing, playerPos[1] + dtns[direc][1]*spacing, playerPos[2])
        if 0<=nxtPos[0]<=(spacing*(len(ptGrid)-1)) and 0<=nxtPos[1]<=(spacing*(len(ptGrid[0])-1)):
            if direc == 'n' or direc == 's':
                #if there is no wall
                if(lstWalls[x][y][0]+dtns[direc][0])%2 == 0 and ((nxtPos[0], nxtPos[1], playerPos[2]) not in path): 
                    path += [(nxtPos[0], nxtPos[1], playerPos[2])]
                    dirL += [direc]
                    tempSol = findExit(nxtPos, exitPos, ptGrid, lstWalls, spacing, path, dirL)
                    if tempSol != None:
                        return tempSol
                    path.pop()
                    dirL.pop()
            else: 
                #if there is no wall 
                if(lstWalls[x][y][1]+dtns[direc][1])%2 == 0 and ((nxtPos[0], nxtPos[1], playerPos[2]) not in path): 
                    path += [(nxtPos[0], nxtPos[1], playerPos[2])]
                    dirL += [direc]
                    tempSol = findExit(nxtPos, exitPos, ptGrid, lstWalls, spacing, path, dirL)
                    if tempSol != None:
                        return tempSol
                    path.pop()
                    dirL.pop()
    return None

def findDir(exitPos, ptGrid):
    print(exitPos)
    #on left side
    if exitPos[1] == 0:
        return 'w'
    elif exitPos[1] == len(ptGrid[0])-1:
        return 'e'
    elif exitPos[0] == 0:
        return 'n'
    elif exitPos[0] == len(ptGrid)-1:
        return 's'




    



