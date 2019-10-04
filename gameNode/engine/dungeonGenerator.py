

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
	def getObjectLayer(self, player):
		#should return objects here, not relevant yet
		result = [[","] * size] * self.size

		for unit in self.players:
			pass
			# check players location, if unit == player, use @, otherwise Y
			# MOVEMENT CHECK GOES IN THIS CLASS
		return result
	