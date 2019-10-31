

class dungeon:
	def __init__(self, type, size):
		self.type = type
		self.size = size
		self.map  = [["x"] * size] * size


		self.players = []
		#luo täällä kartta

	def getType(self):
		return self.type
	def getMap(self):
		return self.map
	def addPlayer(self, player):
		self.players.append(player)
	def canMove(self, x, y):
		#just a bounding box at first, figure out blocking tiletypes etc later
		if (x > 0 and x < self.size -1):
			if (y > 0 and y < self.size -1):
				return True

	def getObjectLayer(self, player):
		result = [["," for y in range(self.size)] for x in range(self.size)]

		for unit in self.players:
			pass
			result[unit.dX][unit.dY] = "Y"
		result[player.dX][player.dY] = "@"

		return result
	