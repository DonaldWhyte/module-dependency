import unittest
import sys
import os
import platform
import shutil

sys.path.append(os.environ.get("PROJECT_ROOT_DIRECTORY", "."))
from moduledependency.dependency_extractor import ModuleDependencyExtractor, WhitelistGenerator
from moduledependency.parser import ParsedImport


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

	def test_belongsTo(self):
		# Test with empty package name (should always return True)
		self.assertTrue( self.extractorNoWhitelist.belongsTo("", "") )
		self.assertTrue( self.extractorNoWhitelist.belongsTo("", "foo.bar") )
		# Test with empty module name
		self.assertFalse( self.extractorNoWhitelist.belongsTo("foo", "") )
		# Test with modules that DON'T belong to package
		self.assertFalse( self.extractorNoWhitelist.belongsTo("foo", "sys.path") )
		self.assertFalse( self.extractorNoWhitelist.belongsTo("something", "another_thing") )
		self.assertFalse( self.extractorNoWhitelist.belongsTo("foo.bar", "foo.haha") )
		# Test with modules that DO belong to package
		self.assertTrue( self.extractorNoWhitelist.belongsTo("foo", "foo") )
		self.assertTrue( self.extractorNoWhitelist.belongsTo("foo.bar", "foo.bar") )
		self.assertTrue( self.extractorNoWhitelist.belongsTo("foo", "foo.haha") )
		self.assertTrue( self.extractorNoWhitelist.belongsTo("foo.bar", "foo.bar.foobar") )

	def test_packageHasComponent(self):
		# Test empty values
		self.assertTrue( self.extractorNoWhitelist.packageHasComponent("", "") )
		self.assertFalse( self.extractorNoWhitelist.packageHasComponent("somePackage", "") )
		self.assertFalse( self.extractorNoWhitelist.packageHasComponent("", "someModule") )
		# Test components that do NOT belong to package
		self.assertFalse( self.extractorNoWhitelist.packageHasComponent("foo", "bar") )
		self.assertFalse( self.extractorNoWhitelist.packageHasComponent("foo.bar", "foobar") )
		self.assertFalse( self.extractorNoWhitelist.packageHasComponent("foo.bar.baz.hahaha.something_else", "not_there") )
		# Test components that do belong to package
		self.assertTrue( self.extractorNoWhitelist.packageHasComponent("foo", "foo") )
		self.assertTrue( self.extractorNoWhitelist.packageHasComponent("foo.bar", "foo") )
		self.assertTrue( self.extractorNoWhitelist.packageHasComponent("foo.bar", "bar") )
		self.assertTrue( self.extractorNoWhitelist.packageHasComponent("foo.bar.baz.hahaha.something_else", "hahaha") )

	def test_inWhitelist(self):
		testExtractor = ModuleDependencyExtractor( ["sys", "test.allowed", "rootPackage.hello.something"] )

		# Test with invalid types
		with self.assertRaises(AttributeError):
			self.extractorWithWhitelist.inWhitelist({})
		# Test with modules that aren't in wthe whitelist
		self.assertFalse( testExtractor.inWhitelist( ParsedImport("test.stuff", False) ) ) # absolute
		self.assertFalse( testExtractor.inWhitelist( ParsedImport("really_not_in_list", True) ) ) # relative
		# Test with modules that ARE in whitelist
		# absolute where name is FULL match
		self.assertTrue( testExtractor.inWhitelist( ParsedImport("sys", False) ) )
		# absolute where names are PARTIAL matches
		self.assertTrue( testExtractor.inWhitelist( ParsedImport("sys.path", False) ) )
		self.assertTrue( testExtractor.inWhitelist( ParsedImport("test.allowed.yes", False) ) )
		# relative where name is FULL match
		self.assertTrue( testExtractor.inWhitelist( ParsedImport("test.allowed", True) ) ) # "from .test import allowed"
		# relative where names are PARTIAL matches
		self.assertTrue( testExtractor.inWhitelist( ParsedImport(".something", True) ) ) # "from . import something"
		self.assertTrue( testExtractor.inWhitelist( ParsedImport("test.allowed.yes", True) ) ) # "from .test.allowed import yes"

		# Ensuring partial matches at module NAME level are not allowed
		self.assertFalse( testExtractor.inWhitelist( ParsedImport(".some", True) ) ) # "from . import something"

	def test_applyWhitelist(self):
		DISALLOWED_DEPDENDENCIES = set([
			ParsedImport("aha", False),
			ParsedImport("sys.path", False),
			ParsedImport("not_allowed.test", True),
			ParsedImport("iles", True)
		])
		ALLOWED_DEPENDENCIES = set([
			ParsedImport("a", False),
			ParsedImport("b", False),
			ParsedImport("c.d", True)
		])
		ALL_DEPENDENCIES = ALLOWED_DEPENDENCIES.union(DISALLOWED_DEPDENDENCIES)

		# Test not using whitelist
		self.assertEqual(self.extractorNoWhitelist.applyWhitelist(ALL_DEPENDENCIES), ALL_DEPENDENCIES)
		# Test empty dependency set
		self.assertEqual(self.extractorWithWhitelist.applyWhitelist(set()), set())
		# Test dependencies that are NOT in the whitelist
		self.assertEqual(self.extractorWithWhitelist.applyWhitelist(DISALLOWED_DEPDENDENCIES), set())
		# Test dependencies where some are allowed
		self.assertEqual(self.extractorWithWhitelist.applyWhitelist(ALL_DEPENDENCIES), ALLOWED_DEPENDENCIES)

	def test_extract(self):
		EXPECTED_WITH_WHITELIST = [
			ParsedImport("a", False), ParsedImport("a.b", False), ParsedImport("c", False),
			ParsedImport("d.e", False), ParsedImport("d.f", False), ParsedImport("g", False),
			ParsedImport(".h", True), ParsedImport(".i", True), ParsedImport(".j", True),
			ParsedImport("k.l", True), ParsedImport("m", True), ParsedImport("n.o.p", True),
			ParsedImport("q", True)
		]
		EXPECTED_WITHOUT_WHITELIST = list(EXPECTED_WITH_WHITELIST)
		EXPECTED_WITHOUT_WHITELIST += [
			ParsedImport("sys.path", False), ParsedImport("bang", False) ]
		
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
			set([ ParsedImport("hashlib", False),
				ParsedImport("blocked_module.initialise", False), ParsedImport("os.path.abspath", False) ]))
		self.assertEqual(self.extractorWithWhitelist.extract("files/blocked_dependencies.py"), set())
		# Test with file that has some standard library (not in whitelist) and
		# internal module dependencies
		self.assertEqual(self.extractorNoWhitelist.extract("files/some_dependencies.py"),
			set(EXPECTED_WITHOUT_WHITELIST)) # should have blocked modules in too!!!
		self.assertEqual(self.extractorWithWhitelist.extract("files/some_dependencies.py"),
			set(EXPECTED_WITH_WHITELIST))


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