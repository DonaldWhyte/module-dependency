from blocked_module import initialise
from os.path import abspath

class Hasher:

	def __init__(self, data):
		import hashlib
		self.hashObject = hashlib.sha1()


initialise()