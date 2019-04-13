import configparser
import json
import random

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

        xseed = seed + worldx % 1000001
        yseed = seed - worldy % 1000003
        objectSeed = (xseed + yseed) % len(possibleTypes)
        self.type = possibleTypes[objectSeed]


        self.character = self.config[self.type]["character"]
        self.hp = int(self.config[self.type]["hp"])

        self.drops = self.config[self.type]["itemDrop"]
        self.dropValue = int(self.config[self.type]["dropAmount"])

        self.deathNote = self.config[self.type]["deathNote"]
        self.hitNote = self.config[self.type]["hitNote"]


        self.x = x
        self.y = y

    def hit(self):
        if (self.hp > 0):
            self.hp -= 1

    def alive(self):
        if (self.hp > 0):
            return True
        else:
            return False

    def dropType(self):
        return self.drops
    def dropAmount(self):
        return self.dropValue
    def getDeathNote(self):
        return self.deathNote
    def getHitNote(self):
        return self.hitNote




class Shop(GameObject):
    def __init__(self, x, y):
        self.config = configparser.ConfigParser()
        self.config.read("./engine/config.cfg")
        self.character = self.config["shop"]["character"]


        self.shopItems = json.loads(self.config["shop"]["items"])


        self.sellValues = {}  # use as item:value
        self.buyValues = {}


        for i in self.shopItems:
            self.sellValues[i] = int(self.config[i]["sellPrice"])
            self.buyValues[i] = int(self.config[i]["buyPrice"])


        #self.sellValues["log"] = int(self.config["log"]["sellPrice"])
        #self.buyValues["log"] = int(self.config["log"]["buyPrice"])

        self.stock = {}

        self.x = x
        self.y = y

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
