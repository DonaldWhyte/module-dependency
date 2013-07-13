import unittest
import sys
import os
sys.path.append(os.environ.get("PROJECT_ROOT_DIRECTORY", "."))

from moduledependency.tokeniser import Token, Tokeniser


class TestToken(unittest.TestCase):

	def test_construction(self):#
		# Test with invalid token type
		with self.assertRaises(ValueError):
			Token("HAHAHAHAHA")
		# Test with valid token types (one with value and one without)
		token = Token("identifier", "testVariable")
		self.assertEqual(token.type, "identifier")
		self.assertEqual(token.value, "testVariable")
		token = Token("from")
		self.assertEqual(token.type, "from")
		self.assertEqual(token.value, "from")


class TestTokeniser(unittest.TestCase):

	def setUp(self):
		self.tokeniser = Tokeniser()
		# Create test data
		self.noImportSource = """
		def testFunction(x):
			\"\"\"This is a docstring but I'm not sure
			how far it goes.
			\"\"\"
			return x * 2
			\'\'\'Another multi
			line string\'\'\'

		'test'
		something = [ "hello" ]

		"""
		self.importSource = """#comment here
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
				# Hello World!
				from sys import path # test
				print(path)

			def somethingEntirelyDifferent():
				import bang
				bang.start()
		"""
		self.noImportTokens = [
			Token("identifier", "def"), Token("identifier", "testFunction"),
			Token("other", "("), Token("identifier", "x"), Token("other", ")"), Token("other", ":"),
			Token("identifier", "return"), Token("identifier", "x"),
			Token("*"), Token("other", "2"), Token("identifier", "something"),
			Token("other", "="), Token("other", "["), Token("other", "]"),
		]
		self.importTokens = [
			Token("import"), Token("identifier", "a"),
			Token("from"), Token("identifier", "a"), Token("import"), Token("identifier", "b"),
			Token("from"), Token("identifier", "c"), Token("import"), Token("*"),
			Token("from"), Token("identifier", "d"), Token("import"), Token("identifier", "e"), Token(","), Token("identifier", "f"),
			Token("from"), Token("identifier", "g"), Token("import"), Token("identifier", "dummy"), Token(","), Token("*"),

			Token("from"), Token("."), Token("import"), Token("identifier", "h"),
			Token("from"), Token("."), Token("import"), Token("identifier", "i"), Token(","), Token("identifier", "j"),
			Token("from"), Token("."), Token("identifier", "k"), Token("import"), Token("identifier", "l"),
			Token("from"), Token("."), Token("identifier", "m"), Token("import"), Token("*"),
			Token("from"), Token("."), Token("identifier", "n"), Token("import"), Token("identifier", "o"), Token("."), Token("identifier", "p"),
			Token("from"), Token("."), Token("identifier", "q"), Token("import"), Token("identifier", "another_dummy"), Token(","), Token("*"),

			Token("identifier", "class"), Token("identifier", "DummyClass"), Token("other", ":"),
			Token("identifier", "def"), Token("identifier", "something"), Token("other", "("), Token("other", ")"), Token("other", ":"),
			Token("from"), Token("identifier", "sys"), Token("import"), Token("identifier", "path"),
			Token("identifier", "print"), Token("other", "("), Token("identifier", "path"), Token("other", ")"),
			Token("identifier", "def"), Token("identifier", "somethingEntirelyDifferent"), Token("other", "("), Token("other", ")"), Token("other", ":"),
			Token("import"), Token("identifier", "bang"),
			Token("identifier", "bang"), Token("."), Token("identifier", "start"), Token("other", "("), Token("other", ")")
		]

	def tearDown(self):
		self.tokeniser = None
		self.noImportSource = None
		self.importSource = None
		self.noImportTokens = None
		self.importTokens = None

	def test_tokenise(self):
		# Test with invalid type
		with self.assertRaises(TypeError):
			self.tokeniser.tokenise(3636)
		# Test with empty Python source code
		self.assertEqual(self.tokeniser.tokenise(""), [])
		# Test with source code that has no imports
		self.assertEqual(self.tokeniser.tokenise(self.noImportSource), self.noImportTokens)
		# Test with source code that has imports
		self.assertEqual(self.tokeniser.tokenise(self.importSource), self.importTokens)
		# Test with source that ends STRAIGHT after import
		self.assertEqual(self.tokeniser.tokenise("from . import pack"),
			[ Token("from"), Token("."), Token("import"), Token("identifier", "pack") ])

	def test_skipComment(self):
		# First element of tuple is the index to start skipping from
		# and the second element is the desired end element
		TEST_SOURCE = """#comment at the start
		hello = 5 # comment at the end of a thing
		# # # # nestetd comment
		"""
		TEST_INDICES = [ (0, 21), (31, 65), (66, 91) ]
		for test in TEST_INDICES:
			self.tokeniser.clear()
			self.tokeniser.source = TEST_SOURCE
			self.tokeniser.index = test[0]
			self.tokeniser.skipComment()
			self.assertEqual(self.tokeniser.index, test[1])

	def test_skipString(self):
		# Contains tuples where the first element is the index of
		# the character the test should start at, the second
		# element is where the tokeniser should stop skipping and
		# the third element is the delimiter of the test string
		TEST_INDICES = [ 
			(31, 6, "\""),
			(49, 5, "\'"),
			(68, 20, "\"\"\""),
			(104, 34, "'''"),
			(152, 13, "\"")
		]
		# Set the source code that will be used for comment skipping
		TEST_SOURCE = """#comment at the start
		test = "hello"
		test2 = 'ello'
		test3 = \"\"\""hello"
		multiline\"\"\"
		test4 = '''can be multiline but 'test' isn't'''
		no_end=" ijruiytie
		"""
		for test in TEST_INDICES:
			self.tokeniser.clear()
			self.tokeniser.source = TEST_SOURCE
			self.tokeniser.index = test[0]
			self.tokeniser.skipString(test[2])
			self.assertEqual(self.tokeniser.index, test[0] + test[1])