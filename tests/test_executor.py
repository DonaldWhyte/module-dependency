import unittest
import sys
import os
sys.path.append(os.environ.get("PROJECT_ROOT_DIRECTORY", "."))

from moduledependency import Executor
from moduledependency import ResultOutputter



class MockResultOutputter(ResultOutputter):

	OUTPUT_FILE = ".result_output.txt"

	def __init__(self):
		super().__init__()

	def createOutput(self, dependencies):
		f.write( str(dependencies) )


class TestExecutor(unittest.TestCase):

	EXPECTED_DEPENDENCIES = {
	
	}

	def setUp(self):
		# Create executor without a visualiser
		self.executor = Executor()

	def tearDown(self):
		self.executor = None

	def test_construction(self):
		self.assertEqual(self.executor.outputter, None)

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
			with open(MockResultOutputter.OUTPUT_FILE, "r") as f:
				selfassertEqual(f.read(), str(self.EXPECTED_DEPENDENCIES))
		finally: # cleanup
			if  os.path.isfile(MockResultOutputter.OUTPUT_FILE):
				os.remove(MockResultOutputter.OUTPUT_FILE)