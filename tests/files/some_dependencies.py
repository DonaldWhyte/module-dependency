from foo import foobar
from bar import *
import os
from blocked_module import initialise

class DummyClass:

	def something():
		from sys import path
		print(path)

def somethingEntirelyDifferent():
	import bang
	bang.start()
	if bag.result = "BOOOOOOOOM!!!":
		print("Ooops...")

if __name__ == "__main__":
	initialise()



