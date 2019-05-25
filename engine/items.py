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
class Items:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("./engine/config.cfg")
        self.itemTypes = json.loads(self.config["allItems"]["types"])
        self.items = {}
        for i in self.itemTypes:
            self.items[i] = Item(i)
        print(self.items)
    def itemWearable(self, itemName):
        if (itemName in self.itemTypes):
            return self.items[itemName].canWear()
        else:
            return False

items = Items()
