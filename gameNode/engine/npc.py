from random import shuffle
import configparser
import json
import random
import time
from engine.pseudo import *

class AiBase:
    # define class for npcs, non violent non player characters
    def __init__(self, name, worldx, worldy, x, y, worldSize, onLand, seed):

        self.allowedTerrain = "."
        self.unAllowedTerrain = "x"
        self.roamRadius = 1

        self.character = "n"

        self.name_ = name
        self.worldx_ = worldx
        self.worldy_ = worldy
        self.x_ = x
        self.y_ = y
        self.worldSize_ = worldSize
        self.onLand = onLand
        self.lastMove = 0  # put the time the npc moved here,
        # will be used to figure out if it has to move again
        self.originX_ = x
        self.originY_ = y
        self.directions = [0, 1, 2, 3]  # left, right, up, down
        self.canMove = True
        self.type = ""

    def getCharacter(self):
        return self.character

    def getName(self):
        return self.name_
    def getType(self):
        return self.type

    def getWorldX(self):
        return self.worldx_

    def getWorldY(self):
        return self.worldy_

    def getX(self):
        return self.x_

    def getY(self):
        return self.y_

    def setMovable(self):
        self.canMove = True

    def disableMovingIfNearby(self, x, y):
        # disable moving, if x and y are around the npc, (x,y) is player pos
        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                if (abs(x - self.x_) <= 1 and abs(y - self.y_) <= 1):

                    self.canMove = False
                    return

    def move(self, area):
        # move toward random direction if possible
        if (not self.canMove):
            return
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
            if (abs(newX - self.originX_) > self.roamRadius or abs(newY - self.originY_) > self.roamRadius):
                continue
            if (newX < 0 or newY < 0 or newX > self.worldSize_ - 1 or newY > self.worldSize_ - 1):
                continue
            newLocation = area[newY][newX]
            if (newLocation not in self.allowedTerrain):
                continue

            self.x_ = newX
            self.y_ = newY
            break
        # roam randomly but not outside of the playable area.
        # mayble also don't go into water
        # at first only move around the spawn point

class Npc(AiBase):
    # define class for npcs, non violent non player characters
    def __init__(self, name, worldx, worldy, x, y, worldSize, onLand, seed):
        self.name_ = name
        self.worldx_ = worldx
        self.worldy_ = worldy
        self.x_ = x
        self.y_ = y
        self.worldSize_ = worldSize
        self.onLand = onLand

        self.config = configparser.ConfigParser()
        self.config.read("./engine/config.cfg")


        possibleTypes = json.loads(self.config["npcs"]["types"])
        choiceList = []
        for i in possibleTypes:
            if (self.config[i]["terrain"] == "ground" and self.onLand):
                weight = int(self.config[i]["probabilityFactor"])
                for j in range(weight):
                    choiceList.append(i)
            elif (self.config[i]["terrain"] == "sea" and self.onLand == False):
                weight = int(self.config[i]["probabilityFactor"])
                for j in range(weight):
                    choiceList.append(i)

        
        #self.type = random.choice(choiceList)
        self.type = choiceList[pseudo.getNumberInRangeByLocation(0, len(choiceList), worldx, worldy, seed)]



        self.AllowedTerrain = ""
        if (self.onLand):
            self.allowedTerrain = self.config["terrain"]["ground"]
        else:
            self.allowedTerrain = self.config["terrain"]["sea"]

        self.roamRadius = int(self.config[self.type]["moveRadius"])

        self.character = self.config[self.type]["character"]

        self.lines = json.loads(self.config[self.type]["lines"])

        self.lastMove = 0  # put the time the npc moved here,
        # will be used to figure out if it has to move again
        self.originX_ = x
        self.originY_ = y
        self.directions = [0, 1, 2, 3]  # left, right, up, down
        self.canMove = True

    def getLine(self):
        return random.choice(self.lines)


class Monster(AiBase):
    # define hostile npc class
    def __init__(self, name, worldx, worldy, x, y, worldSize, onLand, seed):

        self.name_ = name
        self.worldx_ = worldx
        self.worldy_ = worldy
        self.x_ = x
        self.y_ = y
        self.worldSize_ = worldSize
        self.onLand = onLand

        self.config = configparser.ConfigParser()
        self.config.read("./engine/config.cfg")

        possibleTypes = json.loads(self.config["monsters"]["types"])
        """SHOULD THIS REMAIN RANDOM?"""
        choiceList = []
        for i in possibleTypes:
            if (self.config[i]["terrain"] == "ground" and self.onLand):
                weight = int(self.config[i]["probabilityFactor"])
                for j in range(weight):
                    choiceList.append(i)
            elif (self.config[i]["terrain"] == "sea" and self.onLand == False):
                weight = int(self.config[i]["probabilityFactor"])
                for j in range(weight):
                    choiceList.append(i)

        #self.type = random.choice(choiceList)
        self.type = choiceList[pseudo.getNumberInRangeByLocation(0, len(choiceList), worldx, worldy, seed)]



        self.AllowedTerrain = ""
        if (self.onLand):
            self.allowedTerrain = self.config["terrain"]["ground"]
        else:
            self.allowedTerrain = self.config["terrain"]["sea"]

        self.character = self.config[self.type]["character"]
        self.roamRadius = int(self.config[self.type]["moveRadius"])
        self.hp = int(self.config[self.type]["hp"])
        self.attack = int(self.config[self.type]["attack"])
        self.attackType = self.config[self.type]["attackType"]
        self.deathNote = self.config[self.type]["deathNote"]

        self.drops = ""
        self.dropValue = 0

        if (self.config.has_option(self.type, "itemDrop")):
            self.drops = self.config[self.type]["itemDrop"]
            self.dropValue = int(self.config[self.type]["dropAmount"])

        self.lastMove = 0  # put the time the npc moved here,
        # will be used to figure out if it has to move again
        self.originX_ = x
        self.originY_ = y
        self.directions = [0, 1, 2, 3]  # left, right, up, down
        self.canMove = True


        self.deathTime = 0
        self.respawnDelay = int(self.config[self.type]["respawnDelay"])
        self.originalHp = self.hp



    def alive(self):
        if (self.hp > 0):
            return True
        else:
            return False

    def hit(self, amount):
        self.hp -= amount
        if (self.hp <= 0):
            self.deathTime = time.time()

    def respawn(self):
        self.hp = self.originalHp
    def canRespawn(self):
        if (time.time() - self.deathTime >= self.respawnDelay):
            return True
        else:
            return False





    def getAttack(self):
        return self.attack
    def getAttackType(self):
        return self.attackType
    def getDeathNote(self):
        return self.deathNote
    def dropType(self):
        return self.drops
    def dropAmount(self):
        return self.dropValue




"""
npc = Npc("asd", 10, 10, 0, 0, 20)
for i in range(30):
    npc.move()
    print(npc.getName(), npc.getX(), npc.getY())
"""
