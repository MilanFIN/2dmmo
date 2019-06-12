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
    def resetFirstGold(self):
        self.firstGold = 0
    def resetSecondGold(self):
        self.secondGold = 0

class Trades:
    def __init__(self):
        self.trades = {}
        self.byFirst = {}
        self.bySecond = {}
    def addTrade(self, first, second):
        self.trades[(first, second)] = Trade(first, second)
        self.byFirst[first] = second
        self.bySecond[second] = first
    def addItem(self, name, item):
        comb = ("","")
        if (name in self.byFirst):
            comb = (name, self.byFirst[name])
            if (comb in self.trades):
                self.trades[comb].addFirstItem(item)

        elif (name in self.bySecond):
            comb = (self.bySecond[name], name)
            if (comb in self.trades):
                self.trades[comb].addSecondItem(item)
        else:
            return
    def removeItem(self, name, item):
        comb = ("","")
        if (name in self.byFirst):
            comb = (name, self.byFirst[name])
            if (comb in self.trades):
                self.trades[comb].removeFirstItem(item)

        elif (name in self.bySecond):
            comb = (self.bySecond[name], name)
            if (comb in self.trades):
                self.trades[comb].removeSecondItem(item)
        else:
            return

    def addGold(self, name, amount):
                comb = ("","")
                if (name in self.byFirst):
                    comb = (name, self.byFirst[name])
                    if (comb in self.trades):
                        self.trades[comb].addFirstGold(amount)

                elif (name in self.bySecond):
                    comb = (self.bySecond[name], name)
                    if (comb in self.trades):
                        self.trades[comb].addSecondGold(item)
                else:
                    return

    def resetGold(self, name):
                comb = ("","")
                if (name in self.byFirst):
                    comb = (name, self.byFirst[name])
                    if (comb in self.trades):
                        self.trades[comb].resetFirstGold()

                elif (name in self.bySecond):
                    comb = (self.bySecond[name], name)
                    if (comb in self.trades):
                        self.trades[comb].resetSecondGold()
                else:
                    return

trades = Trades()
#trades.addTrade("1", "2")
#trades.addItem("2", "testi")
#trades.addItem("2", "testi")
#trades.removeItem("2", "testi")
#for i in trades.trades.values():
#    print(i.getSecondItems())
