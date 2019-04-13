

from time import sleep
import copy

from engine.npc import *
from engine.gameObjects import *
from engine.inventory import *
from engine.player import *

import datetime
import random
import configparser


"""
TODO:



-change trees to resources, add mining similar to npc types
    -info messages are read from config
    -drops also
    -only 1 type per island, decide procedurally


-pvp
-ships. if none owned, the default is a raft, but better can be bought instead
    -bought from ships sales locations, have to sell previous ship before buying
    -adds hp when seaborne
-shipyards, where one could setup their ship with items (cannons, plating etc)
    -these are bought from a shop to ones inventory and transported to an island
     with a shipyard

-limit worldsize, for ex 100 by 100 for a start?
    -make "round"?








### secondary todo:

#make browser use the same 0.2 second rules as the server, even though mostly pointless

#make trees respawn after a time?, now respawn when area is left
#faction areas?, rnd, generate enemy levels based on faction area, 1 to nullsec, pvp?

#pringtgamestate shared for multiple worker threads as it's the slowest function to run by far



"""


class Game:
    """Game runner object, handles players and passes their actions to the corresponding objects"""

    def __init__(self):

        self.config = configparser.ConfigParser()
        self.config.read("./engine/config.cfg")
        self.ground = self.config["terrain"]["ground"]
        self.sea = self.config["terrain"]["sea"]

        self.allPlayers_ = {}  # use as playername: Player()
        self.squareSize_ = int(self.config["terrain"]["squareSize"])
        self.seed = 1254122

        self.squareCache = {}  # use as [(x, y): 2Dlist of tiles]


        self.trees = {}  # use as [(x, y): list of trees
        # use as [(x, y): list of shops, only one per island atm
        self.shops = {}
        # use as [(x, y): list of banks, only one per island atm
        self.banks = {}
        # use as [(x, y): list of harbors, only one per island
        self.harbors = {}
        self.hospitals = {}
        self.Npcs = {}
        self.monsters = {}

    def getSize(self):
        return 3 * self.squareSize_

    def addPlayer(self, playerName):
        player = Player(playerName, 0, 0, 10, 10, self.seed, self.squareSize_)
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
            hx = self.harbors[(player.getWorldX(),
                               player.getWorldY())][0].getX()
            hy = self.harbors[(player.getWorldX(),
                               player.getWorldY())][0].getY()

        if ((player.getWorldX(), player.getWorldY()) in self.squareCache):
            player.moveLeft(
                self.squareCache[(player.getWorldX(), player.getWorldY())], hx, hy)

    def movePlayerRight(self, playerName):
        player = self.allPlayers_[playerName]
        hx = -1
        hy = -1
        if ((player.getWorldX(), player.getWorldY()) in self.harbors):
            hx = self.harbors[(player.getWorldX(),
                               player.getWorldY())][0].getX()
            hy = self.harbors[(player.getWorldX(),
                               player.getWorldY())][0].getY()

        if ((player.getWorldX(), player.getWorldY()) in self.squareCache):
            player.moveRight(
                self.squareCache[(player.getWorldX(), player.getWorldY())], hx, hy)

    def movePlayerUp(self, playerName):
        player = self.allPlayers_[playerName]
        hx = -1
        hy = -1
        if ((player.getWorldX(), player.getWorldY()) in self.harbors):
            hx = self.harbors[(player.getWorldX(),
                               player.getWorldY())][0].getX()
            hy = self.harbors[(player.getWorldX(),
                               player.getWorldY())][0].getY()

        if ((player.getWorldX(), player.getWorldY()) in self.squareCache):
            player.moveUp(
                self.squareCache[(player.getWorldX(), player.getWorldY())], hx, hy)

    def movePlayerDown(self, playerName):
        player = self.allPlayers_[playerName]
        hx = -1
        hy = -1
        if ((player.getWorldX(), player.getWorldY()) in self.harbors):
            hx = self.harbors[(player.getWorldX(),
                               player.getWorldY())][0].getX()
            hy = self.harbors[(player.getWorldX(),
                               player.getWorldY())][0].getY()

        if ((player.getWorldX(), player.getWorldY()) in self.squareCache):
            player.moveDown(
                self.squareCache[(player.getWorldX(), player.getWorldY())], hx, hy)

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
                        newTree = Resource(2, x, y, square[0], square[1], self.seed)
                        if (square in self.trees):
                            self.trees[square].append(newTree)
                        else:
                            newList = [newTree]
                            self.trees[square] = newList

    def checkSurroundingTileCount(self, tileSet, tileType, x, y):
        # check number of tiles of tileType near x,y in tileset
        value = 0
        if (x - 1 >= 0):
            if (tileSet[y][x - 1] == tileType):
                value += 1
        if (x + 1 < self.squareSize_):
            if (tileSet[y][x + 1] == tileType):
                value += 1
        if (y - 1 >= 0):
            if (tileSet[y - 1][x] == tileType):
                value += 1
        if (y + 1 < self.squareSize_):
            if (tileSet[y + 1][x] == tileType):
                value += 1
        return value

    """next functions generate different gameobjects"""

    def generateShop(self, square):
        baseLayer = self.squareCache[square]
        groundTiles = []
        for y in range(len(baseLayer)):
            for x in range(len(baseLayer[y])):
                if (baseLayer[y][x] == self.ground):
                    if (self.checkSurroundingTileCount(baseLayer, self.ground, x, y) >= 3):
                        groundTiles.append((x, y))

        if (len(groundTiles) == 0):  # no available spots
            return

        chunkSeed = self.seed
        if (square[0] != 0):
            chunkSeed = chunkSeed * square[0] + chunkSeed // square[0]
        if (square[1] != 0):
            chunkSeed = chunkSeed * square[1] + chunkSeed // square[1]

        tileNumber = chunkSeed % 170767 % len(groundTiles)

        self.shops[square] = [
            Shop(groundTiles[tileNumber][0], groundTiles[tileNumber][1])]

    def generateBank(self, square):
        baseLayer = self.squareCache[square]
        groundTiles = []
        for y in range(len(baseLayer)):
            for x in range(len(baseLayer[y])):
                if (baseLayer[y][x] == self.ground):
                    if (self.checkSurroundingTileCount(baseLayer, self.ground, x, y) >= 3):
                        groundTiles.append((x, y))

        if (len(groundTiles) == 0):  # no available spots
            return

        chunkSeed = self.seed
        if (square[0] != 0):
            chunkSeed = chunkSeed * square[0] + chunkSeed // square[0]
        if (square[1] != 0):
            chunkSeed = chunkSeed * square[1] + chunkSeed // square[1]

        tileNumber = chunkSeed % 170767 % len(groundTiles)

        self.banks[square] = [
            GameBank(groundTiles[tileNumber][0], groundTiles[tileNumber][1])]


    def generateHospital(self, square):
        baseLayer = self.squareCache[square]
        groundTiles = []
        for y in range(len(baseLayer)):
            for x in range(len(baseLayer[y])):
                if (baseLayer[y][x] == self.ground):
                    if (self.checkSurroundingTileCount(baseLayer, self.ground, x, y) >= 3):
                        groundTiles.append((x, y))

        if (len(groundTiles) == 0):  # no available spots
            return

        chunkSeed = self.seed
        if (square[0] != 0):
            chunkSeed = chunkSeed * square[0] + chunkSeed // square[0]
        if (square[1] != 0):
            chunkSeed = chunkSeed * square[1] + chunkSeed // square[1]

        tileNumber = chunkSeed % 170767 % len(groundTiles)

        self.hospitals[square] = [
            Hospital(groundTiles[tileNumber][0], groundTiles[tileNumber][1])]



    def generateHarbor(self, square):
        baseLayer = self.squareCache[square]
        groundTiles = []
        for y in range(len(baseLayer)):
            for x in range(len(baseLayer[y])):
                if (baseLayer[y][x] == self.ground):
                    if (self.checkSurroundingTileCount(baseLayer, self.sea, x, y) >= 2):
                        groundTiles.append((x, y))

        if (len(groundTiles) == 0):  # no available spots
            return

        chunkSeed = self.seed
        if (square[0] != 0):
            chunkSeed = chunkSeed * square[0] + chunkSeed // square[0]
        if (square[1] != 0):
            chunkSeed = chunkSeed * square[1] + chunkSeed // square[1]

        tileNumber = chunkSeed % 170773 % len(groundTiles)
        self.harbors[square] = [
            Harbor(groundTiles[tileNumber][0], groundTiles[tileNumber][1])]

    def generateNpc(self, square):
        possibleLocations = []
        baseLayer = self.squareCache[square]

        for i in range(len(baseLayer)):
            for j in range(len(baseLayer[i])):
                if (baseLayer[i][j] == self.ground):
                    possibleLocations.append((j, i))
        """spawn npc to pseudorandom location"""
        xseed = self.seed + square[0] % 1000001
        yseed = self.seed - square[1] % 1000003
        npcSeed = (xseed + yseed) % len(possibleLocations)

        # random.choice(possibleLocations)
        location = possibleLocations[npcSeed]
        self.Npcs[square] = [
            Npc("asd", square[0], square[1], location[0], location[1], self.squareSize_)]

    def generateMonster(self, square):
        possibleLocations = []
        baseLayer = self.squareCache[square]

        for i in range(len(baseLayer)):
            for j in range(len(baseLayer[i])):
                possibleLocations.append((j, i))
        """spawn npc to pseudorandom location"""
        xseed = self.seed + square[0] % 1000001
        yseed = self.seed - square[1] % 1000003
        npcSeed = (xseed + yseed) % len(possibleLocations)

        # random.choice(possibleLocations)
        location = possibleLocations[npcSeed]
        self.monsters[square] = [
            Monster("asd", square[0], square[1], location[0], location[1], self.squareSize_)]

    def updateSquareCache(self):
        """update cache of gamesquares, and remove and create gameobjects for new/old squares
        This only removes squares, they are generated elsewhere as players access them"""


        #respawn dead players
        for player in self.allPlayers_.values():
            if (not player.alive()):
                player.addMessage("Game", "You died an lost all your items")
                player.respawn()



        # remove unhabitated squares
        locations = []  # list of worldcoord pairs
        for player in self.allPlayers_.values():
            x = player.getWorldX()
            y = player.getWorldY()
            if ((x, y) not in locations):
                locations.append((x, y))
            if ((x - 1, y) not in locations):
                locations.append((x - 1, y))
            if ((x + 1, y) not in locations):
                locations.append((x + 1, y))
            if ((x, y - 1) not in locations):
                locations.append((x, y - 1))
            if ((x - 1, y - 1) not in locations):
                locations.append((x - 1, y - 1))
            if ((x + 1, y - 1) not in locations):
                locations.append((x + 1, y - 1))
            if ((x, y + 1) not in locations):
                locations.append((x, y + 1))
            if ((x - 1, y + 1) not in locations):
                locations.append((x - 1, y + 1))
            if ((x + 1, y + 1) not in locations):
                locations.append((x + 1, y + 1))
        newCache = {}
        for square in self.squareCache:
            if (square in locations):
                newCache[square] = self.squareCache[square]
        self.squareCache = newCache

        # take old gameobjects, and get rid of the ones that are no longer visible in the game area
        newTrees = {}
        for trees in self.trees:
            if (trees in locations):
                newTrees[trees] = self.trees[trees]
        self.trees = newTrees

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

        newHospitals = {}
        for hosps in self.hospitals:
            if (hosps in locations):
                newHospitals[hosps] = self.hospitals[hosps]
        self.hospitals = newHospitals

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

        newMonsters = {}
        for monster in self.monsters:
            if (monster in locations):
                newMonsters[monster] = self.monsters[monster]
        self.monsters = newMonsters

        # generate new gameobjects on new squarecache squares as they are blank before
        for square in self.squareCache:
            if (square not in self.trees):
                if (any(self.ground in sublist for sublist in self.squareCache[square])):
                    self.generateTrees(square)

        """
        for square in self.squareCache:
            if (square not in self.shops):
                if (any(self.ground in sublist for sublist in self.squareCache[square])):
                    self.generateShop(square)

        for square in self.squareCache:
            if (square not in self.banks):
                if (any(self.ground in sublist for sublist in self.squareCache[square])):
                    self.generateBank(square)
        """

        for square in self.squareCache:
            if (square not in self.banks and square not in self.shops):
                if (any(self.ground in sublist for sublist in self.squareCache[square])):
                    xseed = self.seed + square[0] % 1000001
                    yseed = self.seed - square[1] % 1000003
                    objectSeed = (xseed + yseed) % 3
                    if (objectSeed == 0):
                        self.generateBank(square)
                    elif (objectSeed == 1):
                        self.generateShop(square)
                    else:
                        self.generateHospital(square)


        for square in self.squareCache:
            if (square not in self.harbors):
                if (any(self.ground in sublist for sublist in self.squareCache[square])):
                    self.generateHarbor(square)

        for square in self.squareCache:
            if (square not in self.Npcs):
                if (any(self.ground in sublist for sublist in self.squareCache[square])):
                    self.generateNpc(square)

        for square in self.squareCache:
            if (square not in self.monsters):
                if (not any(self.ground in sublist for sublist in self.squareCache[square])):
                    xseed = self.seed + square[0] % 1000001
                    yseed = self.seed - square[1] % 1000003
                    objectSeed = (xseed + yseed) % 2
                    if (objectSeed == 0):
                        self.generateMonster(square)

        # allow npcs and monsters to move, then disable movement for those that are
        # ontop of players or next to them
        for npcs in self.Npcs.values():
            for npc in npcs:
                npc.setMovable()

        for player in self.allPlayers_.values():
            worldX = player.getWorldX()
            worldY = player.getWorldY()
            if ((worldX, worldY) in self.Npcs):
                x = player.getX()
                y = player.getY()
                for npc in self.Npcs[(worldX, worldY)]:
                    npc.disableMovingIfNearby(x, y)

        for monsters in self.monsters.values():
            for monster in monsters:
                monster.setMovable()

        for player in self.allPlayers_.values():
            worldX = player.getWorldX()
            worldY = player.getWorldY()
            if ((worldX, worldY) in self.monsters):
                x = player.getX()
                y = player.getY()
                for monster in self.monsters[(worldX, worldY)]:
                    monster.disableMovingIfNearby(x, y)

        # call move for all npcs and monsters, they know if they can and will
        for i in (self.Npcs):
            if (i in self.squareCache):
                for npc in self.Npcs[i]:
                    npc.move(self.squareCache[i])

        for i in (self.monsters):
            if (i in self.squareCache):
                for monster in self.monsters[i]:
                    monster.move(self.squareCache[i])

    def printGameState(self, playerName):  # again bad name, just returns stuff
        # get a gameview of the specified player
        return self.allPlayers_[playerName].printLocation(self.allPlayers_, self.Npcs, self.monsters, self.squareCache, self.trees, self.shops, self.banks, self.hospitals, self.harbors)

    def getActionStatus(self, playerName):
        # get the state of info that needs to be shown to the player
        # this means besides the chat and map
        player = self.allPlayers_[playerName]
        if (player.isInBank()):
            return "bank"
        if (player.isInShop()):
            return "shop"
        else:
            return "none"

    def getPlayerHp(self, playerName):
        return self.allPlayers_[playerName].getHp()

    def getItems(self, playerName):
        # return the entire inventory of the player
        return self.allPlayers_[playerName].getInventory()

    def getBankBalance(self, playerName):
        # return the entire bank balance of the plaeyr
        return self.allPlayers_[playerName].getBankBalance()

    def getShopSell(self, playerName):
        # if player is in a shop, get all the items available in the shop and
        # return a dict (item:price), if not in a shop, return false
        player = self.allPlayers_[playerName]
        if (player.isInShop()):
            # return items player has and their values
            items = player.getPhysicalInventory().keys()  # remove physical for thesting
            x = player.getWorldX()
            y = player.getWorldY()

            shop = self.shops[(x, y)][0]

            itemsAndValues = {}
            for item in items:
                itemsAndValues[item] = shop.getSellPrice(item)
            return itemsAndValues
        return False

    def getShopBuy(self, playerName):
        # if player is in a shop, return dict of items and sellprices of the
        # players inventory
        player = self.allPlayers_[playerName]
        if (player.isInShop()):
            x = player.getWorldX()
            y = player.getWorldY()

            shop = self.shops[(x, y)][0]
            catalog = copy.deepcopy(shop.getBuyPrices())
            return catalog
        return False

    def doAction(self, playerName):
        # check if player is able to do any actions in the game and do them
        # only 1 per call
        player = self.allPlayers_[playerName]

        if (player.canAct() == False):
            return

        # get players square, so we can check if any of the objects are nearby
        x = player.getWorldX()
        y = player.getWorldY()

        # handle harbors
        if ((x, y) in self.harbors):
            for harbor in self.harbors[(x, y)]:
                if (harbor.getX() == player.getX() and harbor.getY() == player.getY()):
                    player.act()
                    player.useHarbor()
                    player.addMessage("Game", "You use the harbor.")
                    return

        # handle hospitals
        if ((x, y) in self.hospitals):
            for hospital in self.hospitals[(x, y)]:
                if (hospital.getX() == player.getX() and hospital.getY() == player.getY()):
                    if (not player.isInBuilding()):
                        player.act()
                        player.goToBuilding()
                        player.resetHp()
                        player.addMessage("Game", "You heal yourself to " + str(player.getHp()))
                    return

        # handle banks
        if ((x, y) in self.banks):
            for bank in self.banks[(x, y)]:
                if (bank.getX() == player.getX() and bank.getY() == player.getY()):
                    if (not player.isInBuilding()):
                        player.act()
                        player.goToBank()
                        player.goToBuilding()

                        player.addMessage("Game", "You enter a bank.")
                    return

        # handle shops
        if ((x, y) in self.shops):
            for shop in self.shops[(x, y)]:
                if (shop.getX() == player.getX() and shop.getY() == player.getY()):
                    if (not player.isInBuilding()):
                        player.act()
                        player.goToShop()
                        player.goToBuilding()

                        player.addMessage("Game", "You enter a shop.")
                    return

        #handle npcs
        if ((x, y) in self.Npcs):
            for npc in self.Npcs[(x, y)]:
                if (npc.getX() == player.getX() and npc.getY() == player.getY()):
                    player.act()

                    player.addMessage(npc.getType(), npc.getLine())
                    return


        # handle monsters
        if ((x, y) in self.monsters):
            canExit = False
            for monster in self.monsters[(x, y)]:
                locX = player.getX()
                locY = player.getY()
                if (abs(monster.getX() - player.getX()) <= 1 and abs(monster.getY() - player.getY()) <= 1):
                    player.act()
                    monster.hit(player.getAttack())

                    """ MAKE PLAYER DIE HERE?
                    """

                    if (not monster.alive()):
                        player.addMessage(
                            "Game", "You hit the " + monster.getType() + " and it "+ monster.getDeathNote() + ".")
                        if (monster.dropType() == ""):
                            pass
                        elif (monster.dropType() == "gold"):
                            player.addGold(monster.dropAmount())
                        else:
                            for i in range(monster.dropAmount()):
                                player.addItemToInv(monster.dropType())
                        self.monsters[(x, y)].remove(monster)
                    else:
                        player.hit(monster.getAttack())

                        player.addMessage(
                            "Game", "You hit a " + monster.getType() + " and did " + str(player.getAttack()) + " damage.")

                        player.addMessage(
                            "Game", "The " + monster.getType() + " " + monster.getAttackType() +" you and did " + str(monster.getAttack()) + " damage.")

                    canExit = True
                    break
            if (canExit):
                return

        # handle trees
        if ((x, y) in self.trees):
            for tree in self.trees[(x, y)]:
                if (tree.getX() == player.getX() and tree.getY() == player.getY()):
                    player.act()
                    tree.hit()
                    if (not tree.alive()):
                        player.addMessage(
                            "Game", "You " + tree.getDeathNote() + ".")
                        for i in range(tree.dropAmount()):
                            player.addItemToInv(tree.dropType())

                        self.trees[(x, y)].remove(tree)
                    else:
                        player.addMessage("Game", "You " + tree.getHitNote() + ".")
                    return

    def changeBankBalance(self, playerName, amount):
        # add or remove money from the players bank, if possible
        player = self.allPlayers_[playerName]
        if (player.isInBank()):
            x = player.getWorldX()
            y = player.getWorldY()
            bank = self.banks[(x, y)][0]
            if (bank.getX() == player.getX() and bank.getY() == player.getY()):
                if (amount % 1 != 0):  # check if whole number
                    return

                if (amount > 0):
                    success = player.changeBankBalance(amount)
                    if (success):
                        player.addMessage(
                            "Game", "You deposited " + str(amount) + " gold.")
                elif (amount < 0):
                    success = player.changeBankBalance(amount)
                    if (success):
                        player.addMessage(
                            "Game", "You withdrew " + str(abs(amount)) + " gold.")
                    else:
                        player.addMessage("Game", "You are too broke.")

    def buyItem(self, playerName, item):
        # buy a item for the player and reduce the amount of money it costs from them
        # won't do anything if the player is not in a shop or the shop doesn't carry teh item
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
                        player.addGold(-1 * value)
                        player.addItemToInv(item)

                        player.addMessage(
                            "Game", "You bought a " + item + " for " + str(value) + " gold.")
                    else:
                        player.addMessage("Game", "You are too broke.")

    def sellItem(self, playerName, item):
        # sell an item to a shop that the player is standing on, wont do anything
        # if the player doesnt have the item or is not in a shop
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
                        player.addMessage(
                            "Game", "You sold a " + item + " for " + str(value) + " gold.")


"""
#testing purposes only
game = Game()

game.addPlayer("asd")
game.addPlayer("asd2")
game.moveRight("asd")
game.printGameState("asd")
"""
