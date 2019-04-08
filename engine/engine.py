


from time import sleep
import copy

from engine.npc import Npc
from engine.gameObjects import *
from engine.inventory import Inventory, playerBank


import datetime
import random
import configparser








"""
TODO:


#fix port locations, make shops and banks spawn alternatively
#make npcs not move when players around, start fight with a, and attack by clicking
    -make sea-based npcs, that work kinda same, but fights with ships
#default sea fight mode is swimming, low hp etch.
    -best loot from pirates, much harder than on land, but easier with a ship
#create ships that have limited hp, used to fight sea-based npcs?
#ports heal ships automatically or paid?, make hospitals(or inns) that heal player hp

#allow team fighting npcs, that way groups are useful (limit npc attack to groups to be lower than to player)
#TRADING?


### secondary todo:

#make browser use the same 0.2 second rules as the server, even though mostly pointless

#make trees respawn after a time?, now respawn when area is left
#faction areas?, rnd, generate enemy levels based on faction area, 1 to nullsec, pvp?

#pringtgamestate shared for multiple worker threads as it's the slowest function to run by far


#TESTING:
#FIX OTHER PLAYER LOCATIONS WHEN HOPPING VERTICALLY (LINE 507)



KIND OF DONE:
#generate islands on some mapsquares of random size from a seed value
    -make a square of certain size, and after that make passes on all the ground areas,
    and expand them based on their coordinate and the seed number, set limit to recursion

#generate json file of the map
#implement for eg. flask server which sends the json to browser
    #has to be done with sockets as otherwise there would be too many post requests
#make map visible in bowser
#send player inputs from browser to server
#-update server gamestate and inform browser


FUTURE:
-inventory system
-player communication when nearby
-enemies??
-dungeons???
-shops on islands
    -additional content

"""


class MapSquare:
    """
    Define individual part of the world of size x and y, shown to the player in groups of 9
    """
    def __init__(self, x, y, xSize, ySize, seed):

        self.config = configparser.ConfigParser()
        self.config.read("./engine/config.cfg")
        self.sea = self.config["terrain"]["sea"]
        self.ground = self.config["terrain"]["ground"]


        self.seed_ = seed
        self.x_ = x
        self.y_ = y
        self.xSize_ = xSize
        self.ySize_ = ySize
        self.mapMatrix_ = [[self.sea for y in range(self.ySize_)] for x in range(self.xSize_)]


    #recursive function to spread the edges of an island square
    def expandIslandEdges(self, islandEdges, chunkSeed,  depth):
        """Takes a blocky island and spreads its edges pseudorandomly"""
        if (depth == 5):
            return

        for locationPair in islandEdges:
            #location pair is in form (y, x)
            if (locationPair[0] == 0 or locationPair[0] == self.ySize_ - 1):
                break
            if (locationPair[1] == 0 or locationPair[1] == self.xSize_ - 1):
                break
            else:
                #direction = random.randint(0,3)

                tileSeed = chunkSeed * locationPair[1] + chunkSeed * locationPair[0] + chunkSeed
                direction = tileSeed % 4

                xMoveDir = 0
                yMoveDir = 0
                if (direction == 0):
                    xMoveDir = -1
                if (direction == 1):
                    xMoveDir = 1
                if (direction == 2):
                    yMoveDir = -1
                if (direction == 3):
                    yMoveDir = 1
                #check if the tile is already ground
                if (self.mapMatrix_[locationPair[0] + yMoveDir][locationPair[1] + xMoveDir] == self.ground):
                    continue #then we shouldn't continue as it wont produce any meaningful progress
                pair = (locationPair[0] + yMoveDir, locationPair[1] + xMoveDir)
                self.mapMatrix_[locationPair[0] + yMoveDir][locationPair[1] + xMoveDir] = self.ground
                newMap = {}
                newMap[pair] = self.ground
                self.expandIslandEdges(newMap, chunkSeed, depth +1)
    def getSquare(self):
        """returns (and as such generates) the square this object is responsible for"""
        chunkSeed = self.seed_
        if (self.x_ != 0):
            chunkSeed = chunkSeed * self.x_ + chunkSeed // self.x_
        if (self.y_ != 0):
            chunkSeed = chunkSeed * self.y_ + chunkSeed // self.y_
        #print(chunkSeed)
        chunkSeed = chunkSeed % 1000001
        #print(chunkSeed)
        islandExists = chunkSeed % 3
        if (islandExists == 0):
            islandWidth = chunkSeed % 11 // 2
            islandHeight = chunkSeed % 13 // 2
            islandCenterOffset = chunkSeed % 5 // 2
            #print("size: ", islandWidth, islandHeight, islandCenterOffsetX)

            #island edges
            islandEdges = {};



            for y in range(self.ySize_ // 2 - islandCenterOffset, self.ySize_ // 2 - islandCenterOffset + islandHeight):
                for x in range(self.xSize_ // 2 - islandCenterOffset, self.xSize_ // 2 - islandCenterOffset + islandWidth):
                    self.mapMatrix_[y][x] = self.ground
                    #check if tile is on the edge of the island
                    if (y == self.ySize_ // 2 - islandCenterOffset or y == self.ySize_ // 2 - islandCenterOffset + islandHeight - 1):
                        # take note of the edges
                        islandEdges[(y, x)] = self.ground;
                    if (x == self.xSize_ // 2 - islandCenterOffset or x == self.xSize_ // 2 - islandCenterOffset + islandWidth -1):
                        #take note of the edges
                        islandEdges[(y, x)] = self.ground;
            #print(islandEdges);


            self.expandIslandEdges(islandEdges, chunkSeed, 0)


        return self.mapMatrix_



class Player:
    """defines a player and the actions they can take"""
    def __init__(self,name, worldX, worldY, x, y, seed, squareSize):


        self.config = configparser.ConfigParser()
        self.config.read("./engine/config.cfg")
        self.character = self.config["player"]["character"]
        self.others = self.config["player"]["otherPlayer"]
        self.ground = self.config["terrain"]["ground"]
        self.sea = self.config["terrain"]["sea"]
        self.actionDelay = int(self.config["player"]["actionDelay"])
        startingGold = int(self.config["player"]["money"])

        self.name_ = name
        self.seed_ = seed
        self.worldX_ = worldX
        self.worldY_ = worldY
        self.squareSize_ = squareSize
        self.x_ = x
        self.y_ = y
        self.moved_ = False #defines if player has moved on the server tick alaready
        self.acted = 0

        self.neightbors_ = []
        self.messages_ = []

        self.bank = playerBank()

        self.inventory = Inventory()
        self.inventory.addGold(startingGold)

        self.inShop = False
        self.inBank = False

        self.onLand = True
    def getName(self):
        return self.name_
    def getWorldX(self):
        return self.worldX_
    def getWorldY(self):
        return self.worldY_
    def getX(self):
        return self.x_
    def getY(self):
        return self.y_
    def getNeighbors(self):
        return self.neightbors_
    def addMessage(self, playerName, message):
        self.messages_.append(playerName + ": " + message)
    def getMessages(self):
        return self.messages_
    def clearMessages(self):
        self.messages_ = []
    def allowMoving(self): #reset this every server tick, so player can move again
        self.moved_ = False
    def canAct(self):
        if (self.acted == 0):
            return True
        else:
            return False
    def act(self):
        self.acted = self.actionDelay
    def regenActions(self):
        if (self.acted != 0):
            self.acted -= 1

    def getInv(self):
        return self.inventory
    #remove these
    def getInventory(self):
        return self.inventory.getAllItems()
    def getPhysicalInventory(self):
        return self.inventory.getPhysicalItems()
    def addItemToInv(self, item):
        self.inventory.addItem(item)
    def getGold(self):
        return self.inventory.getGold()
    def addGold(self, amount):
        self.inventory.addGold(amount)

    def isInShop(self):
        return self.inShop
    def goToShop(self):
        self.inShop = True

    def isInBank(self):
        return self.inBank
    def goToBank(self):
        self.inBank = True

    def getBankBalance(self):
        return self.bank.getBalance()

    def changeBankBalance(self, amount):
        if (amount > 0 and self.inventory.getGold() >= amount):
            self.bank.deposit(amount)
            self.inventory.removeGold(amount)
            return True
        elif (amount < 0 and self.bank.canWithDraw(abs(amount)) == True):
            self.bank.withDraw(abs(amount))
            self.inventory.addGold(abs(amount))
            return True
        else:
            return False

    def useHarbor(self):
        self.onLand = not self.onLand

    def canMove(self, tile):
        if (self.onLand and tile == self.ground):
            return True
        elif (not self.onLand and tile == self.sea):
            return True
        else:
            return False
        #check if player can move to the position

    def moveLeft(self, square, hx = -1, hy = -1):

        if (self.moved_ == True):
            return

        newX = self.x_ -1
        if (newX < 0):
            newX = self.squareSize_ -1
            self.worldX_ -= 1
        elif (self.canMove(square[self.y_][newX]) == False and not(newX == hx and self.y_ == hy)):
            return
        self.x_ = newX
        self.moved_ = True
        self.inShop = False
        self.inBank = False

    def moveRight(self, square, hx = -1, hy = -1):

        if (self.moved_ == True):
            return

        newX = self.x_ +1
        if (newX >= self.squareSize_):
            newX = 0
            self.worldX_ += 1
        elif (self.canMove(square[self.y_][newX]) == False and not(newX == hx and self.y_ == hy)):
            return
        self.x_ = newX
        self.moved_ = True
        self.inShop = False
        self.inBank = False

    def moveDown(self, square, hx = -1, hy = -1):
        if (self.moved_ == True):
            return
        newY = self.y_ + 1
        if (newY >= self.squareSize_):
            newY = 0
            self.worldY_ += 1
        elif (self.canMove(square[newY][self.x_]) == False and not(self.x_ == hx and newY == hy)):
            return
        self.y_ = newY
        self.moved_ = True
        self.inShop = False
        self.inBank = False

    def moveUp(self, square, hx = -1, hy = -1):
        if (self.moved_ == True):
            return

        newY = self.y_ - 1
        if (newY < 0):
            newY = self.squareSize_ -1
            self.worldY_ -= 1
        elif (self.canMove(square[newY][self.x_]) == False and not(self.x_ == hx and newY == hy)):
            return
        self.y_ = newY
        self.moved_ = True
        self.inShop = False
        self.inBank = False


    def doNpcExist(self, npcs, area):

        if (any(self.ground in tileRow for tileRow in area)  == False):
            return True
        if ((self.worldX_, self.worldY_) not in npcs.keys()):
            #generate npcs for the level here
            possibleLocations = []
            for i in range(len(area)):
                for j in range(len(area[i])):
                    if (area[i][j] == self.ground):
                        possibleLocations.append((j,i))
            """spawn npc to pseudorandom location"""
            xseed = self.seed_ + self.worldX_ % 1000001
            yseed = self.seed_ - self.worldY_ % 1000003
            npcSeed = (xseed + yseed) % len(possibleLocations)

            location = possibleLocations[npcSeed]#random.choice(possibleLocations)
            return Npc("asd", self.worldX_, self.worldY_, location[0], location[1], 20)
            pass
        else:
            return True
            #set npcs visible in the mapsquare

    def printLocation(self, allPlayers, npcs, cache, trees, shops, banks, harbors):

        """bad name for the function, but this returns the whole map with they player in it"""
        areaToPrint = [[self.sea for y in range(self.squareSize_ * 3)] for x in range(self.squareSize_ * 3)]
        self.neightbors_ = []


        for thirdHeight in range(-1, 2):

            zero = ""
            if ((self.worldX_, self.worldY_ + thirdHeight) in cache):
                zero = cache[(self.worldX_, self.worldY_ + thirdHeight)]
            else:
                zeroSquare = MapSquare(self.worldX_, self.worldY_ + thirdHeight, self.squareSize_, self.squareSize_, self.seed_)
                zero = zeroSquare.getSquare()
                cache[(self.worldX_, self.worldY_ + thirdHeight)] = zero

            right = ""
            if ((self.worldX_ + 1, self.worldY_ + thirdHeight) in cache):
                right = cache[(self.worldX_ + 1, self.worldY_ + thirdHeight)]
            else:
                rightSquare = MapSquare(self.worldX_ + 1, self.worldY_ + thirdHeight, self.squareSize_, self.squareSize_, self.seed_)
                right = rightSquare.getSquare()
                cache[(self.worldX_ + 1, self.worldY_ + thirdHeight)] = right

            left = ""
            if ((self.worldX_ - 1, self.worldY_ + thirdHeight) in cache):
                left = cache[(self.worldX_ - 1, self.worldY_ + thirdHeight)]
            else:
                leftSquare = MapSquare(self.worldX_ - 1, self.worldY_ + thirdHeight, self.squareSize_, self.squareSize_, self.seed_)
                left = leftSquare.getSquare()
                cache[(self.worldX_ - 1, self.worldY_ + thirdHeight)] = left

            #deprecated, generates new square every frame, above uses caching
            #zeroSquare = MapSquare(self.worldX_, self.worldY_ + thirdHeight, self.squareSize_, self.squareSize_, self.seed_)
            #zero = zeroSquare.getSquare()
            #rightSquare = MapSquare(self.worldX_ + 1, self.worldY_ + thirdHeight, self.squareSize_, self.squareSize_, self.seed_)
            #right = rightSquare.getSquare()
            #leftSquare = MapSquare(self.worldX_ - 1, self.worldY_ + thirdHeight, self.squareSize_, self.squareSize_, self.seed_)
            #left = leftSquare.getSquare()
            for y in range(self.squareSize_):
                for x in range(self.squareSize_):
                    areaToPrint[(thirdHeight+1) * self.squareSize_ + y][x] = left[y][x]
                    #print(left[y][x], end="")
                for x in range(self.squareSize_):
                    if (x == self.x_ and y == self.y_ and thirdHeight == 0):
                        areaToPrint[(thirdHeight+1)  * self.squareSize_ + y][x + self.squareSize_] = zero[y][x]#"@"
                        #print("@", end="")
                    else:
                        areaToPrint[(thirdHeight+1)  * self.squareSize_ + y][x + self.squareSize_] = zero[y][x]
                        #print(zero[y][x], end="")
                for x in range(self.squareSize_):
                    areaToPrint[(thirdHeight+1) * self.squareSize_ + y][x + self.squareSize_ * 2] = right[y][x]
                    #print(right[y][x], end="")
                #print("")

        #trees
        for y in range(-1, 2):
            for x in range(-1, 2):
                if ((self.worldX_ + x, self.worldY_ + y) in trees):
                    for tree in trees[(self.worldX_ + x, self.worldY_ + y)]:
                        #print(tree.getX(), tree.getY(), tree.getCharacter())
                        areaToPrint[y * self.squareSize_ + self.squareSize_ + tree.getY()][x * self.squareSize_ + self.squareSize_ + tree.getX()] = tree.getCharacter()

        #shops
        for y in range(-1, 2):
            for x in range(-1, 2):
                if ((self.worldX_ + x, self.worldY_ + y) in shops):
                    for shop in shops[(self.worldX_ + x, self.worldY_ + y)]:
                        #print(tree.getX(), tree.getY(), tree.getCharacter())
                        areaToPrint[y * self.squareSize_ + self.squareSize_ + shop.getY()][x * self.squareSize_ + self.squareSize_ + shop.getX()] = shop.getCharacter()

        #banks
        for y in range(-1, 2):
            for x in range(-1, 2):
                if ((self.worldX_ + x, self.worldY_ + y) in banks):
                    for bank in banks[(self.worldX_ + x, self.worldY_ + y)]:
                        #print(tree.getX(), tree.getY(), tree.getCharacter())
                        areaToPrint[y * self.squareSize_ + self.squareSize_ + bank.getY()][x * self.squareSize_ + self.squareSize_ + bank.getX()] = bank.getCharacter()

        #harbors
        for y in range(-1, 2):
            for x in range(-1, 2):
                if ((self.worldX_ + x, self.worldY_ + y) in harbors):
                    for harbor in harbors[(self.worldX_ + x, self.worldY_ + y)]:
                        #print(tree.getX(), tree.getY(), tree.getCharacter())
                        areaToPrint[y * self.squareSize_ + self.squareSize_ + harbor.getY()][x * self.squareSize_ + self.squareSize_ + harbor.getX()] = harbor.getCharacter()

        #npcs
        for y in range(-1, 2):
            for x in range(-1, 2):
                if ((self.worldX_ + x, self.worldY_ + y) in npcs):
                    for npc in npcs[(self.worldX_ + x, self.worldY_ + y)]:
                        #print(tree.getX(), tree.getY(), tree.getCharacter())
                        areaToPrint[y * self.squareSize_ + self.squareSize_ + npc.getY()][x * self.squareSize_ + self.squareSize_ + npc.getX()] = npc.getCharacter()


        """
        if ((self.worldX_, self.worldY_) in trees):
            for tree in trees[(self.worldX_, self.worldY_)]:
                #print(tree.getX(), tree.getY(), tree.getCharacter())
                areaToPrint[self.squareSize_ + tree.getY()][self.squareSize_ + tree.getX()] = tree.getCharacter()
        """


        """
        for y in range(-1, 2):
            for x in range(-1, 2):
                if ((self.worldX_ + x, self.worldY_ + y) in npcs):
                    npc = npcs[(self.worldX_ + x, self.worldY_ + y)]
                    areaToPrint[y * self.squareSize_ + self.squareSize_ + npc.getY()][x * self.squareSize_ + self.squareSize_ + npc.getX()] = npc.getCharacter()
        """

        """
        if ((self.worldX_, self.worldY_) in npcs):
            npc = npcs[(self.worldX_, self.worldY_)]
            areaToPrint[self.squareSize_ + npc.getY()][self.squareSize_ + npc.getX()] = npc.getCharacter()
        """

        for value in allPlayers.values():
            worldx = value.getWorldX()
            worldy = value.getWorldY()
            x = value.getX()
            y = value.getY()

            if (value.getName == self.name_):
                continue
            if (worldx == self.worldX_ or worldx == self.worldX_+1 or worldx == self.worldX_ -1):
                if (worldy == self.worldY_ or worldy == self.worldY_+1 or worldy == self.worldY_ -1):
                    if (value.getName() != self.name_):
                        xloc = worldx - self.worldX_ + 1 #self.worldX_ - worldx + 1
                        yloc = worldy - self.worldY_ + 1
                        """ERROR was HERE"""
                        areaToPrint[yloc*self.squareSize_ + y][xloc*self.squareSize_ + x] = self.others
                        self.neightbors_.append(value.getName())


        worldx = self.worldX_
        worldy = self.worldY_
        x = self.x_
        y = self.y_


        xloc = worldx - self.worldX_ + 1 #self.worldX_ - worldx + 1
        yloc = self.worldY_ - worldy + 1
        areaToPrint[yloc*self.squareSize_ + y][xloc*self.squareSize_ + x] = self.character

        return areaToPrint


class Game:
    """Game runner object, handles players and passes their actions to the corresponding objects"""
    def __init__(self):

        self.config = configparser.ConfigParser()
        self.config.read("./engine/config.cfg")
        self.ground = self.config["terrain"]["ground"]

        self.allPlayers_ = {} #use as playername: Player()
        self.Npcs = {}
        self.squareSize_ = 20
        self.seed = 1254122


        self.squareCache = {} #use as [(x, y): 2Dlist of tiles]
        self.trees = {} #use as [(x, y): list of trees
        self.shops = {} #use as [(x, y): list of shops, only one per island atm
        self.banks = {} #use as [(x, y): list of banks, only one per island atm
        self.harbors = {} #use as [(x, y): list of harbors, only one per island


    def getSize(self):
        return 3* self.squareSize_
    def addPlayer(self, playerName):
        player = Player(playerName, 0, 0, 10, 10, self.seed, self.squareSize_);
        self.allPlayers_[playerName] = player
    def removePlayer(self, playerName):
        try:
            del self.allPlayers_[playerName]
        except KeyError:
            pass
    def allowMoving(self, playerName):
        self.allPlayers_[playerName].allowMoving()
        self.allPlayers_[playerName].regenActions()
    def addMessageToNeighbors(self, playerName, message):
        self.allPlayers_[playerName].addMessage(playerName, message)
        neighbors = self.allPlayers_[playerName].getNeighbors()
        for unit in neighbors:
            self.allPlayers_[unit].addMessage(playerName, message)
    def getMessages(self, playerName):
        return self.allPlayers_[playerName].getMessages()
    def clearMessages(self, playerName):
        self.allPlayers_[playerName].clearMessages()
    def movePlayerLeft(self, playerName):
        player = self.allPlayers_[playerName]
        hx = -1
        hy = -1
        if ((player.getWorldX(), player.getWorldY()) in self.harbors):
            hx = self.harbors[(player.getWorldX(), player.getWorldY())][0].getX()
            hy = self.harbors[(player.getWorldX(), player.getWorldY())][0].getY()

        if ((player.getWorldX(), player.getWorldY()) in self.squareCache):
            player.moveLeft(self.squareCache[(player.getWorldX(), player.getWorldY())], hx, hy)
    def movePlayerRight(self, playerName):
        player = self.allPlayers_[playerName]
        hx = -1
        hy = -1
        if ((player.getWorldX(), player.getWorldY()) in self.harbors):
            hx = self.harbors[(player.getWorldX(), player.getWorldY())][0].getX()
            hy = self.harbors[(player.getWorldX(), player.getWorldY())][0].getY()

        if ((player.getWorldX(), player.getWorldY()) in self.squareCache):
            player.moveRight(self.squareCache[(player.getWorldX(), player.getWorldY())], hx, hy)
    def movePlayerUp(self, playerName):
        player = self.allPlayers_[playerName]
        hx = -1
        hy = -1
        if ((player.getWorldX(), player.getWorldY()) in self.harbors):
            hx = self.harbors[(player.getWorldX(), player.getWorldY())][0].getX()
            hy = self.harbors[(player.getWorldX(), player.getWorldY())][0].getY()

        if ((player.getWorldX(), player.getWorldY()) in self.squareCache):
            player.moveUp(self.squareCache[(player.getWorldX(), player.getWorldY())], hx, hy)
    def movePlayerDown(self, playerName):
        player = self.allPlayers_[playerName]
        hx = -1
        hy = -1
        if ((player.getWorldX(), player.getWorldY()) in self.harbors):
            hx = self.harbors[(player.getWorldX(), player.getWorldY())][0].getX()
            hy = self.harbors[(player.getWorldX(), player.getWorldY())][0].getY()

        if ((player.getWorldX(), player.getWorldY()) in self.squareCache):
            player.moveDown(self.squareCache[(player.getWorldX(), player.getWorldY())], hx, hy)


    def generateTrees(self, square):
        baseLayer = self.squareCache[square]

        #npcSeed = (xseed + yseed) % len(possibleLocations)
        for y in range(len(baseLayer)):
            for x in range(len(baseLayer[y])):
                if (baseLayer[y][x] == self.ground):

                    chunkSeed = self.seed
                    if (x != 0):
                        chunkSeed = chunkSeed * square[0] + chunkSeed // x
                    if (y != 0):
                        chunkSeed = chunkSeed * square[1] + chunkSeed // y

                    xseed = chunkSeed % 162007
                    ##yseed = self.seed - (square[1] + x) % 1000003
                    addTree = (xseed) % 5
                    if (addTree == 0):
                        newTree = Tree(2, x, y)
                        if (square in self.trees):
                            self.trees[square].append(newTree)
                        else:
                            newList = [newTree]
                            self.trees[square] = newList

    def generateShop(self, square):
        baseLayer = self.squareCache[square]
        groundTiles = []
        for y in range(len(baseLayer)):
            for x in range(len(baseLayer[y])):
                if (baseLayer[y][x] == self.ground):
                    groundTiles.append((x, y))

        chunkSeed = self.seed
        if (square[0] != 0):
            chunkSeed = chunkSeed * square[0] + chunkSeed // square[0]
        if (square[1] != 0):
            chunkSeed = chunkSeed * square[1] + chunkSeed // square[1]

        tileNumber = chunkSeed % 170539 % len(groundTiles)

        self.shops[square] = [Shop(groundTiles[tileNumber][0], groundTiles[tileNumber][1])]

    def generateBank(self, square):
        baseLayer = self.squareCache[square]
        groundTiles = []
        for y in range(len(baseLayer)):
            for x in range(len(baseLayer[y])):
                if (baseLayer[y][x] == self.ground):
                    self.banks[square] = [GameBank(x, y)]
                    groundTiles.append((x, y))
        chunkSeed = self.seed
        if (square[0] != 0):
            chunkSeed = chunkSeed * square[0] + chunkSeed // square[0]
        if (square[1] != 0):
            chunkSeed = chunkSeed * square[1] + chunkSeed // square[1]

        tileNumber = chunkSeed % 170773 % len(groundTiles)

        self.banks[square] = [GameBank(groundTiles[tileNumber][0], groundTiles[tileNumber][1])]


    def generateHarbor(self, square):
        baseLayer = self.squareCache[square]
        groundTiles = []
        for y in range(len(baseLayer)):
            for x in range(len(baseLayer[y])):
                if (baseLayer[y][x] == self.ground):
                    self.harbors[square] = [Harbor(x, y)]
                    break

    def generateNpc(self, square):
        possibleLocations = []
        baseLayer = self.squareCache[square]

        for i in range(len(baseLayer)):
            for j in range(len(baseLayer[i])):
                if (baseLayer[i][j] == self.ground):
                    possibleLocations.append((j,i))
        """spawn npc to pseudorandom location"""
        xseed = self.seed + square[0] % 1000001
        yseed = self.seed - square[1] % 1000003
        npcSeed = (xseed + yseed) % len(possibleLocations)

        location = possibleLocations[npcSeed]#random.choice(possibleLocations)
        self.Npcs[square] =  [Npc("asd", square[0], square[1], location[0], location[1], 20)]


    def updateSquareCache(self):



        #remove unhabitated squares
        locations = [] #list of worldcoord pairs
        for player in self.allPlayers_.values():
            x = player.getWorldX()
            y = player.getWorldY()
            if ((x, y) not in locations):
                locations.append((x, y))
            if ((x-1, y) not in locations):
                locations.append((x-1, y))
            if ((x+1, y) not in locations):
                locations.append((x+1, y))
            if ((x, y-1) not in locations):
                locations.append((x, y-1))
            if ((x-1, y-1) not in locations):
                locations.append((x-1, y-1))
            if ((x+1, y-1) not in locations):
                locations.append((x+1, y-1))
            if ((x, y+1) not in locations):
                locations.append((x, y+1))
            if ((x-1, y+1) not in locations):
                locations.append((x-1, y+1))
            if ((x+1, y+1) not in locations):
                locations.append((x+1, y+1))
        #print(locations)
        newCache = {}
        for square in self.squareCache:
            if (square in locations):
                newCache[square] = self.squareCache[square]
        self.squareCache = newCache




        #print(len(self.squareCache))

        newTrees = {}
        for trees in self.trees:
            if (trees in locations):
                newTrees[trees] = self.trees[trees]
        self.trees = newTrees
        #print(len(self.trees.keys()))

        newShops = {}
        for shops in self.shops:
            if (shops in locations):
                newShops[shops] = self.shops[shops]
        self.shops = newShops

        newBanks = {}
        for banks in self.banks:
            if (banks in locations):
                newBanks[banks] = self.banks[banks]
        self.banks = newBanks

        newHarbors = {}
        for harbor in self.harbors:
            if (harbor in locations):
                newHarbors[harbor] = self.harbors[harbor]
        self.harbors = newHarbors

        newNpcs = {}
        for npc in self.Npcs:
            if (npc in locations):
                newNpcs[npc] = self.Npcs[npc]
        self.Npcs = newNpcs



        """update trees here"""
        for square in self.squareCache:
            if (square not in self.trees):
                if (any(self.ground in sublist for sublist in self.squareCache[square])):
                    self.generateTrees(square)


        for square in self.squareCache:
            if (square not in self.shops):
                if (any(self.ground in sublist for sublist in self.squareCache[square])):
                    self.generateShop(square)

        for square in self.squareCache:
            if (square not in self.banks):
                if (any(self.ground in sublist for sublist in self.squareCache[square])):
                    self.generateBank(square)


        for square in self.squareCache:
            if (square not in self.harbors):
                if (any(self.ground in sublist for sublist in self.squareCache[square])):
                    self.generateHarbor(square)



        for square in self.squareCache:
            if (square not in self.Npcs):
                if (any(self.ground in sublist for sublist in self.squareCache[square])):
                    self.generateNpc(square)


        """move npcs"""
        for i in (self.Npcs):
            if (i in self.squareCache):
                for npc in self.Npcs[i]:
                    npc.move(self.squareCache[i])

    def printGameState(self, playerName): #again bad name, just returns stuff

        return self.allPlayers_[playerName].printLocation(self.allPlayers_, self.Npcs, self.squareCache, self.trees, self.shops, self.banks, self.harbors)
    def getActionStatus(self, playerName):
        player = self.allPlayers_[playerName]
        if (player.isInBank()):
            return "bank"
        if (player.isInShop()):
            return "shop"
        else:
            return "none"

    def getItems(self, playerName):
        return self.allPlayers_[playerName].getInventory()

    def getBankBalance(self, playerName):
        return self.allPlayers_[playerName].getBankBalance()

    def getShopSell(self, playerName):
        player = self.allPlayers_[playerName]
        if (player.isInShop()):
            #return items player has and their values
            items = player.getPhysicalInventory().keys() #remove physical for thesting
            x = player.getWorldX()
            y = player.getWorldY()

            shop = self.shops[(x, y)][0]

            itemsAndValues = {}
            for item in items:
                itemsAndValues[item] = shop.getSellPrice(item)
            return itemsAndValues
        return False

    def getShopBuy(self, playerName):
        player = self.allPlayers_[playerName]
        if (player.isInShop()):
            x = player.getWorldX()
            y = player.getWorldY()

            shop = self.shops[(x, y)][0]
            catalog = copy.deepcopy(shop.getBuyPrices())
            return catalog
        return False

    def doAction(self, playerName):
        player = self.allPlayers_[playerName]

        if (player.canAct() == False):
            return

        x = player.getWorldX()
        y = player.getWorldY()

        #handle harbors
        if ((x, y) in self.harbors):
            for harbor in self.harbors[(x, y)]:
                if (harbor.getX() == player.getX() and harbor.getY() == player.getY()):
                    player.act()
                    player.useHarbor()
                    player.addMessage("Game", "You use the harbor.")
                    return




        #handle banks
        if ((x, y) in self.banks):
            for bank in self.banks[(x, y)]:
                if (bank.getX() == player.getX() and bank.getY() == player.getY()):
                    if (not player.isInBank()):
                        player.act()
                        player.goToBank()
                        player.addMessage("Game", "You enter a bank.")
                    return

        #handle shops
        if ((x, y) in self.shops):
            for shop in self.shops[(x, y)]:
                if (shop.getX() == player.getX() and shop.getY() == player.getY()):
                    if (not player.isInShop()):
                        player.act()
                        player.goToShop()
                        player.addMessage("Game", "You enter a shop.")
                    return


        #handle trees
        if ((x, y) in self.trees):
            for tree in self.trees[(x, y)]:
                if (tree.getX() == player.getX() and tree.getY() == player.getY()):
                    player.act()
                    tree.hit()
                    if (not tree.isAlive()):
                        player.addMessage("Game", "You hit a tree and cut it down.")
                        player.addItemToInv(tree.getDrops())
                        self.trees[(x, y)].remove(tree)
                    else:
                        player.addMessage("Game", "You hit a tree.")
                    return

    def changeBankBalance(self, playerName, amount):
        player = self.allPlayers_[playerName]
        if (player.isInBank()):
            x = player.getWorldX()
            y = player.getWorldY()
            bank = self.banks[(x, y)][0]
            if (bank.getX() == player.getX() and bank.getY() == player.getY()):
                if (amount % 1 != 0): #check if whole number
                    return

                if (amount > 0):
                    success = player.changeBankBalance(amount)
                    if (success):
                        player.addMessage("Game", "You deposited "+str(amount)+" gold.")
                elif (amount < 0):
                    success = player.changeBankBalance(amount)
                    if (success):
                        player.addMessage("Game", "You withdrew "+str(abs(amount))+" gold.")
                    else:
                        player.addMessage("Game", "You are too broke.")






    def buyItem(self, playerName, item):
        player = self.allPlayers_[playerName]
        if (player.isInShop()):
            x = player.getWorldX()
            y = player.getWorldY()
            shop = self.shops[(x, y)][0]
            if (shop.getX() == player.getX() and shop.getY() == player.getY()):
                value = shop.getBuyPrice(item)
                if (value != False):
                    gold = player.getGold()
                    if (gold >= value):
                        inv = player.getInv()
                        value = shop.buyItem(item)
                        player.addGold(-1* value)
                        player.addItemToInv(item)

                        player.addMessage("Game", "You bought a "+item+" for "+str(value)+" gold.")
                    else:
                        player.addMessage("Game", "You are too broke.")


    def sellItem(self, playerName, item):
        player = self.allPlayers_[playerName]
        if (player.isInShop()):
            if (item in player.getPhysicalInventory().keys()):
                x = player.getWorldX()
                y = player.getWorldY()
                if ((x, y) in self.shops):
                    shop = self.shops[(x, y)][0]
                    if (shop.getX() == player.getX() and shop.getY() == player.getY()):
                        value = shop.sellItem(item)
                        inv = player.getInv()
                        inv.removeItem(item)
                        inv.addGold(value)
                        player.addMessage("Game", "You sold a "+item+" for "+str(value)+" gold.")






"""
#testing purposes only
game = Game()

game.addPlayer("asd")
game.addPlayer("asd2")
game.moveRight("asd")
game.printGameState("asd")
"""
