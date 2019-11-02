import configparser
import json
from engine.pseudo import *
import time

class GameObject:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.character = "0"

    def getCharacter(self):
        return self.character

    def getX(self):
        return self.x

    def getY(self):
        return self.y


class Resource(GameObject):
    def __init__(self, hp, x, y, worldx, worldy, seed):

        self.config = configparser.ConfigParser()
        
        self.config.read("./engine/config.cfg")

        possibleTypes = json.loads(self.config["resources"]["types"])


        choiceNumber = pseudo.inRange(len(possibleTypes), worldx, worldy, seed)

        self.type = possibleTypes[choiceNumber]


        self.character = self.config[self.type]["character"]
        self.hp = int(self.config[self.type]["hp"])

        self.drops = self.config[self.type]["itemDrop"]
        self.dropValue = int(self.config[self.type]["dropAmount"])

        self.deathNote = self.config[self.type]["deathNote"]
        self.hitNote = self.config[self.type]["hitNote"]


        self.x = x
        self.y = y

        """Tästä jatkoa, lisää actioniin testi onko hengissä, piirtoon samoin
        päivitystriggeriin check onko kulunut tarpeeksi aikaa, ja jos on niin resettaa hp
        Lue aika configista
        """
        self.deathTime = 0
        self.respawnDelay = int(self.config[self.type]["respawnDelay"])
        self.originalHp = self.hp

    def hit(self):
        if (self.hp > 0):
            self.hp -= 1
        if (self.hp <= 0):
            self.deathTime = time.time()

    def alive(self):
        if (self.hp > 0):
            return True
        else:
            return False
    def respawn(self):
        self.hp = self.originalHp
    def canRespawn(self):
        if (time.time() - self.deathTime >= self.respawnDelay):
            return True
        else:
            return False

    def getType(self):
        return self.type

    def dropType(self):
        return self.drops
    def dropAmount(self):
        return self.dropValue
    def getDeathNote(self):
        return self.deathNote
    def getHitNote(self):
        return self.hitNote




class Shop(GameObject):
    def __init__(self, x, y, worldx, worldy, seed):
        self.config = configparser.ConfigParser()
        self.config.read("./engine/config.cfg")




        possibleTypes = json.loads(self.config["shopTypes"]["types"])
        choiceList = []
        for i in possibleTypes:
            weight = int(self.config[i]["probabilityFactor"])
            for j in range(weight):
                choiceList.append(i)

        self.type = choiceList[pseudo.getNumberInRangeByLocation(0, len(choiceList), worldx, worldy, seed)]

        self.character = self.config[self.type]["character"]
        self.shopItems = json.loads(self.config[self.type]["items"])
        self.allItems = json.loads(self.config["allItems"]["types"])

        self.sellValues = {}  # use as item:value
        self.buyValues = {}


        for i in self.shopItems:
            self.buyValues[i] = int(self.config[i]["buyPrice"])
        for i in self.allItems:
            self.sellValues[i] = int(self.config[i]["sellPrice"])

        #self.sellValues["log"] = int(self.config["log"]["sellPrice"])
        #self.buyValues["log"] = int(self.config["log"]["buyPrice"])

        self.stock = {}

        self.x = x
        self.y = y

    def getType(self):
        return self.type

    def getBuyPrices(self):
        return self.buyValues

    def getBuyPrice(self, item):
        if (item in self.buyValues):
            return self.buyValues[item]
        else:
            return False

    def getSellPrice(self, item):
        if (item in self.sellValues):
            return self.sellValues[item]
        else:
            return False

    def buyItem(self, item):
        if (item in self.stock):
            self.stock[item] -= 1
        else:
            self.stock[item] = 0
        return self.buyValues[item]

    def sellItem(self, item):  # returns the price paid
        if (item in self.stock):
            self.stock[item] += 1
        else:
            self.stock[item] = 1
        return self.sellValues[item]

    def getStock(self, item):
        if (item in self.stock):
            return self.stock[item]
        else:
            return 0


class GameBank(GameObject):
    def __init__(self, x, y):
        self.config = configparser.ConfigParser()
        self.config.read("./engine/config.cfg")
        self.character = self.config["bank"]["character"]
        self.x = x
        self.y = y


class Harbor(GameObject):
    def __init__(self, x, y):
        self.config = configparser.ConfigParser()
        self.config.read("./engine/config.cfg")
        self.character = self.config["harbor"]["character"]
        self.x = x
        self.y = y


class Hospital(GameObject):
    def __init__(self, x, y):
        self.config = configparser.ConfigParser()
        self.config.read("./engine/config.cfg")
        self.character = self.config["hospital"]["character"]
        self.x = x
        self.y = y

class DungeonEntrance(GameObject):
    def __init__(self, x, y):
        self.config = configparser.ConfigParser()
        self.config.read("./engine/config.cfg")
        self.character = self.config["dungeonEntrance"]["character"]
        self.x = x
        self.y = y
        self.type = self.config["dungeonEntrance"]["dungeonType"]
    def getId(self):
        return "x:"+str(self.x)+"y:"+str(self.y)+"dungeon"
    def getType(self):
        return self.type