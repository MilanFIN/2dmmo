import configparser


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


class Tree(GameObject):
    def __init__(self, hp, x, y):

        self.config = configparser.ConfigParser()
        self.config.read("./engine/config.cfg")
        self.character = self.config["tree"]["character"]
        self.hp = int(self.config["tree"]["hp"])

        self.drops = self.config["tree"]["itemDrop"]
        self.dropValue = int(self.config["tree"]["dropAmount"])

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


class Shop(GameObject):
    def __init__(self, x, y):
        self.config = configparser.ConfigParser()
        self.config.read("./engine/config.cfg")
        self.character = self.config["shop"]["character"]

        self.sellValues = {}  # use as item:value
        self.buyValues = {}

        self.sellValues["log"] = int(self.config["log"]["sellPrice"])
        self.buyValues["log"] = int(self.config["log"]["buyPrice"])

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
