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

    def getTradeState(self, name1, name2):
        comb = ("","")
        result = []
        if ((name1, name2) in self.trades):
            comb = (name1, name2)
            result = [self.trades[comb].getFirstItems(),
                        self.trades[comb].getFirstGold(),
                        self.trades[comb].getSecondItems(),
                        self.trades[comb].getSecondGold()]
        elif ((name2, name1) in self.trades):
            comb = (name2, name1)
            result = [self.trades[comb].getSecondItems(),
                        self.trades[comb].getSecondGold(),
                        self.trades[comb].getFirstItems(),
                        self.trades[comb].getFirstGold()]
        else:
            return
        return result

    def removeTrade(self, name1, name2):
        if ((name1, name2) in self.trades):
            self.trades.pop((name1, name2), None)
        if ((name2, name1) in self.trades):
            self.trades.pop((name2, name1), None)


trades = Trades()
