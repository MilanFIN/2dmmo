class Trade:
    def __init__(self, first, second):
        self.first = first
        self.second = second
        self.firstItems = []
        self.secondItems = []
        self.firstGold = 0
        self.secondGold = 0

    def getFirstItems(self):
        return self.firstItems
    def getSecondItems(self):
        return self.secondItems
    def getFirstGold(self):
        return self.firstGold
    def getSecondGold(self):
        return self.secondGold
    def addFirstItem(self, item):
        self.firstItems.append(item)
    def addSecondItem(self, item):
        self.secondItems.append(item)
    def removeFirstItem(self, item):
        if item in (self.firstItems):
            self.firstItems.remove(item)
    def removeSecondItem(self, item):
        if item in (self.secondItems):
            self.secondItems.remove(item)
    def addFirstGold(self, amount):
        self.firstGold += amount
    def addSecondGold(self, amount):
        self.secondGold += amount
    def getFirstItems(self):
        return self.firstItems


class Trades:
    def __init__(self):
        self.trades = {}
        self.byFirst = {}
        self.bySeconds = {}
    def addTrade(self, first, second):
        self.trades[(first, second)] = Trade
        self.byFirst[first] = second
        self.bySecond[second] = first
    


trades = Trades()
