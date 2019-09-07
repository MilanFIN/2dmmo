from engine.items import *

import copy
import configparser
from engine.items import *


class Inventory:
    def __init__(self):
        self.items = {}  # use as item:count
        self.gold = 0


    def setInventory(self, inv):
        self.items = inv
    def setGold(self, amt):
        if (amt >= 0):
            self.gold = amt


    def addGold(self, amount):
        self.gold += amount

    def removeGold(self, amount):
        self.gold -= amount

    def getGold(self):
        return self.gold

    def addItem(self, itemName):
        if (itemName in self.items):
            self.items[itemName] += 1
        else:
            self.items[itemName] = 1

    def removeItem(self, itemName):
        if (itemName in self.items.keys()):
            self.items[itemName] -= 1
            if (self.items[itemName] <= 0):
                self.items.pop(itemName)

    def getInventorySize(self):
        return sum(self.items.values())

    def getItemTypes(self):
        return self.items.keys()

    def getItemAmount(self, itemName):
        if (itemName in self.items.keys()):
            return self.items[itemName]
        else:
            return 0

    def getPhysicalItems(self):
        # only return items and not gold
        return self.items

    def getAllItems(self):
        returnItems = copy.deepcopy(self.items)
        for item in returnItems.keys():

            returnItems[item] = (returnItems[item], items.itemWearable(item))
        if (self.gold != 0):
            returnItems["gold"] = (self.gold, False)
        return returnItems

    def checkIfHasItem(self, item):
        if (item in self.items.keys()):
            return True
        else:
            return False



class playerBank:
    def __init__(self):
        self.items = {}  # use as item:count
        self.gold = 0

    def getBalance(self):
        return self.gold

    def setBalance(self, amt):
        if (amt >= 0):
            self.gold = amt

    def deposit(self, amount):
        self.gold += abs(amount)

    def canWithDraw(self, amount):
        if (self.gold - abs(amount) >= 0):
            return True
        else:
            return False

    def withDraw(self, amount):
        self.gold -= abs(amount)


class playerWear:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("./engine/config.cfg")

        self.armorType = ""
        self.armorBonus = 0
        self.attackType = ""
        self.attackBonus = 0
        self.shipType = ""
        self.shipBonus = 0
        self.maxCannon = 0
        self.cannonType = ""
        self.cannonBonus = 0
        self.cannonSize = 0


    def getWear(self):
        wear = [self.armorType, self.attackType, self.shipType, self.cannonType]
        return wear

    def resetAll(self):
        self.armorType = ""
        self.armorBonus = 0
        self.attackType = ""
        self.attackBonus = 0
        self.shipType = ""
        self.shipBonus = 0
        self.maxCannon = 0
        self.cannonType = ""
        self.cannonBonus = 0
        self.cannonSize

    def removeIfWorn(self, itemName):
        if (not items.itemWearable(itemName)):
            return
        item = itemName
        if (item == self.armorType):
            self.armorType = ""
            self.armorBonus = 0
        elif (item == self.attackType):
            self.attackType = ""
            self.attackBonus = 0
        elif (item == self.shipType):
            self.shipType = ""
            self.ShipBonus = 0
            self.maxCannon = 0
            self.cannonType = ""
            self.cannonBonus = 0
            self.cannonSize = 0
        elif (item == self.cannonType):
            self.cannonType = ""
            self.cannonBonus = 0
            self.cannonSize


    def changeItem(self, itemName):
        if (not items.itemWearable(itemName)):
            return

        itemType = items.getWearType(itemName)
        bonus = items.getWearBonus(itemName)

        if (itemType == "armor"):
            self.armorType = itemName
            self.armorBonus = bonus
        if (itemType == "attack"):
            self.attackType = itemName
            self.attackBonus = bonus
        if (itemType == "ship"):
            self.shipType = itemName
            self.shipBonus = bonus
            self.maxCannon = items.getMaxCannonSize(itemName)
            if (self.cannonSize > self.maxCannon):
                self.cannonType = ""
                self.cannonBonus = 0
                self.cannonSize = 0

        if (itemType == "cannon"):
            if (items.getCannonSize(itemName) <= self.maxCannon):
                self.cannonBonus = items.getWearBonus(itemName)
                self.cannonType = itemName
                self.cannonSize = items.getCannonSize(itemName)

    def getShipDefBonus(self):
        return self.shipBonus
    def getCannonBonus(self):
        return self.cannonBonus
    def getArmorBonus(self):
        return self.armorBonus
    def getAttackBonus(self):
        return self.attackBonus


    """
    def changeShip(self, shipName, bonus):
        self.shipType = shipName
        self.shipBonus = bonus
    def resetShip(self):
        self.shipType = ""
        self.shipBonus = 0
    def changeArmor(self, armorName, bonus):
        self.armorType = armorName
        self.armorBonus = bonus
    def resetArmor(self):
        self.armorType = ""
        self.armorBonus = 0

    def changeAttack(self, attackName, bonus):
        self.attackType = attackName
        self.attackBonus = bonus
    def resetAttack(self):
        self.attackType = ""
        self.attackBonus = 0
    """


