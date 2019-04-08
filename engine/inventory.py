import copy

class Inventory:
    def __init__(self):
        self.items = {} #use as item:count
        self.gold = 0
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
        #only return items and not gold
        return self.items
    def getAllItems(self):
        returnItems = copy.deepcopy(self.items)
        if (self.gold != 0):
            returnItems["gold"] = self.gold
        return returnItems

class playerBank:
    def __init__(self):
        self.items = {} #use as item:count
        self.gold = 0
    def getBalance(self):
        return self.gold
    def deposit(self, amount):
        self.gold += abs(amount)
    def canWithDraw(self, amount):
        if (self.gold - abs(amount) >= 0):
            return True
        else:
            return False
    def withDraw(self, amount):
        self.gold -= abs(amount)



"""
inv = Inventory()
inv.addItem("tree")
print(inv.getInventorySize())

inv.addItem("tree")
print(inv.getInventorySize())

inv.removeItem("tree")

print(inv.getInventorySize())
inv.removeItem("tree")
print(inv.getInventorySize())
inv.removeItem("tree")
print(inv.getInventorySize())
"""
