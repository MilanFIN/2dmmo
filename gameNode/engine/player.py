

import copy

from engine.npc import *
from engine.gameObjects import *
from engine.inventory import *
from engine.pseudo import *
from engine.items import *

import configparser
import json

class MapSquare:
    """
    Define individual part of the world of size x and y, shown to the player in groups of 9
    """
    def __init__(self, x, y, xSize, ySize, seed):

        self.config = configparser.ConfigParser()
        self.config.read("./engine/config.cfg")
        self.sea = self.config["terrain"]["sea"]
        self.ground = self.config["terrain"]["ground"]
        self.worldSize = int(self.config["terrain"]["worldRadius"])
        if (self.worldSize < 3):
            self.worldSize = 3

        self.seed_ = seed
        self.x_ = x
        self.y_ = y
        self.xSize_ = xSize
        self.ySize_ = ySize
        self.mapMatrix_ = [[self.sea for y in range(self.ySize_)] for x in range(self.xSize_)]


    #recursive function to spread the edges of an island square
    def expandIslandEdges(self, islandEdges,  depth):
        """Takes a blocky island and spreads its edges pseudorandomly"""
        if (depth == 5):
            return

        for locationPair in islandEdges:
            #location pair is in form (y, x)
            if (locationPair[0] == 1 or locationPair[0] == self.ySize_ - 2):
                break
            if (locationPair[1] == 1 or locationPair[1] == self.xSize_ - 2):
                break
            else:
                #direction = random.randint(0,3)

                """
                tileSeed = chunkSeed * locationPair[1] + chunkSeed * locationPair[0] + chunkSeed
                direction = tileSeed % 4
                """
                direction = pseudo.getIslandExpansionDirection(locationPair[1], locationPair[0], self.x_ ,self.y_ ,self.seed_)

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
                self.expandIslandEdges(newMap, depth +1)
    def getSquare(self):
        """returns (and as such generates) the square this object is responsible for"""
        """
        chunkSeed = self.seed_
        if (self.x_ != 0):
            chunkSeed = chunkSeed * self.x_ + chunkSeed // self.x_
        if (self.y_ != 0):
            chunkSeed = chunkSeed * self.y_ + chunkSeed // self.y_
        #print(chunkSeed)
        chunkSeed = chunkSeed % 1000001
        #print(chunkSeed)
        islandExists = chunkSeed % 3
        """

        if (self.x_ >= self.worldSize-1 or self.y_ >= self.worldSize-1 or self.x_ <= -self.worldSize+1 or self.y_ <= -self.worldSize+1 ):
            return self.mapMatrix_

        elif (pseudo.islandExists(self.x_, self.y_, self.seed_)):
            """
            islandWidth = chunkSeed % 11 // 2
            islandHeight = chunkSeed % 13 // 2
            islandCenterOffset = chunkSeed % 5 // 2
            #print("size: ", islandWidth, islandHeight, islandCenterOffsetX)
            """
            islandWidth, islandHeight, islandCenterOffset = pseudo.getIslandDimensions(self.x_, self.y_, self.seed_, self.worldSize)

            #island edges
            islandEdges = {};



            for y in range((self.ySize_ - islandHeight )//2, (self.ySize_ - islandHeight )//2+ islandHeight): #range(self.ySize_ // 2 - islandCenterOffset, self.ySize_ // 2 - islandCenterOffset + islandHeight):
                for x in range((self.xSize_ - islandWidth )//2, (self.xSize_ - islandWidth )//2+ islandWidth):  #range(self.xSize_ // 2 - islandCenterOffset, self.xSize_ // 2 - islandCenterOffset + islandWidth):
                    self.mapMatrix_[y][x] = self.ground
                    #check if tile is on the edge of the island
                    if (y == (self.ySize_ - islandHeight )//2 or y == (self.ySize_ - islandHeight )//2+ islandHeight - 1):
                        # take note of the edges
                        islandEdges[(y, x)] = self.ground;
                    if (x == (self.xSize_ - islandWidth )//2 or x == (self.xSize_ - islandWidth )//2+ islandWidth -1):
                        #take note of the edges
                        islandEdges[(y, x)] = self.ground;
            #print(islandEdges);

            #important
            self.expandIslandEdges(islandEdges, 0)


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
        self.empty = self.config["terrain"]["empty"]

        self.worldSize = int(self.config["terrain"]["worldRadius"])
        self.actionDelay = int(self.config["player"]["actionDelay"])
        self.attack = int(self.config["player"]["attack"])
        self.counterAttack = int(self.config["player"]["counterAttack"])
        self.hp = int(self.config["player"]["hp"])
        self.maxHp = int(self.config["player"]["hp"])

        self.fightTime = int(self.config["player"]["fightTime"]) * 5

        startingGold = int(self.config["player"]["money"])

        self.name_ = name
        self.seed_ = seed

        self.worldX_ = worldX
        self.worldY_ = worldY
        self.x_ = x
        self.y_ = y

        self.originWX = worldX
        self.originWY = worldY
        self.originX = x
        self.originY = y

        self.squareSize_ = squareSize
        self.moved_ = False #defines if player has moved on the server tick alaready
        self.acted = 0
        self.inFight = 0

        self.neightbors_ = []
        self.messages_ = []


        self.wear = playerWear()
        self.bank = playerBank()

        self.inventory = Inventory()
        self.inventory.addGold(startingGold)

        self.inShop = False
        self.inBank = False

        self.inBuilding = False

        self.inTrade = False
        self.tradeCandidates = []
        self.tradeOffer = ""
        self.tradeOffered = ""

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

    def getAttack(self):


        return self.attack + self.wear.getAttackBonus()
    def getCounterAttack(self):
        return self.counterAttack

    def getNeighbors(self):
        #other players that are in the vicinity of the player
        #used for messaging
        return self.neightbors_


    def getGameState(self):
        result = {}
        result["worldx"] = self.worldX_
        result["worldy"] = self.worldY_
        result["x"] = self.x_
        result["y"] = self.y_

        result["gold"] = self.inventory.getGold()
        result["bankgold"] = self.bank.getBalance()

        result["hp"] = self.hp
        result["onland"] = self.onLand
        result["inventory"] = self.inventory.getPhysicalItems()

        return result


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
    def getHp(self):
        return self.hp
    def setHp(self, hp):
        if (hp <= self.maxHp and hp >= 0):
            self.hp = hp
        else:
            self.hp = self.maxHp

    def fight(self):
        self.inFight = self.fightTime
    def fighting(self):
        if (self.inFight == 0):
            return False
        else:
            return True

    def hit(self, amount):
        if (not self.onLand):
            defBonus = self.wear.getShipDefBonus()
            if (defBonus > 0):
                amount = amount - int(amount * defBonus)
        else: #on land
            defBonus = self.wear.getArmorBonus()
            if (defBonus > 0):
                amount = amount - int(amount * defBonus)

        self.hp -= amount
        return amount

    def alive(self):
        if (self.hp <= 0):
            return False
        else:
            return True
    def resetHp(self):
        self.hp = self.maxHp
    def respawn(self):
        self.x_ = self.originX
        self.y_ = self.originY
        self.worldX_ = self.originWX
        self.worldY_ = self.originWY
        self.onLand = True

        #reset hp and empty inventory
        self.hp = self.maxHp
        self.inventory = Inventory()
    def setOnLand(self, val):
        self.onLand = val
    def isOnLand(self):
        return self.onLand
    def regenActions(self):
        if (self.acted != 0):
            self.acted -= 1
        if (self.inFight != 0):
            self.inFight -= 1

    def getInv(self):
        return self.inventory
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

    def goToTrade(self):
        self.inTrade = True
    def isInTrade(self):
        return self.inTrade
    def leaveTrade(self):
        self.inTrade = False

    def addTradeCandidate(self, name):
        self.tradeCandidates.append(name)
    def resetTradeCandidates(self):
        self.tradeCandidates = []
        self.tradeOffer = ""
        self.tradeOffered = ""

    def getTradeCandidates(self):
        return self.tradeCandidates

    def getTradeOffered(self):
        return self.tradeOffered
    def offerTrade(self, name):
        self.tradeOffered = name

    def addTradeOffer(self, name):
        self.tradeOffer = name
    def getTradeOffer(self):
        return self.tradeOffer
    def declineTradeOffer(self):
        self.tradeOffer = ""


    def isInBuilding(self):
        return self.inBuilding
    def goToBuilding(self):
        self.inBuilding = True
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

    def wearItem(self, item):
        if (not items.itemWearable(item)):
            return
        else:

            self.wear.changeItem(items.getWearType(item), item, items.getWearBonus(item))


    def canMove(self, tile):
        if (self.onLand and tile == self.ground):
            return True
        elif (not self.onLand and tile == self.sea):
            return True
        else:
            return False
        #check if player can move to the position

    def moveLeft(self, square, hx = -1, hy = -1):

        if (self.moved_ == True or self.inFight != 0):
            return

        newX = self.x_ -1
        if (newX < 0):
            newX = self.squareSize_ -1
            self.worldX_ -= 1
            if (self.worldX_ <= -self.worldSize +1):
                self.worldX_ = self.worldSize -1

        elif (self.canMove(square[self.y_][newX]) == False and not(newX == hx and self.y_ == hy)):
            return
        self.x_ = newX
        self.moved_ = True
        self.inShop = False
        self.inBank = False

        self.inBuilding = False
        self.inTrade = False
        self.resetTradeCandidates()

    def moveRight(self, square, hx = -1, hy = -1):

        if (self.moved_ == True or self.inFight != 0):
            return

        newX = self.x_ +1
        if (newX >= self.squareSize_):
            newX = 0
            self.worldX_ += 1
            if (self.worldX_ >= self.worldSize -1):
                self.worldX_ = -self.worldSize +1

        elif (self.canMove(square[self.y_][newX]) == False and not(newX == hx and self.y_ == hy)):
            return
        self.x_ = newX
        self.moved_ = True
        self.inShop = False
        self.inBank = False

        self.inBuilding = False
        self.inTrade = False
        self.resetTradeCandidates()


    def moveDown(self, square, hx = -1, hy = -1):
        if (self.moved_ == True or self.inFight != 0):
            return
        newY = self.y_ + 1
        if (newY >= self.squareSize_):
            newY = 0
            self.worldY_ += 1

            if (self.worldY_ >= self.worldSize -1):
                self.worldY_ = -self.worldSize +1

        elif (self.canMove(square[newY][self.x_]) == False and not(self.x_ == hx and newY == hy)):
            return
        self.y_ = newY
        self.moved_ = True
        self.inShop = False
        self.inBank = False

        self.inBuilding = False
        self.inTrade = False
        self.resetTradeCandidates()


    def moveUp(self, square, hx = -1, hy = -1):
        if (self.moved_ == True or self.inFight != 0):
            return

        newY = self.y_ - 1
        if (newY < 0):
            newY = self.squareSize_ -1
            self.worldY_ -= 1

            if (self.worldY_ <= -self.worldSize +1):
                self.worldY_ = self.worldSize -1

        elif (self.canMove(square[newY][self.x_]) == False and not(self.x_ == hx and newY == hy)):
            return
        self.y_ = newY
        self.moved_ = True
        self.inShop = False
        self.inBank = False

        self.inBuilding = False
        self.inTrade = False
        self.resetTradeCandidates()


    def printLocation(self, allPlayers, npcs, monsters, cache, trees, shops, banks, hospitals, harbors):
        #returns the gamemap the player sees as a 2d array
        #populates the map with all different gameobjects on their right places

        #areatoprint is the maplayer, objectlayer is for objects such as resources and players
        areaToPrint = [[self.sea for y in range(self.squareSize_ * 3)] for x in range(self.squareSize_ * 3)]
        objectLayer = [[self.empty for y in range(self.squareSize_ * 3)] for x in range(self.squareSize_ * 3)]

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

            for y in range(self.squareSize_):
                for x in range(self.squareSize_):
                    areaToPrint[(thirdHeight+1) * self.squareSize_ + y][x] = left[y][x]
                    #print(left[y][x], end="")
                for x in range(self.squareSize_):
                    if (x == self.x_ and y == self.y_ and thirdHeight == 0):
                        areaToPrint[(thirdHeight+1)  * self.squareSize_ + y][x + self.squareSize_] = zero[y][x]#"@"
                    else:
                        areaToPrint[(thirdHeight+1)  * self.squareSize_ + y][x + self.squareSize_] = zero[y][x]
                for x in range(self.squareSize_):
                    areaToPrint[(thirdHeight+1) * self.squareSize_ + y][x + self.squareSize_ * 2] = right[y][x]



        #trees
        for y in range(-1, 2):
            for x in range(-1, 2):
                if ((self.worldX_ + x, self.worldY_ + y) in trees):
                    for tree in trees[(self.worldX_ + x, self.worldY_ + y)]:
                        objectLayer[y * self.squareSize_ + self.squareSize_ + tree.getY()][x * self.squareSize_ + self.squareSize_ + tree.getX()] = tree.getCharacter()

        #shops
        for y in range(-1, 2):
            for x in range(-1, 2):
                if ((self.worldX_ + x, self.worldY_ + y) in shops):
                    for shop in shops[(self.worldX_ + x, self.worldY_ + y)]:
                        objectLayer[y * self.squareSize_ + self.squareSize_ + shop.getY()][x * self.squareSize_ + self.squareSize_ + shop.getX()] = shop.getCharacter()

        #banks
        for y in range(-1, 2):
            for x in range(-1, 2):
                if ((self.worldX_ + x, self.worldY_ + y) in banks):
                    for bank in banks[(self.worldX_ + x, self.worldY_ + y)]:
                        objectLayer[y * self.squareSize_ + self.squareSize_ + bank.getY()][x * self.squareSize_ + self.squareSize_ + bank.getX()] = bank.getCharacter()

        #hospitals
        for y in range(-1, 2):
            for x in range(-1, 2):
                if ((self.worldX_ + x, self.worldY_ + y) in hospitals):
                    for hosp in hospitals[(self.worldX_ + x, self.worldY_ + y)]:
                        objectLayer[y * self.squareSize_ + self.squareSize_ + hosp.getY()][x * self.squareSize_ + self.squareSize_ + hosp.getX()] = hosp.getCharacter()

        #harbors
        for y in range(-1, 2):
            for x in range(-1, 2):
                if ((self.worldX_ + x, self.worldY_ + y) in harbors):
                    for harbor in harbors[(self.worldX_ + x, self.worldY_ + y)]:
                        objectLayer[y * self.squareSize_ + self.squareSize_ + harbor.getY()][x * self.squareSize_ + self.squareSize_ + harbor.getX()] = harbor.getCharacter()

        #npcs
        for y in range(-1, 2):
            for x in range(-1, 2):
                if ((self.worldX_ + x, self.worldY_ + y) in npcs):
                    for npc in npcs[(self.worldX_ + x, self.worldY_ + y)]:
                        objectLayer[y * self.squareSize_ + self.squareSize_ + npc.getY()][x * self.squareSize_ + self.squareSize_ + npc.getX()] = npc.getCharacter()


        #monsters
        for y in range(-1, 2):
            for x in range(-1, 2):
                if ((self.worldX_ + x, self.worldY_ + y) in monsters):
                    for monster in monsters[(self.worldX_ + x, self.worldY_ + y)]:
                        objectLayer[y * self.squareSize_ + self.squareSize_ + monster.getY()][x * self.squareSize_ + self.squareSize_ + monster.getX()] = monster.getCharacter()


        #draw other players
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
                        objectLayer[yloc*self.squareSize_ + y][xloc*self.squareSize_ + x] = self.others
                        self.neightbors_.append(value.getName())


        #draw the player itself
        worldx = self.worldX_
        worldy = self.worldY_
        x = self.x_
        y = self.y_
        xloc = worldx - self.worldX_ + 1 #self.worldX_ - worldx + 1
        yloc = self.worldY_ - worldy + 1
        objectLayer[yloc*self.squareSize_ + y][xloc*self.squareSize_ + x] = self.character

        return areaToPrint, objectLayer
