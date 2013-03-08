import a
from a import b
from c import *
from d import e, f
from g import dummy, *

from . import h
from . import i, j
from .k import l
from .m import *
from .n import o.p
from .q import another_dummy, *

class DummyClass:

	def something():
		from sys import path
		print(path)

def somethingEntirelyDifferent():
	import bang
	bang.start()
	if bang.result = "BOOOOOOOOM!!!":
		print("Ooops...")

if __name__ == "__main__":
	initialise()
