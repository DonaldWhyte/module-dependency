import unittest
import sys
import os
sys.path.append(os.environ.get("PROJECT_ROOT_DIRECTORY", "."))

from moduledependency.dependency_extractor import ModuleDependencyExtractor

class TestModuleDependencyExtractor(unittest.TestCase):

	def setUp(self):
		self.extractorNoWhitelist = ModuleDependencyExtractor()
		self.whitelist = [ "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "files" ]
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
		EXPECTED_WITH_WHITELIST = [
			"a", "a.b", "c", "d.e", "d.f", "g", # ABSOLUTE
			"some_dependencies.h", "some_dependencies.i", "some_dependencies.j",  # RELATIVE
			"some_dependencies.k.l", "some_dependencies.m", "some_dependencies.n.o.p",
			"some_dependencies.q"
		]
		EXPECTED_WITHOUT_WHITELIST = list(EXPECTED_WITH_WHITELIST)
		EXPECTED_WITHOUT_WHITELIST += [ "sys.path", "bang" ]
		
		# Test with invalid filename type
		with self.assertRaises(TypeError):
			self.extractorNoWhitelist.extract(5353)
		# Test with non-existent filename
		with self.assertRaises(IOError):
			self.extractorNoWhitelist.extract("non-existent")

		# Test with file that has no module dependencies
		self.assertEqual(self.extractorNoWhitelist.extract("files/no_dependencies.py"), set())
		self.assertEqual(self.extractorWithWhitelist.extract("files/no_dependencies.py"), set())
		# Test with file that has only dependencies not in whitelist
		self.assertEqual(self.extractorNoWhitelist.extract("files/blocked_dependencies.py"),
			set(["hashlib", "blocked_module.initialise", "os.path.abspath"]))
		self.assertEqual(self.extractorWithWhitelist.extract("files/blocked_dependencies.py"), set())
		# Test with file that has some standard library (not in whitelist) and
		# internal module dependencies
		self.assertEqual(self.extractorNoWhitelist.extract("files/some_dependencies.py"),
			set(EXPECTED_WITHOUT_WHITELIST)) # should have blocked modules in too!!!
		self.assertEqual(self.extractorWithWhitelist.extract("files/some_dependencies.py"),
			set(EXPECTED_WITH_WHITELIST))
