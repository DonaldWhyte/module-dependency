import unittest
import sys
import os
sys.path.append(os.environ.get("PROJECT_ROOT_DIRECTORY", "."))

from moduledependency.import_resolver import ImportResolver
from moduledependency.parser import ParsedImport


class TestImportResolver(unittest.TestCase):

	def setUp(self):
		self.importResolver = ImportResolver("/some/root/dir")

	def test_construction(self):
		self.assertEqual(self.importResolver.rootDirectory, "/some/root/dir")

	def test_addRootToPackage(self):
		# Test with empty string for package (which would be root __init__ of project)
		self.assertEqual(self.importResolver.addRootToPackage(""), "dir")
		# Test with package name
		self.assertEqual(self.importResolver.addRootToPackage("test"), "dir.test")

	def test_getPackageName(self):
		INVALID_PATHS = [
			"/", "C:\\", "",
			"/package", "/package/module.py", "/package/module.txt", "/package/subpackage/module.py",
			"package", "package/module.py", "package/module.txt", "package/subpackage/module.py",
			"C:\\package", "C:\\package\\module.py", "C:\\package\\module.txt", "C:\\package\\subpackage\\module.py",
			"package", "package\\module.py", "package\\module.txt", "package\\subpackage\\module.py",

			"/some/root/dir" # still invalid since it's the root directory - empty module!
		]

		# Test non-string
		with self.assertRaises(TypeError):
			self.importResolver.getPackageName(4435)
		# Test invalid paths (not correct format)
		with self.assertRaises(ValueError):
			self.importResolver.getPackageName("  - -43-5-")
		with self.assertRaises(ValueError):
			self.importResolver.getPackageName("__I*930384095 0d-")
		# Test paths not in assigned root directory
		for path in INVALID_PATHS:
			with self.assertRaises(ValueError):
				self.importResolver.getPackageName(path)
		# Test valid paths (with different path separators)
		self.assertEqual(self.importResolver.getPackageName("/some/root/dir/package"), "package")
		self.assertEqual(self.importResolver.getPackageName("/some/root/dir/package/module.py"), "package.module")
		self.assertEqual(self.importResolver.getPackageName("/some/root/dir/package/module.txt"), "package.module")
		self.assertEqual(self.importResolver.getPackageName("/some/root/dir/package/subpackage/"), "package.subpackage")
		self.assertEqual(self.importResolver.getPackageName("/some/root/dir/package/subpackage/module.py"), "package.subpackage.module")
		# Test with __main__.py and __init__.py files
		self.assertEqual(self.importResolver.getPackageName("/some/root/dir/package/__init__.py"), "package.__init__")
		self.assertEqual(self.importResolver.getPackageName("/some/root/dir/package/__main__.py"), "package.__main__")

	def test_resolveImport(self):
		# Test with incorrect types
		with self.assertRaises(AttributeError):
			self.importResolver.resolveImport("", 4553)
		with self.assertRaises(AttributeError):
			self.importResolver.resolveImport("", {})
		with self.assertRaises(TypeError):
			self.importResolver.resolveImport(24532, ParsedImport("test", True))
		# Test with non-relative import
		with self.assertRaises(ValueError):
			self.importResolver.resolveImport( "", ParsedImport("test", False) )
		# Test with relative import where there is NO root
		self.assertEqual( self.importResolver.resolveImport("/some/root/dir/another.py", ParsedImport(".test", True)), "dir.test" )
		# Test with valid relative imports where there is a root
		self.assertEqual( self.importResolver.resolveImport("/some/root/dir/package/something.py",
			ParsedImport(".test", True)), "dir.package.test" )
		self.assertEqual( self.importResolver.resolveImport("/some/root/dir/package/__init__.py",
			ParsedImport(".test", True)), "dir.package.test" )
		self.assertEqual( self.importResolver.resolveImport("/some/root/dir/package/subpackage/files.py",
			ParsedImport("something.nested", True)), "dir.package.subpackage.something.nested" )
		# Test out of bounds upper level import
		with self.assertRaises(ValueError):
			self.importResolver.resolveImport("/some/root/dir/package/test.py", ParsedImport("...a", True))
		# Test valid upper level imports
		self.assertEqual(self.importResolver.resolveImport("/some/root/dir/package/test.py",
			ParsedImport("..a", True)), "dir.a")
		self.assertEqual(self.importResolver.resolveImport("/some/root/dir/package/test/test2/test3/nested.py",
			ParsedImport("....fromnested.foobar", True)), "dir.package.fromnested.foobar")

	def test_resolveImports(self):
		INVALID_INPUT_DEPENDENCIES = {
			"/some/root/dir/package" : set(),
			"/not/in/assigned/root.py" : set()
		}
		INPUT_DEPENDENCIES = {
			"/some/root/dir/__init__.py" : set([]),
			"/some/root/dir/setup.py" : set([ParsedImport("distutils", False)]),
			"/some/root/dir/package" : set([
				ParsedImport("sys", False),
				ParsedImport("os.path", False)
			]),
			"/some/root/dir/package/module.py" : set([
				ParsedImport("haslib.sha1", False),
				ParsedImport("test", True),
				ParsedImport("something.nested.even_more.module", True)
			]),
			"/some/root/dir/package/subpackage/__init__.py" : set([
				ParsedImport(".hello", True)
			]),
			"/some/root/dir/package/subpackage/module.py" : set([
				ParsedImport("hello.byebye", True),
				ParsedImport("y.x", True),
				ParsedImport(".z", True),
				ParsedImport("z", False)
			])
		}
		RESOLVED_DEPENDENCIES = {
			"dir" : set(),
			"dir.setup" : set(["distutils"]),
			"dir.package" : set(["sys", "os.path"]),
			"dir.package.module" : set(["haslib.sha1", "dir.package.test", "dir.package.something.nested.even_more.module"]),
			"dir.package.subpackage" : set(["dir.package.subpackage.hello"]),
			"dir.package.subpackage.module" : set([
				"dir.package.subpackage.hello.byebye", "dir.package.subpackage.y.x",
				"dir.package.subpackage.z", "z"])
		}

		# Test with non-iterable
		with self.assertRaises(TypeError):
			self.importResolver.resolveImports(35335)
		# Test with empty dependency dictionary
		self.assertEqual(self.importResolver.resolveImports({}), {})
		# Test with dependency dictonary where ne of the files is
		# NOT in the root directory
		with self.assertRaises(ValueError):
			self.importResolver.resolveImports(INVALID_INPUT_DEPENDENCIES)
		# Test with filled dependency dicitonary
		self.assertEqual(self.importResolver.resolveImports(INPUT_DEPENDENCIES), RESOLVED_DEPENDENCIES)
