from random import shuffle
import configparser



#unAllowedTerrain = ["."]


class Npc:
    def __init__(self, name, worldx, worldy, x, y, worldSize):

        self.config = configparser.ConfigParser()
        self.config.read("./engine/config.cfg")
        self.unAllowedTerrain = self.config["npc"]["unallowedTerrain"]


        self.character = self.config["npc"]["character"]
        self.name_ = name
        self.worldx_ = worldx
        self.worldy_ = worldy
        self.x_ = x
        self.y_ = y
        self.worldSize_ = worldSize
        self.lastMove = 0 # put the time the npc moved here,
        #will be used to figure out if it has to move again
        self.originX_ = x
        self.originY_ = y
        self.roamRadius = 3
        self.directions = [0, 1, 2, 3] # left, right, up, down
        self.exists = True
    def getCharacter(self):
        return self.character
    def doesExist(self):
        return self.exists
    def makeNotExist(self):
        self.exists = False
    def makeExist(self):
        self.exists = True
    def getName(self):
        return self.name_
    def getWorldX(self):
        return self.worldx_
    def getWorldY(self):
        return self.worldy_
    def getX(self):
        return self.x_
    def getY(self):
        return self.y_
    def move(self, area):
        shuffle(self.directions)
        for newDirection in self.directions:
            newX = 0
            newY = 0
            if (newDirection == 0):
                newX = self.x_ - 1
                newY = self.y_
            if (newDirection == 1):
                newX = self.x_ + 1
                newY = self.y_
            if (newDirection == 2):
                newX = self.x_
                newY = self.y_ - 1
            if (newDirection == 3):
                newX = self.x_
                newY = self.y_ + 1
            if (abs(newX  - self.originX_) > self.roamRadius or abs(newY  - self.originY_) > self.roamRadius):
                continue
            newLocation = area[newY][newX]
            if (newLocation in self.unAllowedTerrain):
                continue
            self.x_ = newX
            self.y_ = newY
            break
        #roam randomly but not outside of the playable area.
        #mayble also don't go into water
        #at first only move around the spawn point


"""
npc = Npc("asd", 10, 10, 0, 0, 20)
for i in range(30):
    npc.move()
    print(npc.getName(), npc.getX(), npc.getY())
"""
