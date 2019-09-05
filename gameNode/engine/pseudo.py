import configparser



class Pseudo:
    def __init__(self):
        pass
    """island related"""
    def generateChunk(self, x, y, seed):
        chunkSeed = seed
        if (x != 0):
            chunkSeed = chunkSeed * x + chunkSeed // x
        if (y != 0):
            chunkSeed = chunkSeed * y + chunkSeed // y
        #print(chunkSeed)
        chunkSeed = chunkSeed % 1000001
        return chunkSeed

    def islandExists(self, x, y, seed):
        chunkSeed = self.generateChunk(x, y, seed)
        islandExists = chunkSeed % 3

        if (islandExists == 0):
            return True
        return False

    def getIslandDimensions(self, x, y, seed, size):
        chunkSeed = self.generateChunk(x, y, seed)
        islandWidth = chunkSeed % 11 // 2
        if (islandWidth > size -2):
            islandWidth = size -2
        islandHeight = chunkSeed % 13 // 2
        if (islandHeight > size -2):
            islandHeight = size -2

        #this one needs fixing if supposed to work right
        islandCenterOffset = 0 #= chunkSeed % 5 // 2

        return islandWidth, islandHeight, islandCenterOffset

    def getIslandExpansionDirection(self, x, y, worldX, worldY, seed):
        chunkSeed = self.generateChunk(worldX, worldY, seed)

        tileSeed = chunkSeed * x + chunkSeed * y+ chunkSeed
        direction = tileSeed % 4
        return direction

    """range and probabilities"""
    def inRange(self, count, x, y, seed):
        xseed = seed + x % 1000001
        yseed = seed - y % 1000003
        objectSeed = (xseed + yseed) % count
        return objectSeed

    def npcProbability(self, fraction, x, y, seed):
        xseed = seed + x % 1000007
        yseed = seed - y % 1000011
        objectSeed = (xseed + yseed) % fraction
        return objectSeed
    def monsterProbability(self, fraction, x, y, seed):
        xseed = seed + x % 1000001
        yseed = seed - y % 1000003
        objectSeed = (xseed + yseed) % fraction
        return objectSeed

    """building locations"""
    def harborLocation(self, landTileCount, x, y, seed):
        chunkSeed = seed
        if (x != 0):
            chunkSeed = chunkSeed * x + chunkSeed // x
        if (y!= 0):
            chunkSeed = chunkSeed * y + chunkSeed // y

        tileNumber = chunkSeed % 170773 % landTileCount
        return tileNumber

    def buildingLocation(self, landTileCount, x, y, seed):
        chunkSeed = seed
        if (x != 0):
            chunkSeed = chunkSeed * x + chunkSeed // x
        if (y!= 0):
            chunkSeed = chunkSeed * y + chunkSeed // y

        tileNumber = chunkSeed % 170767 % landTileCount
        return tileNumber
    
    def getNumberInRangeByLocation(self, min, max, x, y, seed):
        if (min == max):
            return min
        chunkSeed = seed
        if (x != 0):
            chunkSeed = chunkSeed * x + chunkSeed // x
        if (y != 0):
            chunkSeed = chunkSeed * y + chunkSeed // y
        #print(chunkSeed)
        chunkSeed = chunkSeed % 1001 % (max-min)
        return chunkSeed



pseudo = Pseudo()
