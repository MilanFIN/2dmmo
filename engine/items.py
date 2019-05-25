import configparser
import json

class Item:
    def __init__(self, itemType):
        self.type = itemType
        self.config = configparser.ConfigParser()
        self.config.read("./engine/config.cfg")
        self.wearable = self.config[itemType]["wear"]

    def canWear(self):
        if (self.wearable != "none"):
            return True
        else:
            return False
    def wearType(self):
        return self.wearable
class Items:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("./engine/config.cfg")
        self.itemTypes = json.loads(self.config["allItems"]["types"])
        self.items = {}
        for i in self.itemTypes:
            self.items[i] = Item(i)
    def itemWearable(self, itemName):
        if (itemName in self.itemTypes):
            return self.items[itemName].canWear()
        else:
            return False
    def getWearType(self, itemName):
        if (itemName in self.itemTypes):
            return self.items[itemName].wearType()
        else:
            return "none"

items = Items()
