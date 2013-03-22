import unittest
import sys
import os
import platform
import shutil

sys.path.append(os.environ.get("PROJECT_ROOT_DIRECTORY", "."))
from moduledependency.whitelist import WhitelistGenerator, WhitelistApplier


class TestWhitelistGenerator(unittest.TestCase):

	def createFile(self, filename):
		"""Create empty text file at given path."""
		with open(filename, "w") as f:
			f.write("")

	def setUp(self):
		self.whitelistGenerator = WhitelistGenerator()
		# Create mock files for testing
		try:
			os.mkdir(".test_whitelist_generator")
			os.mkdir(".test_whitelist_generator/empty")
			os.mkdir(".test_whitelist_generator/flat")
			self.createFile(".test_whitelist_generator/flat/m1.py")
			self.createFile(".test_whitelist_generator/flat/m2.py")
			self.createFile(".test_whitelist_generator/flat/m3.py")
			os.mkdir(".test_whitelist_generator/nested")
			self.createFile(".test_whitelist_generator/nested/m1.py")
			os.mkdir(".test_whitelist_generator/nested/a")
			os.mkdir(".test_whitelist_generator/nested/a/b")
			self.createFile(".test_whitelist_generator/nested/a/b/m2.py")
			self.createFile(".test_whitelist_generator/nested/a/b/m3.py")
			os.mkdir(".test_whitelist_generator/nested/c")
			self.createFile(".test_whitelist_generator/nested/c/m4.py")
			self.createFile(".test_whitelist_generator/nested/c/m5.py")
		except:
			if os.path.isdir(".test_whitelist_generator"):
				shutil.rmtree(".test_whitelist_generator")

	def tearDown(self):
		# Make sure test files are deleted
		if os.path.isdir(".test_whitelist_generator"):
			shutil.rmtree(".test_whitelist_generator")

	def test_getPackageName(self):
		# Test empty path
		with self.assertRaises(ValueError):
			self.whitelistGenerator.getPackageName("")
		# Test with invalid extension
		with self.assertRaises(ValueError):
			self.whitelistGenerator.getPackageName("package/test.txt")
		# Test valid paths
		self.assertEqual(self.whitelistGenerator.getPackageName("__init__.py"), "")
		self.assertEqual(self.whitelistGenerator.getPackageName("__main__.py"), "__main__")
		self.assertEqual(self.whitelistGenerator.getPackageName("test.py"), "test")
		self.assertEqual(self.whitelistGenerator.getPackageName("package"), "package")
		self.assertEqual(self.whitelistGenerator.getPackageName("package/subpackage"), "package.subpackage")
		self.assertEqual(self.whitelistGenerator.getPackageName("package/subpackage/__init__.py"), "package.subpackage")
		self.assertEqual(self.whitelistGenerator.getPackageName("package/subpackage/__main__.py"), "package.subpackage.__main__")
		self.assertEqual(self.whitelistGenerator.getPackageName("package/subpackage/submodule.py"), "package.subpackage.submodule")

	def test_generate(self):
		# Test with non-existent directory
		with self.assertRaises(IOError):
			self.whitelistGenerator.generate("__DIRECTORY_THAT_DOES_NOT_EXIST__")
		# Test with empty directory
		self.assertEqual( self.whitelistGenerator.generate(".test_whitelist_generator/empty"), [] )
		# Test with flat directory
		# NOTE: Converting to sets since order doesn't matter
		self.assertEqual( set(self.whitelistGenerator.generate(".test_whitelist_generator/flat")),
			set([ "flat.m1", "flat.m2", "flat.m3" ]) )
		# Test with nested directory
		self.assertEqual( set(self.whitelistGenerator.generate(".test_whitelist_generator/nested")),
			set([ "nested.a", "nested.c", "nested.a.b", "nested.m1", "nested.a.b.m2",
				  "nested.a.b.m3", "nested.c.m4", "nested.c.m5" ]) )


class TestWhitelistApplier(unittest.TestCase):

	def setUp(self):
		self.applier = WhitelistApplier()

	def tearDown(self):
		self.applier = None

	def test_inWhitelist(self):
		WHITELIST = [ "a", "b.c" ]
		# Test empty whitelist
		self.assertFalse( self.applier.inWhitelist("a", []) )
		# Test single-level module with a direct match in whitelist
		self.assertTrue( self.applier.inWhitelist("a", WHITELIST) )
		# Test nested module with a direct match in whitelist
		self.assertTrue( self.applier.inWhitelist("b.c", WHITELIST) )
		# Test nested module with an upper level match in whitelist
		self.assertTrue( self.applier.inWhitelist("b.c.d", WHITELIST) )
		# Test nested module one level too deep to match element in whitelist
		self.assertFalse( self.applier.inWhitelist("b.c.d.e", WHITELIST) )

	def test_applyToProject(self):
		PROJECT_PATH = "project"
		EXTERNAL_DEPENDENCIES = {
			"project.pack2.e" : set(["sys", "os"]),
			"sys" : set(["project.pack2.e"])
		}
		INPUT_DEPENDENCIES = {
			'project': set(['project.pack', 'sys', 'project.pack2', 'os.path']),
			'project.__main__': set(['project.a', 'project.pack.subpack2']),
			'project.a': set(['project.pack', 'project.a']),
			'project.pack.subpack2': set(['project.pack.subpack2.d',
			                       'project.pack.subpack2.subsubpack.c']),
			'project.pack.subpack2.d': set(['project.pack',
			                         'project.pack.subpack2.subsubpack.c',
			                         'project.pack2.e']),
			'project.pack.subpack2.subsubpack.c': set(),
			'project.pack2.e': set(['project.pack2.subpack.f']),
			'project.pack2.subpack.f': set(['project.pack2.e'])
		}
		EXPECTED_FILTERED_DEPENDENCIES = {
			'project': set(['project.pack', 'project.pack2']),
			'project.__main__': set(['project.a', 'project.pack.subpack2']),
			'project.a': set(['project.pack', 'project.a']),
			'project.pack.subpack2': set(['project.pack.subpack2.d',
			                       'project.pack.subpack2.subsubpack.c']),
			'project.pack.subpack2.d': set(['project.pack',
			                         'project.pack.subpack2.subsubpack.c',
			                         'project.pack2.e']),
			'project.pack.subpack2.subsubpack.c': set(),
			'project.pack2.e': set(['project.pack2.subpack.f']),
			'project.pack2.subpack.f': set(['project.pack2.e'])
 		}		

		# Test with invalid project path
		with self.assertRaises(IOError):
			self.applier.applyToProject("fherre8375848_not_a_valid_path", {})
		# Test with no dependencies given
		self.assertEqual( self.applier.applyToProject(PROJECT_PATH, {}), {})
		# Test with dependencies where NONE are in
		# the specified project, except for one dependant module
		self.assertEqual( self.applier.applyToProject(PROJECT_PATH,
			EXTERNAL_DEPENDENCIES), { "project.pack2.e" : set() })
		# Test dependencies where most are in given project
		self.assertEqual( self.applier.applyToProject(PROJECT_PATH,
			INPUT_DEPENDENCIES), EXPECTED_FILTERED_DEPENDENCIES)
