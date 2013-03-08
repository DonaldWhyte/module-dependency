import unittest
import sys
import os
sys.path.append(os.environ.get("PROJECT_ROOT_DIRECTORY", "."))

from moduledependency.tokeniser import Token
from moduledependency.parser import ImportParser, ParsedImport, ParseError


class TestImport(unittest.TestCase):

	def test_construction(self):
		# Test relative import
		importObj = ParsedImport("hello", True)
		self.assertEqual(importObj.moduleName, "hello")
		self.assertTrue( importObj.isRelative() )
		# Test absolute import
		importObj = ParsedImport("byebye", False)
		self.assertEqual(importObj.moduleName, "byebye")
		self.assertFalse( importObj.isRelative() )


class TestImportParser(unittest.TestCase):

	def setUp(self):
		self.parser = ImportParser()
		self.noImportTokens = [
			Token("identifier", "def"), Token("identifier", "testFunction"),
			Token("other", "("), Token("identifier", "x"), Token("other", ")"), Token("other", ":"),
			Token("identifier", "return"), Token("identifier", "x"),
			Token("*"), Token("other", "2"), Token("identifier", "something"),
			Token("other", "="), Token("other", "["), Token("other", "\""),
			Token("identifier", "hello"), Token("other", "\""), Token("other", "]")
			# TODO: add osme invalid stuff in here
		]
		self.invalidImportTokens = [
			Token("from"), Token("identifier", "g"), Token("import"), Token("identifier", "dummy"), Token(","), Token("*"),

			Token("from"), Token("."), Token("import"), Token("identifier", "h"),
			Token("from"), Token("."), Token("import"), Token("identifier", "i"), Token(","), Token("identifier", "j"),
			Token("from"), Token("."), Token("identifier", "k"), Token("import"), Token("identifier", "l"),
			Token("from"), Token("."), Token("identifier", "m"), Token("import"), Token("*"),
			Token("from"), Token("."), Token("identifier", "n"), Token("import")
		]
		self.validImportTokens = [
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
		self.foundImports = [
			ParsedImport("a", False), ParsedImport("a.b", False), ParsedImport("c", False),
			ParsedImport("d.e", False), ParsedImport("d.f", False), ParsedImport("g", False),
			ParsedImport("h", True), ParsedImport("i", True), ParsedImport("j", True),
			ParsedImport("k.l", True), ParsedImport("m", True), ParsedImport("n.o.p", True),
			ParsedImport("q", True),
			ParsedImport("sys.path", False), ParsedImport("bang", False),

			ParsedImport("moduleName", False), ParsedImport("this)_a_modue", True)


		]

	def tearDown(self):
		self.parser = None
		self.invalidImportTokens = None
		self.validImportTokens = None
		self.foundImports = None

	def test_parse(self):
		# Test with no tokens
		self.assertEqual(self.parser.parse([]), [])
		self.assertEqual(self.parser.parse(self.noImportTokens), [])
		# Test with incorrectly formed imports
		with self.assertRaises(ParseError):
			self.assertEqual(self.parser.parse(self.invalidImportTokens), [])
		# Test with valid imports
		self.assertEqual(self.parser.parse(self.validImportTokens), self.foundImports)

	"""def test_parseDottedIdentifier(self):
		invalidIdentifierTokens1 = [ Token("other", "(") ]
		invalidIdentifierTokens2 = [ Token(".") ]
		invalidIdentifierTokens3 = [ Token("identifier", "invalid"), Token(".") ]
		invalidIdentifierTokens4 = [ Token("identifier", "invalid"), Token("."), Token(".") ]
		validIdentifierTokens1 = [ Token("identifier", "test") ]
		validIdentifierTokens2 = [ Token("identifier", "test"), Token("."), Token("identifier", "anotherTest") ]
		validIdentifierTokens3 = [ Token("identifier", "test"), Token("."), Token("identifier", "anotherTest"), Token("."), Token("identifier", "ultimateNesting") ]
		validIdentifierTokens4 = [ Token("identifier", "test"), Token("identifier", "endOfSameIdentifier") ]
		validIdentifierTokens5 = [ Token("identifier", "test"), Token("."), Token("identifier", "anotherTest"), Token("identifier", "endOfSameIdentifier")  ]

		# Test invalid identifier
		self.parser.tokens = invalidIdentifierTokens1
		with self.assertRaises(ParseError):
			self.parser.parseDottedIdentifier()
		self.parser.clear()		
		# Test invalid identifier due to just a dot
		self.parser.tokens = invalidIdentifierTokens2
		with self.assertRaises(ParseError):
			self.parser.parseDottedIdentifier()
		self.parser.clear()
		# Test invalid identifier due to trailing dot
		self.parser.tokens = invalidIdentifierTokens3
		with self.assertRaises(ParseError):
			self.parser.parseDottedIdentifier()
		self.parser.clear()
		# Test invalid identifier due to two dots being used in succession
		self.parser.tokens = invalidIdentifierTokens4
		with self.assertRaises(ParseError):
			self.parser.parseDottedIdentifier()
		self.parser.clear()
		# Test identifier without a dot
		self.parser.tokens = validIdentifierTokens1
		self.assertEqual(self.parser.parseDottedIdentifier(), "test")
		self.assertEqual(self.parser.index, 1)
		self.parser.clear()	
		# Test identifier with a dot
		self.parser.tokens = validIdentifierTokens2
		self.assertEqual(self.parser.parseDottedIdentifier(), "test.anotherTest")
		self.assertEqual(self.parser.index, 3)
		self.parser.clear()	
		# Test identifier with multiple dots
		self.parser.tokens = validIdentifierTokens3
		self.assertEqual(self.parser.parseDottedIdentifier(), "test.anotherTest.ultimateNesting")
		self.assertEqual(self.parser.index, 5)
		self.parser.clear()	
		# Test indeitifers where this is an identifier token at end,
		# which SHOULD break up the parsing of the identifier
		self.parser.tokens = validIdentifierTokens4
		self.assertEqual(self.parser.parseDottedIdentifier(), "test")
		self.assertEqual(self.parser.index, 1)
		self.parser.clear()	
		self.parser.tokens = validIdentifierTokens5
		self.assertEqual(self.parser.parseDottedIdentifier(), "test.anotherTest")
		self.assertEqual(self.parser.index, 3)
		self.parser.clear()	

	def test_parseImport(self):
		incorrectImportTokens1 = [ Token("import") ]
		incorrectImportTokens2 = [ Token("import"), Token("other", "(") ]
		correctImportTokens1 = [ Token("import"), Token("identifier", "someModule") ]
		correctImportTokens2 = [ Token("import"), Token("identifier", "somePackage"), Token("."), Token("identifier", "someModule") ]

		# Incorrectly formed imports
		self.parser.tokens = incorrectImportTokens1
		with self.assertRaises(ParseError):
			self.parser.parseImport()
		self.parser.clear()

		self.parser.tokens = incorrectImportTokens2
		with self.assertRaises(ParseError):
			self.parser.parseImport()
		self.parser.clear()

		# Correctly formed imports
		self.parser.tokens = correctImportTokens1
		self.parser.parseImport()
		self.assertEqual( self.parser.foundImports,
			[ParsedImport("someModule", False)] )
		# Check state of the parser to make sure the index
		# and current tokens are at the correct position
		self.assertEqual(self.parser.index, 2)
		self.parser.clear()

		self.parser.tokens = correctImportTokens2
		self.parser.parseImport()
		self.assertEqual( self.parser.foundImports,
			[ParsedImport("somePackage.someModule", False)] )
		self.assertEqual(self.parser.index, 4)
		self.parser.clear()

	def test_parseImportedObjects(self):
		# Test with incorrectly formed identifier
		self.parser.tokens = [ Token("identifier", "test"), Token("."), Token(".") ]
		with self.assertRaises(ParseError):
			self.parser.parseImportedObjects()
		self.parser.clear()
		# Test with an incorrectly formed indentifier in the middle
		self.parser.tokens = [ Token("identifier", "test"), Token(","), Token("identifier", "test2"), Token(","), Token("identifier", "test"), Token("."), Token("."), Token(","), Token("identifier", "test3") ]
		with self.assertRaises(ParseError):
			self.parser.parseImportedObjects()
		self.parser.clear()
		# Test with no tokens left
		self.parser.tokens = []
		with self.assertRaises(ParseError):
			self.parser.parseImportedObjects()
		self.parser.clear()
		# Test with trailing commas
		self.parser.tokens = [ Token("identifier", "test"), Token(","), Token("identifier", "test2"), Token(","), Token(",") ]
		with self.assertRaises(ParseError):
			self.parser.parseImportedObjects()
		self.parser.clear()

		# Test with a single identifier
		self.parser.tokens = [ Token("identifier", "one") ]
		self.assertEqual(self.parser.parseImportedObjects(), ["one"])
		self.assertEqual(self.parser.index, 1)
		self.parser.clear()	
		# Test with a single identifier
		self.parser.tokens = [ Token("identifier", "one"), Token("."), Token("identifier", "fifty") ]
		self.assertEqual(self.parser.parseImportedObjects(), ["one.fifty"])
		self.assertEqual(self.parser.index, 3)
		self.parser.clear()	
		# Test with two identifiers
		self.parser.tokens = Token("identifier", "one"), Token(","), Token("identifier", "two")
		self.assertEqual(self.parser.parseImportedObjects(), ["one", "two"])
		self.assertEqual(self.parser.index, 3)
		self.parser.clear()	
		# Test with more than two identifiers
		self.parser.tokens = [ Token("identifier", "one"), Token("."), Token("identifier", "fifty"),
			Token(","), Token("identifier", "two"), Token(","), Token("identifier", "three"),
			Token("."), Token("identifier", "eighty"), Token(","), Token("identifier", "four") ]
		self.assertEqual(self.parser.parseImportedObjects(), ["one.fifty", "two", "three.eighty", "four"])
		self.assertEqual(self.parser.index, 11)
		self.parser.clear()	
"""
	def test_parseFrom(self):
		pass
		# TODO

