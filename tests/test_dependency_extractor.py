import unittest
import sys
import os
sys.path.append(os.environ.get("PROJECT_ROOT_DIRECTORY", "."))

from moduledependency.dependency_extractor import ModuleDependencyExtractor

class TestModuleDependencyExtractor(unittest.TestCase):

	def setUp(self):
		self.extractorNoWhitelist = ModuleDependencyExtractor(None)
		self.whitelist = [ "foo", "bar", "foobar", "shazam", "bang" ]
		self.extractorWithWhitelist = ModuleDependencyExtractor(self.whitelist)

	def tearDown(self):
		self.extractorNoWhitelist = None
		self.extractorNoWhitelist = None
		self.usingWhitelist = None

	def test_construction(self):
		# Test with invalid type of whitelist passed
		with self.assertRaises(TypeError):
			ModuleDependencyExtractor(5353)
		# Test objects were constructed successfully
		self.assertEqual(self.extractorNoWhitelist.whitelist, None)
		self.assertEqual(self.extractorWithWhitelist.whitelist, self.whitelist)

	def test_usingWhitelist(self):
		self.assertFalse( self.extractorNoWhitelist.usingWhitelist() )
		self.assertTrue( self.extractorWithWhitelist.usingWhitelist() )

	def test_extract(self):
		# Test with invalid filename type
		with self.assertRaises(TypeError):
			self.extractor.extract(5353)
		# Test with non-existent filename
		with self.assertRaises(TypeError):
			self.extractor.extract("non-existent")

		# Test with file that has no module dependencies
		self.assrtEqual(self.extractorNoWhitelist.extract("files/no_dependencies.py"), [])
		self.assrtEqual(self.extractorWithWhitelist.extract("files/no_dependencies.py"), [])
		# Test with file that has only dependencies not in whitelist
		self.assrtEqual(self.extractorNoWhitelist.extract("files/blocked_dependencies.py"),
			["hashlib", "block_module", "os.path"])
		self.assertEqual(self.extractorWithWhitelist.extract("files/blocked_dependencies.py"), [])
		# Test with file that has some standard library (not in whitelist) and
		# internal module dependencies
		self.assertEqual(self.extractorNoWhitelist.extract("files/some_dependencies.py"),
			["foo", "bar", "foobar", "bang", "sys", "os", "blocked_module"]) # should have STDlib modules in too!!!
		self.assertEqual(self.extractorWithWhitelist.extract("files/some_dependencies.py"),
			["foo", "bar", "foobar", "bang"])