from blocked_module import initialise
import os.path

class Hasher:

	def __init__(self, data):
		import hashlib
		self.hashObject = hashlib.sha1()


initialise()