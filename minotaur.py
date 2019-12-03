from direct.showbase.ShowBase import ShowBase
from direct.interval.IntervalGlobal import Sequence
from direct.interval.LerpInterval import LerpPosInterval
from panda3d.core import Point3


class Minotaur(object):
    dtns = {'n':(0,1), 's':(0,-1), 'e':(1,0), 'w':(-1,0)}
    compDtns = {'ne':(1,1), 'nw':(-1,1), 'se':(1,-1), 'sw':(-1,-1)}
    def __init__(self, pos, health = 10, speed = 5):
        self.health = health
        self.speed = speed
        self.pos = pos

    @staticmethod
    def findPt( minPos, ptGrid, dir, spacing):
        
        if dir == 'n' or dir == 'w' or dir == 'nw':
            x = minPos[0] - spacing/2
            y = minPos[1] + spacing/2
        elif dir == 'e' or dir == 'ne':
            x = minPos[0] + spacing/2
            y = minPos[1] + spacing/2
        elif dir == 's' or dir == 'sw':
            x = minPos[0] - spacing/2
            y = minPos[1] - spacing/2
        elif dir == 'se':
            x = minPos[0] + spacing/2
            y = minPos[1] - spacing/2
        row = (len(ptGrid)*spacing - y)//spacing - 1
        col = x//spacing
        return (int(row), int(col))

    def findPerson(self, minPos, personPos, ptGrid, lstWalls, spacing, path=None):
        if (minPos[0], minPos[1]) == (personPos[0], personPos[1]):
            return path 
        if path == None:
            path = [minPos]
        for direc in self.dtns: 
            x, y = Minotaur.findPt(minPos, ptGrid, direc, spacing)
            nxtPos = (minPos[0] + self.dtns[direc][0]*spacing, minPos[1] + self.dtns[direc][1]*spacing, minPos[2])
            if 0<=nxtPos[0]<=(spacing*(len(ptGrid)-1)) and 0<=nxtPos[1]<=(spacing*(len(ptGrid[0])-1)):
                if direc == 'n' or direc == 's':
                    #if there is no wall
                    if (lstWalls[x][y][0]+self.dtns[direc][0])%2 == 0 and ((nxtPos[0], nxtPos[1], minPos[2]) not in path): 
                        path += [(nxtPos[0], nxtPos[1], minPos[2])]
                        tempSol = self.findPerson(nxtPos, personPos, ptGrid, lstWalls, spacing, path)
                        if tempSol != None:
                            return tempSol
                        path.pop()
                else: 
                    #if there is no wall 
                    if (lstWalls[x][y][1]+self.dtns[direc][1])%2 == 0 and ((nxtPos[0], nxtPos[1], minPos[2]) not in path): 
                        path += [(nxtPos[0], nxtPos[1], minPos[2])]
                        tempSol = self.findPerson(nxtPos, personPos, ptGrid, lstWalls, spacing, path)
                        if tempSol != None:
                            return tempSol
                        path.pop()
        return None


    def findDirection(self, playerPos, minPos, ptGrid, spacing):
        #player is north of minotaur
        if playerPos[1] > minPos[1]:
            if abs(playerPos[0] - minPos[0]) < 30:
                direc = 'n'
            else:     
                 # if player is roughly west of minotaur
                 if playerPos[0] < minPos[0]:
                    if abs(playerPos[1] - minPos[1]) < 30:
                        direc = 'w'
                    else: 
                        direc = 'nw'
                 # if player is roughly east of minotaur
                 else: 
                    if abs(playerPos[1] - minPos[1]) < 30:
                        direc = 'e'
                    else: 
                        direc = 'ne'
        #if player is south of minotaur 
        else: 
            if abs(playerPos[0] - minPos[0]) <  30:
                direc = 's'
            else: 
                 # if player is roughly west of minotaur
                 if playerPos[0] < minPos[0]:
                    if abs(playerPos[1] - minPos[1]) < 30:
                        direc = 'w'
                    else: 
                        direc = 'sw'
                 # if player is roughly east of minotaur
                 else: 
                    if abs(playerPos[1] - minPos[1]) < 30:
                        direc = 'e'
                    else: 
                        direc = 'se'

        return direc

    def checkWalls(self, minPos, ptGrid, direc, spacing, lstWalls):

        x, y = self.findPt(minPos, ptGrid, direc, spacing)

        if direc == 'n' or direc == 's':
            #if there is no wall
            if (lstWalls[x][y][0])%2 == 0:

                return ('long', (x, y))
            else: 
                return ('short', (x, y))

        elif direc == 'e' or direc == 'w':
            #if there is no wall
            if (lstWalls[x][y][1])%2 == 0:
                return ('long', (x, y))
            else: 
                return ('short', (x, y))

        #if a combination of n,s,e,w 
        else: 
            #if there are no walls 
            if lstWalls[x][y][0] == 0 and lstWalls[x][y][1] == 0:
                return ('long', (x, y))
            else: 
                return ('short', (x, y))

    def attack(self, playerPos, minPos, ptGrid, spacing, lstWalls):
        direc = self.findDirection(playerPos, minPos, ptGrid, spacing)
        distance, (x, y) = self.checkWalls(minPos, ptGrid, direc, spacing, lstWalls)

        #if regular cardinal directions
        if direc == 'n' or direc == 's' or direc == 'e' or direc == 'w':
            if distance == 'long':
                newPos = (minPos[0] + self.dtns[direc][0]*spacing, minPos[1] + self.dtns[direc][1]*spacing, minPos[2])

            elif distance == 'short': 
                newPos = (minPos[0] + self.dtns[direc][0]*(spacing/2 - 10), minPos[1] + self.dtns[direc][1]*(spacing/2 - 10), minPos[2])

        #if combination cardinal directions
        elif direc == 'ne' or direc == 'nw' or direc == 'se' or direc == 'sw':
            if distance == 'long':
                newPos = (minPos[0] + self.compDtns[direc][0]*spacing, minPos[1] + self.compDtns[direc][1]*spacing, minPos[2])

            elif distance == 'short': 
                newPos = (minPos[0] + self.compDtns[direc][0]*(spacing/2 - 10), minPos[1] + self.compDtns[direc][1]*(spacing/2 - 10), minPos[2])

        #if point minotaur is moving to is valid
        if 0<=newPos[0]<=(spacing*(len(ptGrid)-1)) and 0<=newPos[1]<=(spacing*(len(ptGrid[0])-1)):
            attackPos = []
            for i in newPos:
                attackPos += [int(i)]
            return ((attackPos[0], attackPos[1], attackPos[2]), distance, direc)

        #shouldn't hit, but just in case
        return (None, distance, direc) 

    def facePlayer(self, direction):

        if direction == 'n':
            hpr = (180,0,0)
        elif direction == 's':
            hpr = (0,0,0)
        elif direction == 'e':
            hpr = (90,0,0)
        elif direction == 'w':
            hpr = (-90,0,0)
        elif direction == 'ne':
            hpr = (135,0,0)
        elif direction == 'nw':
            hpr = (-135,0,0)
        elif direction == 'se':
            hpr = (45,0,0)
        elif direction == 'sw':
            hpr = (-45,0,0)
        return hpr


    def hit(self):
        self.health -= 10

        print(self.health)








