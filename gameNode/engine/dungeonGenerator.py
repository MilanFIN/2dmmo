import configparser
import json




class dungeon:
	def __init__(self, type, size):
		self.config = configparser.ConfigParser()



		self.config.read("./engine/dungeons/"+"testdungeon"+".cfg")

		self.inX = int(self.config["map"]["inx"])
		self.inY = int(self.config["map"]["iny"])

		self.outX = int(self.config["map"]["outx"])
		self.outY = int(self.config["map"]["outy"])


		self.ground = json.loads(self.config["map"]["ground"])  
		self.wall = self.config["map"]["wall"]

		self.entrance = self.config["map"]["entrance"]
		self.exit = self.config["map"]["exit"]

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
	def removePlayer(self, player):
		if player in self.players:
			self.players.remove(player)
			player.leaveDungeon()
	def canMove(self, x, y):
		#just a bounding box at first, figure out blocking tiletypes etc later
		if (x >= 0 and x <= self.size -1):
			if (y >= 0 and y <= self.size -1):
				if (self.map[y][x] in self.ground):
					return True
		return False

	def getObjectLayer(self, player):
		result = [["," for y in range(self.size)] for x in range(self.size)]

		#place entrance and exit (if above each other, exit is shown)

		result[self.inY][self.inX] = self.entrance
		result[self.outY][self.outX] = self.exit


		#place players to objectlayer
		for unit in self.players:
			pass
			result[unit.dY][unit.dX] = "Y"
		result[player.dY][player.dX] = "@"

		return result
	

	def doAction(self, player):
		if (not player.canAct()):
			return
		else:
			if (player.dX == self.outX and player.dY == self.outY):
				#leave dungeon
				self.removePlayer(player)
				return