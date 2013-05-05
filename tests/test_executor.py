import unittest
import sys
import os
sys.path.append(os.environ.get("PROJECT_ROOT_DIRECTORY", "."))

from moduledependency.executor import Executor
from moduledependency.outputter import ResultOutputter



class MockResultOutputter(ResultOutputter):

	OUTPUT_FILE = ".result_output.txt"

	def __init__(self):
		super().__init__()

	def createOutput(self, dependencies):
		# Output dictionary to a file in sorted manner
		with open(self.OUTPUT_FILE, "w") as f:
			for key in sorted(dependencies.keys()):
				f.write("{} = [ ".format(key))
				for dep in sorted(dependencies[key]):
					f.write(dep + " ")
				f.write("]\n")


class TestExecutor(unittest.TestCase):

	EXPECTED_DEPENDENCIES = {
		"project" : set(["project.pack", "project.pack2"]),
		"project.__main__" : set(["project.a", "project.pack.subpack2"]),
		"project.a" : set(["project.a", "project.pack"]),
		"project.pack.subpack2" : set(["project.pack.subpack2.subsubpack.c", "project.pack.subpack2.d"]),
		"project.pack.subpack2.d" : set(["project.pack.subpack2.subsubpack.c", "project.pack2.e", "project.pack"]),
		"project.pack.subpack2.subsubpack.c" : set(),
		"project.pack2.e" : set(["project.pack2.subpack.f"]),
		"project.pack2.subpack.f" : set(["project.pack2.e"])
	}

	EXPECTED_DEPENDENCIES_WITH_DEPTH_LIMIT = {
		"project" : set(["project.pack", "project.pack2"]),
		"project.__main__" : set(["project.a", "project.pack"]),
		"project.a" : set(["project.pack"]),
		"project.pack" : set(["project.pack2"]),
		"project.pack2" : set()
	}

	EXPECTED_FILE_CONTENTS = """project = [ project.pack project.pack2 ]
project.__main__ = [ project.a project.pack.subpack2 ]
project.a = [ project.a project.pack ]
project.pack.subpack2 = [ project.pack.subpack2.d project.pack.subpack2.subsubpack.c ]
project.pack.subpack2.d = [ project.pack project.pack.subpack2.subsubpack.c project.pack2.e ]
project.pack.subpack2.subsubpack.c = [ ]
project.pack2.e = [ project.pack2.subpack.f ]
project.pack2.subpack.f = [ project.pack2.e ]
"""

	EXPECTED_FILE_CONTENTS_WITH_DEPTH_LIMIT = """project = [ project.pack project.pack2 ]
project.__main__ = [ project.a project.pack ]
project.a = [ project.pack ]
project.pack = [ project.pack2 ]
project.pack2 = [ ]
"""

	def setUp(self):
		# Create executor without a visualiser
		self.executor = Executor()

	def tearDown(self):
		self.executor = None

	def test_construction(self):
		self.assertEqual(self.executor.outputter, None)

	def test_setMaximumDepth(self):
		# Test non-integer
		with self.assertRaises(TypeError):
			self.executor.setMaximumDepth("1")
		with self.assertRaises(TypeError):
			self.executor.setMaximumDepth("HAHA")
		with self.assertRaises(TypeError):
			self.executor.setMaximumDepth([])
		# Test negative depths
		with self.assertRaises(ValueError):
			self.executor.setMaximumDepth(-1)
		with self.assertRaises(ValueError):
			self.executor.setMaximumDepth(-43298)
		# Test valid depths
		self.executor.setMaximumDepth(0)
		self.assertEqual(self.executor.maximumDepth, 0)
		self.executor.setMaximumDepth(1)
		self.assertEqual(self.executor.maximumDepth, 1)
		self.executor.setMaximumDepth(8)
		self.assertEqual(self.executor.maximumDepth, 8)
		self.executor.setMaximumDepth(78487)
		self.assertEqual(self.executor.maximumDepth, 78487)
		self.executor.setMaximumDepth(None)
		self.assertEqual(self.executor.maximumDepth, None)

	def test_searchForDependencies(self):
		# Test non-existent project directory
		with self.assertRaises(IOError):
			self.executor.searchForDependencies("non_existent_dir")
		# Test valid project directory
		self.assertEqual(self.executor.searchForDependencies("project"), self.EXPECTED_DEPENDENCIES)
		
	def test_execute(self):
		try:
			# Test non-existent project directory
			with self.assertRaises(IOError):
				self.executor.execute("non_existent_dir")
			# Test valid project directory
			self.assertEqual(self.executor.execute("project"), self.EXPECTED_DEPENDENCIES)

			# Now test the same call but with an outputter assigned
			self.executor.setOutputter( MockResultOutputter() )
			self.assertEqual(self.executor.execute("project"), self.EXPECTED_DEPENDENCIES)
			# Test that the result was outputted correctly (i.e. output ran!)
			self.assertTrue( os.path.isfile( MockResultOutputter.OUTPUT_FILE ) )
			# Also test that the output was correct
			with open(MockResultOutputter.OUTPUT_FILE, "r") as f:
				self.assertEqual(f.read(), self.EXPECTED_FILE_CONTENTS)	

			# Test again, but with a maximum on depth set this timre as well
			self.executor.setMaximumDepth(1)
			self.assertEqual(self.executor.execute("project"), self.EXPECTED_DEPENDENCIES_WITH_DEPTH_LIMIT)
			# Test that the result was outputted correctly (i.e. output ran!)
			self.assertTrue( os.path.isfile( MockResultOutputter.OUTPUT_FILE ) )
			# Also test that the output was correct
			with open(MockResultOutputter.OUTPUT_FILE, "r") as f:
				self.assertEqual(f.read(), self.EXPECTED_FILE_CONTENTS_WITH_DEPTH_LIMIT)	
		finally: # cleanup
			if os.path.isfile(MockResultOutputter.OUTPUT_FILE):
				os.remove(MockResultOutputter.OUTPUT_FILE)