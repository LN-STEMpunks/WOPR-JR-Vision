

class P:
	def __init__(self, *v):
		self.v = v

	def tuple(self):
		return tuple(self.v)

	def __add__(self, v):
		return P(self.v[0] + v[0], self.v[1] + v[1])

	def __sub__(self, v):
		return P(self.v[0] - v[0], self.v[1] - v[1])

	def __mul__(self, v):
		return P(self.v[0] * v, self.v[1] * v)

	def __div__(self, v):
		return P(self.v[0] / v, self.v[1] / v)
	
	def ints(self):
		return P(*tuple(map(int, self.v)))