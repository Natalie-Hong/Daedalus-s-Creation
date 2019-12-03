#!/usr/bin/env python

#imports from panda3d
from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData
from panda3d.core import WindowProperties
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay, CollisionHandlerPusher
from panda3d.core import CollisionNode, CollisionSphere, CollisionPolygon
from panda3d.core import TextNode, Material
#from panda3d.core import PandaNode, NodePath, Camera
from panda3d.core import LPoint3, LVector3,  BitMask32, Point3, Vec4
from direct.task.Task import Task
from direct.actor.Actor import Actor
from direct.gui.OnscreenText import OnscreenText
#from direct.showbase.DirectObject import DirectObject
#from direct.filter.CommonFilters import *
from direct.interval.LerpInterval import LerpPosInterval
from direct.interval.IntervalGlobal import *


from makeMaze import*
from objects import*
from minotaur import*
import sys
import os

# Function to put instructions on the screen.
def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1, 1, 1, 1), scale=.05,
                        shadow=(0, 0, 0, 1), parent=base.a2dTopLeft,
                        pos=(0.08, -pos - 0.04), align=TextNode.ALeft)

# Function to put title on the screen.
def addTitle(text):
    return OnscreenText(text=text, style=1, fg=(1, 1, 1, 1), scale=.08,
                        parent=base.a2dBottomRight, align=TextNode.ARight,
                        pos=(-0.1, 0.09), shadow=(0, 0, 0, 1))

class Labrintth(ShowBase):

    def __init__(self):

          #from panda3d bump mapping demo
        # Configure the parallax mapping settings (these are just the defaults)
        loadPrcFileData("", "parallax-mapping-samples 3\n"
                            "parallax-mapping-scale 0.1")

        # Initialize the ShowBase class from which we inherit, which will
        # create a window and set up everything we need for rendering into it.
        ShowBase.__init__(self)


        #titles from panda3d bumb mapping demo
        # Check video card capabilities.
        if not self.win.getGsg().getSupportsBasicShaders():
            addTitle("Bump Mapping: "
                "Video driver reports that Cg shaders are not supported.")
            return

        self.playerHealth = 10
        self.loseHealth = True


        brickTexture = loader.loadTexture("models/brick-c.jpg")

        self.lstWalls = makeMaze()
        self.ptGrid = makePointGrid()

        #self.camera.setPos(self.ptGrid[len(self.ptGrid)-1][0])                                           
        self.focus = LVector3(0,1000,30)
     
        for row in range(len(self.ptGrid)):
            for col in range(len(self.ptGrid[row])):
                for n in range(2):
                    
                    #wall model made by 'TheCreator', https://free3d.com/3d-model/brick-wall-51172.html
                    self.wall = loader.loadModel("models/walls")
                    self.wall.setTexture(brickTexture)
                    self.wall.setScale(25.3)
                    self.wall.setPos(self.ptGrid[row][col])
                    self.wallC = self.wall.find("**/collideWall")
                    self.wallC.node().setIntoCollideMask(BitMask32.bit(0))
                    self.wallC.show()

                    #right of cell
                    if n == 0:
                        if self.lstWalls[row][col][n] == 1: 
                            self.wall.setX(self.wall, 1.05)
                            self.wall.setZ(5)
                            self.wall.reparentTo(render)

                    #down of cell
                    else: 
                        if self.lstWalls[row][col][n] == 1:
                            self.wall.setHpr(90,0,0)
                            self.wall.setX(self.wall, -3)    
                            self.wall.setZ(5)      
                            self.wall.reparentTo(render)

                    
        self.spacing = self.ptGrid[0][1][0] - self.ptGrid[0][0][0]

        self.exit = loader.loadModel('models/walls')
        self.exit.setScale(25.3)
        self.exit.setColorScale(0.6,0.6,1,1)

        self.exitCoord, wall = generateDoor(self.ptGrid, self.lstWalls)
        self.exitPos = self.ptGrid[self.exitCoord[0]][self.exitCoord[1]]
        self.exit.setPos(self.exitPos)

        for n in range(2):
            if n == 0:
                if wall[n] == 2: 
                    self.exit.setX(self.exit, 1.15)
                    self.exit.setZ(5)

            #down of cell
            else: 
                if wall[n] == 2:
                    self.exit.setHpr(90,0,0)
                    self.exit.setX(self.exit, -3.2)
                    self.exit.setZ(5)         

        self.exit.reparentTo(render)
        self.exit.detachNode()

        numPpl = 15 #make first pos minotaur
        pplLst = []
        pplLst = generatePosLst(pplLst, numPpl, self.ptGrid, self.spacing)


        targetPos = pplLst[random.randint(1, len(pplLst)-1)]
        print('target:',targetPos)

        #ball model from panda3D ball in maze demo
        num = 0
        for pos in range(1, len(pplLst)):
            num += 1

            #if the person in the list is the minotaur's target, set it's 
            #name to self.target
            if pplLst[pos] == targetPos:
                self.target = loader.loadModel("models/alfred")
                self.target.setPos(pplLst[pos])
                self.target.setScale(5)
                self.target.reparentTo(render)

                self.targetK = self.target.attachNewNode(CollisionNode('targetDie'))
                self.targetK.node().addSolid(CollisionSphere(0, 0, 5, 6))
                self.targetK.node().setIntoCollideMask(BitMask32.bit(2))
                #self.targetK.show()

                self.targetS = self.target.attachNewNode(CollisionNode('targetSave'))
                self.targetS.node().addSolid(CollisionSphere(0, 0, 5, 6))
                self.targetS.node().setIntoCollideMask(BitMask32.bit(1))
                #self.targetS.show()

            #otherwise, keep it as a self.ppl
            else: 
                self.ppl = loader.loadModel("models/alfred")
                self.ppl.setPos(pplLst[pos])
                self.ppl.setScale(5)

                #put a tag on each person so we can tell them apart
                self.ppl.setTag('personNum', str(num))
                self.ppl.reparentTo(render)
  
                #make it so that the people can be collision detected
                self.pplC = self.ppl.attachNewNode(CollisionNode('pplCollision'))
                self.pplC.node().addSolid(CollisionSphere(0, 0, 5, 7))
                self.pplC.node().setIntoCollideMask(BitMask32.bit(1))
                self.pplC.setTag('personCNum', str(num))
                #self.pplC.show()
        
        #first index in pplLst = minotar
        minotaurPos = pplLst[0]

        #Minotaur 3d model by 'Clint Bellanger' https://opengameart.org/content/minotaur
        self.minotaur = Actor("models/TheMinotaur")
        self.minotaur.setPos(minotaurPos)
        self.minotaur.setScale(25)
        self.minotaur.reparentTo(render)


        minotaurTexture = loader.loadTexture("models/catfur.jpg")
        self.minotaur.setTexture(minotaurTexture)

        self.minC = self.minotaur.attachNewNode(CollisionNode('minCollision'))
        self.minC.node().addSolid(CollisionSphere(0 , 0, 1, 0.5))
        self.minC.node().setFromCollideMask(BitMask32.bit(2))
        #self.minC.node().setIntoCollideMask(BitMask32.bit(1))
        #self.minC.show()

        self.minBat = self.minotaur.attachNewNode(CollisionNode('battle'))
        self.minBat.node().addSolid(CollisionSphere(0, 0, 1, 4.3))
        self.minBat.node().setIntoCollideMask(BitMask32.bit(1))
        self.minBat.show()

        self.minHit = self.minotaur.attachNewNode(CollisionNode('hit'))
        self.minHit.node().addSolid(CollisionSphere(0, 0, 1.5, 0.4))
        self.minHit.node().setIntoCollideMask(BitMask32.bit(3))

        self.minAtk = self.minotaur.attachNewNode(CollisionNode('attack'))
        self.minAtk.node().addSolid(CollisionSphere(0, 0, 1.85, 0.4))
        self.minAtk.node().setIntoCollideMask(BitMask32.bit(4))
        self.minAtk.show()

        self.cTrav = CollisionTraverser()
        self.cHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.minC, self.cHandler)
        self.cTrav.addCollider(self.minAtk, self.cHandler)

        self.minotaurObj = Minotaur(self.minotaur.getPos())

        #find the path the minotaur takes to kill the person
        self.killPath = self.minotaurObj.findPerson(minotaurPos, targetPos, self.ptGrid, self.lstWalls, self.spacing)
        self.minSpeed = 1
        self.sleepDelay = 13
        self.killFlag = True
        self.killDone = False
        self.killPause = False
        self.killPaused = False

        self.hit = False
        self.hurtTime = 0
        self.minDied = False
        self.minTimeDied = 0
        self.attackTrig = False
        self.warningTrig = True

        taskMgr.add(self.minotaurKilling, "minotaurKilling")
        taskMgr.add(self.minotaurDie, 'minotaurDied')
        taskMgr.add(self.pauseKill, 'pauseKill')

        self.saved = 0
        self.addSaved = False
        self.saveTrig = False

        taskMgr.add(self.displaySaved, "saved")
        
        #collisions
        #create a ball for collisions 
        self.camBall = loader.loadModel("models/ball")
        self.camBall.setPos(self.spacing/2, self.spacing/2, -1)
        self.camBall.setScale(10)
        #self.camBall.setColorScale(0, 1, 0.7, 1)
        self.camBall.reparentTo(render)

        self.playerPos = (0,0,0)
        
        self.camBallC = self.camBall.find("**/ball")
        #self.camBallC = self.camBall.attachNewNode(CollisionNode('camCollision'))
        #self.camBallC.node().addSolid(CollisionSphere(0, 0, 0, 1.2))
        self.camBallC.node().setFromCollideMask(BitMask32.bit(0))

        self.pusher = CollisionHandlerPusher()
        self.pusher.addCollider(self.camBallC, self.camBall)

        self.cTrav.addCollider(self.camBallC, self.pusher)
        self.camBallC.setPos(0,0.0002,0)

        self.camC = self.camera.attachNewNode(CollisionNode('cameraCollision'))
        self.camC.node().addSolid(CollisionSphere(0, 0, 0, 0.01))
        self.camC.node().setFromCollideMask(BitMask32.bit(1))
        self.camC.node().setIntoCollideMask(BitMask32.bit(4))
        self.camC.show()

        self.cTrav.addCollider(self.camC, self.cHandler)

        taskMgr.add(self.disappear, "disappear")

        #sting-sword model created by  KangaroOz 3D, from: https://www.turbosquid.com/FullPreview/Index.cfm/ID/1125944
        self.sword = loader.loadModel('models/sting-sword')
        self.sword.wrtReparentTo(self.camBall)
        self.sword.detachNode()
        
        self.sword.setY(1)
        self.sword.setX(0.5)
        self.sword.setZ(0.2)
        self.sword.setScale(0.07)


        self.swordC = self.sword.attachNewNode(CollisionNode('stab'))
        self.swordC.node().addSolid(CollisionSphere(0, 25, 0, 2))
        self.swordC.node().setFromCollideMask(BitMask32.bit(3))
        #self.swordC.show()

        self.attacked = False
        self.stabbing = False

        self.cTrav.add_collider(self.swordC, self.cHandler)


        swordTexture = loader.loadTexture("models/Sting_Emissive.png")
        self.sword.setTexture(swordTexture)

        self.stabDelay = 0

        self.redBarL = loader.loadModel('models/walls')
        self.redBarL.setScale(3)
        self.redBarL.setColorScale(250,0,0,1)
        self.redBarL.setPos(38.5, 60,5)
        self.redBarL.wrtReparentTo(self.camBall)
        self.redBarL.detachNode()

        self.redBarR = loader.loadModel('models/walls')
        self.redBarR.setScale(3)
        self.redBarR.setColorScale(250,0,0,1)
        self.redBarR.setPos(55.7,60,5)
        self.redBarR.wrtReparentTo(self.camBall)
        self.redBarR.detachNode()
        
        self.hurtTimeP = 0

        #make list of controls 
        self.keyMap = {
            "left": 0, "right": 0, "forward": 0, "backward": 0, "cam-left": 0,\
             "cam-right": 0, "stab":0, "map": 0, "instrMode":0, "gameMode":0}

        # Make the mouse invisible, turn off normal mouse controls
        self.disableMouse()
        props = WindowProperties()
        props.setCursorHidden(True)
       

        # Set the current viewing target
        self.heading = 0
        self.pitch = 0
        self.last = 0

        self.startMode = True
        self.startTrig = True
        self.startDestroy = True
        self.instrMode = False
        self.instrTrig = True
        self.instrShown = False
        self.instrDestroy = True
        self.gameMode = False

        self.bkGround = loader.loadModel('models/walls')
        self.bkGround.reparentTo(self.camBall)
        self.bkGround.setColorScale(0,0.5,0.55,1)
        self.bkGround.setPos(-1,3,0)

        taskMgr.add(self.showStart, "start-screen")


        taskMgr.add(self.controlCamera, "camera-task")
        self.accept("escape", sys.exit, [0])

        self.accept("o", self.setKey, ["instrMode", True])
        self.accept("p", self.setKey, ["gameMode", True])

        self.accept("arrow_left", self.setKey, ["left", True])
        self.accept("arrow_right", self.setKey, ["right", True])
        self.accept("arrow_up", self.setKey, ["forward", True])
        self.accept("arrow_down", self.setKey, ["backward", True])
        self.accept("w", self.setKey, ["stab", True])
        self.accept("s", self.setKey, ["down", True])
        self.accept("arrow_left-up", self.setKey, ["left", False])
        self.accept("arrow_right-up", self.setKey, ["right", False])
        self.accept("arrow_up-up", self.setKey, ["forward", False])
        self.accept("arrow_down-up", self.setKey, ["backward", False])
        self.accept("w-up", self.setKey, ["stab", False])
        self.accept("s-up", self.setKey, ["down", False])


        self.accept("a", self.setKey, ["cam-left", True])
        self.accept("d", self.setKey, ["cam-right", True])
        self.accept("a-up", self.setKey, ["cam-left", False])
        self.accept("d-up", self.setKey, ["cam-right", False])

        self.accept("space", self.setKey, ["map", True])
        self.accept("space-up", self.setKey, ["map", False])


        
    def setKey(self, key, value):
        self.keyMap[key] = value

    def startKill(self): 
        try:
            self.target.setColorScale(250,0,0,1)
        except: 
            pass
        intervalL = self.intervalLst()

        self.kill = Sequence(intervalL[0], name = 'kill person')
        for i in range(1, len(intervalL)):
            self.kill.append(intervalL[i])
        self.kill.start()

    def pauseKill(self, task):
        print(self.killPaused, self.killPause)
        if self.gameMode == True:

            if self.killDone == True:
                self.kill.finish()
               
            if self.killPaused == False and self.killPause == True:
                print('hmmmmmmmmmmmm')
                self.kill.pause()
                self.killPaused = True

            if self.killPaused == True and self.killPause == False:
                self.kill.resume()
                self.killPaused = False

        return Task.cont

    def intervalLst(self):
        intervals = []
        for i in range(len(self.killPath)):
            intervals += [self.minotaur.posInterval(self.minSpeed, Point3(self.killPath[i]))]
        return intervals

    def stab(self, task):
        timer = globalClock.getFrameTime()
        
        speed = 0.2
        stabIn = LerpPosInterval(self.sword, speed, Point3(0,4,0.2))
        stabOut = LerpPosInterval(self.sword, speed, Point3(0.5,1,0.2))
        stab = Sequence(stabIn, stabOut, name = 'stab')
        stab.start()

        self.stabbing = True 

        if self.hit == True: 
            self.minotaurObj.hit()

            self.hurtTime = globalClock.getFrameTime()
            self.hurtShow(task)
            
            self.hit = False
            self.stabbing = False


    def hurtShow(self,  task):
        if self.hit == True:
            timer = globalClock.getFrameTime()
            if timer - self.hurtTime < 2:
                self.minotaur.setColorScale(180,0,0,1)
        return Task.cont

    def attack(self, task):
        if self.attackTrig == True:
            speed = 1
            turnSpeed = 0.5
            attackPos, distance, direction = self.minotaurObj.attack(self.camera.getPos(), self.minotaur.getPos(), \
                self.ptGrid, self.spacing, self.lstWalls)
            origPt = self.minotaur.getPos()
            if attackPos != None:
                attack = LerpPosInterval(self.minotaur, speed, Point3(attackPos))
                turnToPlayer = LerpHprInterval(self.minotaur, turnSpeed, self.minotaurObj.facePlayer(direction))
                if distance == 'short':
                    retract = LerpPosInterval(self.minotaur, speed, origPt)
                    attackSeq = Sequence(turnToPlayer, attack, retract, name = 'attack')
                    attackSeq.start()
                else: 
                    attackSeq = Sequence(turnToPlayer, attack, name = 'attack')
                    attackSeq.start()

            self.attackTrig = False

            
    def attackShow(self, task):
        if self.attacked == True:
            timer = globalClock.getFrameTime()
            if timer - self.hurtTimeP < 2:
                self.redBarL.reparentTo(self.camBall)
                self.redBarR.reparentTo(self.camBall)
            if self.loseHealth == True:
                self.playerHealth -= 10
                print(self.playerHealth)
                self.loseHealth = False

        return Task.cont


    def displaySaved(self, task):
        if self.gameMode == True:
            if self.saved == 0 and self.saveTrig == False:
                msg = 'Saved: ' + str(self.saved)
                self.displSaved = OnscreenText(text=msg, style=1, fg=(1, 1, 1, 1), scale=.05,
                                shadow=(0, 0, 0, 1),parent=base.a2dTopLeft, align=TextNode.ALeft,
                                 pos=(0.05, -1.9))
                self.saveTrig = True
            
            if self.addSaved == True and self.saveTrig == True and self.saved > 0:
                print('here')
                self.displSaved.destroy()
                msg = 'Saved: ' + str(self.saved)
                self.displSaved = OnscreenText(text=msg, style=1, fg=(1, 1, 1, 1), scale=.05,
                                shadow=(0, 0, 0, 1),parent=base.a2dTopLeft, align=TextNode.ALeft,
                                 pos=(0.05, -1.9))
                self.addSaved = False

        return Task.cont
        
    def minotaurKilling(self, task):
        if self.gameMode == True:
            #timer for minotaur sleeping
            timer = globalClock.getFrameTime()
            timeLeft = self.sleepDelay - int(timer)

            #put up the instructions before the minotaur wakes up
            if timeLeft >= 0:

                if self.warningTrig == True:
                    if timeLeft == 1:
                        msg = "You have 1 second to find the Minotaur before he wakes up!"
                    elif timeLeft == 0:
                        msg = "He's awake!"
                    else: 
                        msg = "You have " + str(timeLeft) + " seconds to find the Minotaur before he wakes up!"
                    
                    self.warning = OnscreenText(text=msg, style=1, fg=(1, 1, 1, 1), scale=0.08,
                                shadow=(0, 0, 0, 1),parent=base.a2dTopLeft, align=TextNode.ALeft,
                                 pos=(0.05, -0.08))
                    self.displayWarning = timer
                    self.warningTrig = False

                if timer - self.displayWarning > 0.92: 
                    self.warning.destroy()
                    self.warningTrig = True

            if timeLeft < 0:
                self.warning.destroy()

            #wake the minotaur up after time ends
            if timeLeft < 0 and self.killFlag == True:
                self.startKill()
                self.killFlag = False

            #make sure minotaur is always the right color
            if timer - self.hurtTime > 2:
                self.minotaur.setColorScaleOff()

            if timer - self.hurtTimeP > 2:
                self.redBarL.detachNode()
                self.redBarR.detachNode()

            if self.minDied == True:
                if timer - self.minTimeDied > 20:
                    self.minotaur.detachNode()
                    self.exit.reparentTo(render)
                    self.showRopes()

            if timer - self.hurtTimeP > 2:
                    self.loseHealth = True

        return Task.cont

    def minotaurDie(self, task):

        if self.minotaurObj.health <= 0 and self.minDied == False:
            dieSpeed = 3
            die = LerpHprInterval(self.minotaur, dieSpeed, (self.camera.getX(), 90, 5))
            die.start()
            self.minDied = True
            self.minTimeDied = globalClock.getDt()

        return Task.cont

    def showropes(self):
        ropeHeight = 30
        lastRope = findExitPos(self.exitPos, self.ptGrid, self.spacing)

        playerPos = findPlayerPos(self.camera.getPos(), self.spacing)
        playerPos = (playerPos[0], playerPos[1], ropeHeight)

        ropePath, ropeDir = findExit(playerPos, lastRope, self.ptGrid, self.lstWalls, self.spacing)
        lastDir = findDir(self.exitCoord, self.ptGrid)

        if ropeDir != None:
            ropeDir += [lastDir]

        #gold texture found at https://www.google.com/url?sa=i&source=images&cd=&cad=r\
        #ja&uact=8&ved=2ahUKEwjw76Lbv4rfAhVpvFkKHY3JDPYQjRx6BAgBEAU&url=http%3A%2F\
        #%2Fmetal.graphics%2Fgraphic%2Fbrushed%2Fgold-texture%2F&psig=AOvVaw1q3Yu\
        #xuuGvetU4fhA1cIqh&ust=1544161415078294
        
        goldTexture = loader.loadTexture("models/gold.jpg")
        if ropePath != None:

            #rope model by Robert J. Smith, https://www.cgtrader.com/free-3d-models/industrial/tool/knot-rope
            for pos in range(len(ropePath)):
                rope = loader.loadModel("models/rope1")
                rope.setPos(ropePath[pos])
                rope.setScale(3.6)
                rope.setZ(-5)

                if pos < len(ropeDir):
                    if ropeDir[pos] == 'e':
                        rope.setHpr(76,0,0)
                        rope.setX(rope.getX() + 75)
                        rope.setY(rope.getY() + 5)
                    if ropeDir[pos] == 'n':
                        rope.setHpr(166,0,0)
                        rope.setY(rope.getY() + 65)
                    if ropeDir[pos] == 'w':
                        rope.setHpr(256,0,0)
                        rope.setX(rope.getX() - 60)
                        rope.setY(rope.getY() - 9)
                    if ropeDir[pos] == 's':
                        rope.setHpr(-14,0,0)
                        rope.setY(rope.getY() - 70)
                        rope.setX(rope.getX() + 15)
                rope.setTexture(goldTexture)
                rope.reparentTo(render)

    def lostGame(self):
        lose = loader.loadModel('models/walls')
        lose.reparentTo(self.camBall)
        lose.setColorScale(0.1,0.1,0.1,1)
        lose.setPos(-1,3,0)

    def showStart(self, task):
        startMsg = "Welcome to Daedalus's Creation." 
        startMsg2 = "You have to kill the minotaur, navegate the labyrinth, and save the others."+"You have 30 seconds to find the Minotaur before he wakes up and starts killing your people."
        startMsg3 = "Good luck doing what no man has done before."
        startMsg4 = "Press 'o' for instructions on how to play."

        if self.startMode == True and self.startTrig == True:
            self.start = OnscreenText(text=startMsg, style=1, fg=(1, 1, 1, 1), scale=0.08,
                                shadow=(0, 0, 0, 1),parent=base.aspect2d, pos = (0,0.5), align=TextNode.ACenter, wordwrap= 15)
            self.start2 = OnscreenText(text=startMsg2, style=1, fg=(1, 1, 1, 1), scale=0.08,
                                shadow=(0, 0, 0, 1),parent=base.aspect2d, align=TextNode.ACenter, pos = (0,0.2), wordwrap= 20)

            self.start3 = OnscreenText(text=startMsg3, style=1, fg=(1, 1, 1, 1), scale=0.08,
                                shadow=(0, 0, 0, 1),parent=base.aspect2d, align=TextNode.ACenter, pos = (0,-0.2), wordwrap= 25)
            self.start4 = OnscreenText(text=startMsg4, style=1, fg=(1, 1, 1, 1), scale=0.1,
                                shadow=(0, 0, 0, 1),parent=base.aspect2d, align=TextNode.ACenter, pos = (0,-0.5), wordwrap= 25)
            self.startTrig = False

        if self.startMode == False and self.startDestroy == True: 
            self.start.destroy()
            self.start2.destroy()
            self.start3.destroy()
            self.start4.destroy()
            self.startDestroy = False

            task.remove()

        return Task.cont

    def showInstr(self):

        instrMsg = "Press the right and left arrow keys to move right and left."
        instrMsg1 = "Press the up and down arrow keys to move forwards and backwards."
        instrMsg2 = "Press the 'a' key to turn the camera left."
        instrMsg3 = "Press the 'd' key to turn the camera right."
        instrMsg4 = "Press the space key for a map of the labyrinth"
        instrMsg5 = "Press the 'w' key to attack." 
        instrMsg6 = "Press the 'p' key to start the game."

        if self.instrMode == True and self.instrTrig == True:

            self.instr = OnscreenText(text=instrMsg, style=1, fg=(1, 1, 1, 1), scale=0.08,
                                    shadow=(0, 0, 0, 1),parent=base.aspect2d, pos = (0,0.7), align=TextNode.ACenter, wordwrap= 30)
            self.instr1 = OnscreenText(text=instrMsg1, style=1, fg=(1, 1, 1, 1), scale=0.08,
                                    shadow=(0, 0, 0, 1),parent=base.aspect2d, pos = (0,0.5), align=TextNode.ACenter, wordwrap= 20)
            self.instr2 = OnscreenText(text=instrMsg2, style=1, fg=(1, 1, 1, 1), scale=0.08,
                                    shadow=(0, 0, 0, 1),parent=base.aspect2d, align=TextNode.ACenter, pos = (0,0.2), wordwrap= 20)
            self.instr3 = OnscreenText(text=instrMsg3, style=1, fg=(1, 1, 1, 1), scale=0.08,
                                    shadow=(0, 0, 0, 1),parent=base.aspect2d, align=TextNode.ACenter, pos = (0,0), wordwrap= 25)
            self.instr4 = OnscreenText(text=instrMsg4, style=1, fg=(1, 1, 1, 1), scale=0.08,
                                    shadow=(0, 0, 0, 1),parent=base.aspect2d, align=TextNode.ACenter, pos = (0,-0.2), wordwrap= 25)
            self.instr5 = OnscreenText(text=instrMsg5, style=1, fg=(1, 1, 1, 1), scale=0.08,
                                    shadow=(0, 0, 0, 1),parent=base.aspect2d, align=TextNode.ACenter, pos = (0,-0.4), wordwrap= 25)
            self.instr6 = OnscreenText(text=instrMsg6, style=1, fg=(1, 1, 1, 1), scale=0.1,
                                    shadow=(0, 0, 0, 1),parent=base.aspect2d, align=TextNode.ACenter, pos = (0,-0.6), wordwrap= 25)
            self.instrTrig = False
            self.instrShown = True

    def endInstr(self):

        if self.instrMode == False and self.instrDestroy == True and self.instrShown == True: 
            self.instr.destroy()
            self.instr1.destroy()
            self.instr2.destroy()
            self.instr3.destroy()
            self.instr4.destroy()
            self.instr5.destroy()
            self.instr6.destroy()
            self.instrDestroy = False

    #make the person disappear when it's touched
    def disappear(self,task):

        for i in range(self.cHandler.getNumEntries()):

            entry = self.cHandler.getEntry(i)
            fromNode = entry.getFromNodePath()
            intoNode = entry.getIntoNodePath()
            intoName = entry.getIntoNode().getName()
            fromName = entry.getFromNode().getName()

            #if the collision was with a person
            if (intoName == 'pplCollision' and fromName == 'cameraCollision'):
                num = intoNode.getTag("personCNum")
                tag = '**/=personNum=' + num
                #finds the person player collided into and removes them
                person = render.find(tag)
                person.removeNode()

                #add one to saved counter
                self.saved += 1
                self.addSaved = True
                self.displSaved.destroy()
                return Task.cont


            if intoName == 'targetSave' and fromName == 'cameraCollision':
                print('saved!')
                self.target.removeNode()
                self.saved += 1
                self.addSaved = True
                return Task.cont
            
            if intoName == 'targetDie' and fromName == 'minCollision':
                print('ahhhhhhhhh!')
                self.target.removeNode()
                self.killDone = True
                return Task.cont

            #if minotaur gets stabbed by player
            if intoName == 'hit' and fromName == 'stab':

                if self.stabbing == True:
                    self.hit = True
                return Task.cont

            if intoName == 'cameraCollision' and fromName == 'attack':
                print('attacked!!!!!')
                self.attacked = True
                self.hurtTimeP = globalClock.getFrameTime()
                self.attackShow(task)

                if self.playerHealth < 0:
                    self.lostGame()
                return Task.cont

            if (intoName == 'battle' and fromName == 'cameraCollision' and self.killFlag == False) \
                or (intoName == 'minCollision' and fromName == 'cameraCollision' and self.killFlag == False):
                print('pause')
                self.killPause = True 
                return Task.cont

            else: 
                print('hereeeee')
                self.killPause = False

            print('killPause', self.killPause)
        return Task.cont

    #structure from panda3d bump mapping demo
    def controlCamera(self, task):

        dt = globalClock.getDt()
       
        self.camera.setHpr(self.heading, self.pitch, 0)
        self.camBall.setHpr(self.heading, self.pitch, 0)
        dir = self.camera.getMat().getRow3(1)

        camPos = (self.camBall.getPos()[0], self.camBall.getPos()[1], 6)
        self.camera.setPos(camPos)

        if self.keyMap["instrMode"] == True: 
            self.startMode = False
            self.instrMode = True
            self.showInstr()

        if self.keyMap["gameMode"] == True:
            self.instrMode = False
            self.gameMode = True
            self.bkGround.detachNode()
            self.endInstr()

        if self.gameMode == True:

            #move camera right and left
            if self.keyMap["left"]:
                self.camBall.setX(self.camBall, -10*dt)
            if self.keyMap["right"]:
                self.camBall.setX(self.camBall, +10*dt)
            if self.keyMap["forward"]:
                self.camBall.setY(self.camBall, +10*dt)
            if self.keyMap["backward"]:
                self.camBall.setY(self.camBall, -10*dt)
           

            #rotate camera
            if self.keyMap["cam-right"]:
                self.heading = self.heading -  100*dt
            if self.keyMap["cam-left"]:
                self.heading = self.heading +  100*dt
            self.focus = self.camera.getPos() + (dir * 5)
            self.last = task.time

            
            if self.keyMap['stab']:
                timer = globalClock.getFrameTime()
                if timer - self.stabDelay > 0.5:
                    self.stab(task)
                    self.stabDelay = timer
                    self.attack(task)
                    self.attackTrig = True
                    
            #show map 
            if self.keyMap["map"] == True:
                center = (len(self.ptGrid))/2*self.spacing
                self.camera.setPos(center,center, 1.8*len(self.ptGrid)*self.spacing)
                self.camera.lookAt(center, center, 0)
                self.sword.detachNode()
                if self.killFlag == False and self.killPause == True:
                    self.kill.pause()

                self.camBall.reparentTo(render)
                self.camBall.setScale(20)
                self.camBall.setColorScale(0, 0.5, 1, 1)

            if self.keyMap["map"] == False and self.startMode == False and self.instrMode == False:
                self.sword.reparentTo(self.camBall)
                self.camBall.setColorScaleOff()
                self.camBall.setScale(10)

        
        return Task.cont

demo = Labrintth()
demo.run()



