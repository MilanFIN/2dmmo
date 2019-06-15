class Trade:
    def __init__(self, first, second):
        self.first = first
        self.second = second
        self.firstItems = {}
        self.secondItems = {}
        self.firstGold = 0
        self.secondGold = 0

        self.firstAccept = False
        self.secondAccept = False

    def acceptFirst(self):
        self.firstAccept = True

    def acceptSecond(self):
        self.secondAccept = True

    def tradeAccepted(self):
        if (self.firstAccept and self.secondAccept):
            return True
        else:
            return False

    def getFirstItems(self):
        return self.firstItems
    def getSecondItems(self):
        return self.secondItems
    def getFirstGold(self):
        return self.firstGold
    def getSecondGold(self):
        return self.secondGold
    def addFirstItem(self, item):

        self.firstAccept = False
        self.secondAccept = False

        if item in (self.firstItems):
            self.firstItems[item] += 1
        else:
            self.firstItems[item] = 1
    def addSecondItem(self, item):

        self.firstAccept = False
        self.secondAccept = False

        if item in (self.secondItems):
            self.secondItems[item] += 1
        else:
            self.secondItems[item] = 1
    def removeFirstItem(self, item):

        self.firstAccept = False
        self.secondAccept = False

        if item in (self.firstItems):
            if (self.firstItems[item] > 1):
                self.firstItems[item] -= 1
            else:
                self.firstItems.pop(item, None)
    def removeSecondItem(self, item):

        self.firstAccept = False
        self.secondAccept = False

        if item in (self.secondItems):
            if (self.secondItems[item] > 1):
                self.secondItems[item] -= 1
            else:
                self.secondItems.pop(item, None)
    def addFirstGold(self, amount):
        self.firstAccept = False
        self.secondAccept = False

        self.firstGold += amount
    def addSecondGold(self, amount):
        self.firstAccept = False
        self.secondAccept = False

        self.secondGold += amount
    def removeFirstGold(self, amount):
        self.firstAccept = False
        self.secondAccept = False

        if (self.firstGold - amount < 0):
            self.firstGold = 0
        else:
            self.firstGold -= amount
    def removeSecondGold(self, amount):
        self.firstAccept = False
        self.secondAccept = False

        if (self.secondGold - amount < 0):
            self.secondGold = 0
        else:
            self.secondGold -= amount


class Trades:
    def __init__(self):
        self.trades = {}
        self.byFirst = {}
        self.bySecond = {}

    def addTrade(self, first, second):
        self.trades[(first, second)] = Trade(first, second)
        self.byFirst[first] = second
        self.bySecond[second] = first
    def getOpponent(self, name):

        if (name in self.byFirst):
            return self.byFirst[name]
        elif (name in self.bySecond):
            return self.bySecond[name]
        else:
            return None

    def acceptTrade(self, name):
        comb = ("","")
        if (name in self.byFirst):
            comb = (name, self.byFirst[name])
            if (comb in self.trades):
                self.trades[comb].acceptFirst()

        elif (name in self.bySecond):
            comb = (self.bySecond[name], name)
            if (comb in self.trades):
                self.trades[comb].acceptSecond()
        else:
            return

    def tradeAccepted(self, name1, name2):
        if ((name1, name2) in self.trades):
            return self.trades[name1, name2].tradeAccepted()
        elif ((name2, name1) in self.trades):
            return self.trades[name2, name1].tradeAccepted()

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
        if (amount < 0):
            return
        comb = ("","")
        if (name in self.byFirst):
            comb = (name, self.byFirst[name])
            if (comb in self.trades):
                self.trades[comb].addFirstGold(amount)

        elif (name in self.bySecond):
            comb = (self.bySecond[name], name)
            if (comb in self.trades):
                self.trades[comb].addSecondGold(amount)
        else:
            return

    def removeGold(self, name, amount):
        if (amount < 0):
            return
        comb = ("","")
        if (name in self.byFirst):
            comb = (name, self.byFirst[name])
            if (comb in self.trades):
                self.trades[comb].removeFirstGold(amount)

        elif (name in self.bySecond):
            comb = (self.bySecond[name], name)
            if (comb in self.trades):
                self.trades[comb].removeSecondGold(amount)
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
