import configparser
import json




class dungeon:
	def __init__(self, type, size):
		self.config = configparser.ConfigParser()



		self.config.read("./engine/dungeons/"+"testdungeon"+".cfg")

		self.inX = int(self.config["map"]["inx"])
		self.inY = int(self.config["map"]["iny"])


		self.type = type
		self.size = size
		map = self.config["map"]["map"]
		map = map.replace('\n', '')
		map = list(map)




		self.map = [["." for y in range(self.size)] for x in range(self.size)]


		for y in range(30):
			for x in range(30):
				self.map[y][x] = map[30*y+x]


		self.players = []
		#luo täällä kartta

	def getType(self):
		return self.type
	def getMap(self):
		return self.map
	def addPlayer(self, player):
		self.players.append(player)

		player.dX = self.inX
		player.dY = self.inY
	def canMove(self, x, y):
		#just a bounding box at first, figure out blocking tiletypes etc later
		if (x >= 0 and x <= self.size -1):
			if (y >= 0 and y <= self.size -1):
				return True
		return False

	def getObjectLayer(self, player):
		result = [["," for y in range(self.size)] for x in range(self.size)]

		for unit in self.players:
			pass
			result[unit.dY][unit.dX] = "Y"
		result[player.dY][player.dX] = "@"

		return result
	