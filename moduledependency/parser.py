"""Contains functionality for parsing tokens to identify module imports and dependencies."""

import hashlib

class ParseError(ValueError):

	"""Exception class raised if an error in parsing occurs."""

	def __init__(self, *args):
		"""Construct instance of ParseError.

		Arguments:
		args -- Any arguments that can be passed to ValueError
				can be provided.

		"""
		super().__init__(*args)

class ParsedImport:

	"""Class represents a single import made a module."""

	def __init__(self, moduleName, relative):
		"""Construct instance of ParsedImport.

		Arguments:
		moduleName -- name of the module/identifier being imported
					  Packages and modules should be separated with
					  ".". "." should also be at the start of the
					  name ONLY IF the import is relative with no
					  root package (e.g. "from . import x" is ".x"
					  but "from .y import x" is "y.x").
		relative -- Boolean flag indicating if the import is relative
					to the importing module's location or if it's
					an absolute import.

		"""
		self.moduleName = moduleName
		self.relative = relative

	def isRelative(self):
		"""Return True if the import is relative to current module."""
		return self.relative

	def __repr__(self):
		"""Return human-readable representation of object."""
		return str(self)

	def __str__(self):
		"""Return string representation of object."""
		if self.isRelative():
			importTypeStr = "relative"
		else:
			importTypeStr = "absolute"
		return "({}, {})".format(self.moduleName, importTypeStr)

	def __eq__(self, other):
		"""Overload of equality operator for comparing imports."""
		return (self.moduleName == other.moduleName and self.relative == other.relative)

	def __ne__(self, other):
		"""Overload of inequality operator for comparing imports."""
		return (self.moduleName != other.moduleName or self.relative != other.relative)

	def __hash__(self):
		"""Return SHA-1 hash of this object.

		Done so ParsedImport objects can be stored in sets."""
		
		# Convert object to series of bytes (string for name and byte for relative flag)
		data = bytearray(self.moduleName, encoding="utf-8")
		if self.relative:
			data.append(1)
		else:
			data.append(0)
		# Hash the raw byte data
		hasher = hashlib.sha1()
		hasher.update(data)
		return int.from_bytes( hasher.digest(), byteorder="little" )


class ImportParser:

	"""Class used to find imports made in Pytho source code.

	Uses a list of tokens (instances of Token class) made from
	Python source code to find these imports.

	"""

	def __init__(self):
		"""Construct instance of ImportParser."""
		self.clear()

	def clear(self):
		"""Clear parser state to make it ready for parsing another token stream."""
		self.foundImports = set()
		self.tokens = []
		self.index = 0

	def currentToken(self):
		"""Return current token.

		If end of token stream has been reached, then
		None will be returned.

		"""
		if self.index < len(self.tokens):
			return self.tokens[self.index]
		else:
			return None

	def nextToken(self):
		"""Move parser to next token."""
		self.index += 1
		return self.currentToken()

	def addImport(self, moduleName, isRelative):
		"""Add found import to the list maintained by the parser class.

		Arguments:
		moduleName -- name of the module/identifier being imported
					  Packages and modules should be separated with
					  ".". "." should also be at the start of the
					  name ONLY IF the import is relative with no
					  root package (e.g. "from . import x" is ".x"
					  but "from .y import x" is "y.x").
		relative -- Boolean flag indicating if the import is relative
					to the importing module's location or if it's
					an absolute import.

		"""
		self.foundImports.add( ParsedImport(moduleName, isRelative) )

	def parseImport(self):
		"""Parse an absolute import."""
		# Skip "import" keyword
		self.nextToken()
		# Get the full name of the module being imported
		moduleName = self.parseDottedIdentifier()
		# Now construct the full module name and add the import
		# as one that was found by the parser
		self.addImport(moduleName, False)

	def parseFrom(self):
		"""Parse "from" import statements."""
		searchForRootModule = True

		# Determine if the from statement is absolute or relative.
		# If it's relative, then the otken straight after the
		# "from" keyword should be a ".".
		token = self.nextToken()
		if not token:
			raise ParseError("Unexpected end of tokens")
		elif token.type == ".":
			isRelative = True
			# Skip the "." and move to root package/module name
			token = self.nextToken()
			# Now check if there is an "import" token. It's valid
			# to just have a "." before "import" in a "from statement"
			if token.type == "import":
				searchForRootModule = False
		else:
			isRelative = False

		# Find the ROOT module name if root is not "."
		if searchForRootModule:
			rootModuleName = self.parseDottedIdentifier(True)
			if not rootModuleName:
				raise ParseError("Module identifier should follow a 'from' keyword")
		else:
			rootModuleName = ""
		# The next token should now be an "import" token
		token = self.currentToken()
		if not token:
			raise ParseError("Unexpected end of tokens")
		elif token.type != "import":
			raise ParseError("'import' keyword should follow root moudle name in 'from' import statement: " + str(token))		
		# Now get the name of all the objects
		self.nextToken() # skip the import tag
		importedObjects = self.parseImportedObjects()

		# If there were no objects imported using the 'from' satement
		# then the statement is a syntax error so the parse will fail
		if len(importedObjects) == 0:
			raise ParseError("Poorly formed 'from' statement never imported any objects: " + str(token))
		# If the wildcard "all" was found in the list of imported objects,
		# the it overrides the other imported obects and the entire root
		# module was imported
		if "*" in importedObjects:
			self.addImport(rootModuleName, isRelative)
		# Add a found module for each of the imported objects
		else:
			for obj in importedObjects:
				fullModuleName = "{}.{}".format(rootModuleName, obj)
				self.addImport(fullModuleName, isRelative)

	def parseImportedObjects(self):
		"""Parse series of dotted identifiers separated by commas.

		Returns list of strings containing those dotted identifiers.

		"""
		importedObjects = []
		importedObjects.append( self.parseDottedIdentifier() )
		while self.currentToken() and self.currentToken().type == ",":
			self.nextToken() # skip comma operator
			importedObjects.append( self.parseDottedIdentifier() )

		return importedObjects

	def parseDottedIdentifier(self, allowStartingDots = False):
		"""Parse a series of identifiers separated with the "." operator.

		Returns this series of identifiers as a string. If no valid
		identifier could be found immediately, then None is returned.

		Keyword arguments:
		allowStartingDots -- If set to True, then a ParseError will NOT
							be raised if the identifier starts with one
							or more dot characters.

		"""
		# Stores complete dotted identifier
		name = ""

		token = self.currentToken()
		if not token:
			raise ParseError("Unexpected end of tokens")
		# Check straight away if the next token is the "all" wildcard.
		# if it is, just return "*" as the identifier
		elif token.type == "*":
			self.nextToken()
			return "*"
		# If identifier starts with a dot character and it's allowed,
		# go through all the dots and add them to the final name
		elif token.type == "." and allowStartingDots:
			while token and token.type == ".":
				name += "."
				token = self.nextToken()
			# If end of token steam has already been reached, just
			# return the parsed dots
			if not token:
				return name
		# Also check if the first token is an identifier. A valid
		# dootted identifier must START with an "identifier" token
		elif token.type != "identifier":
			raise ParseError("Dotted identifier must start with an identifier token")

		# Parse identifier
		lookingForDot = False
		while True:
			if lookingForDot:
				if not token: # if end of tokens has been reached
					break
				elif token.type == ".":
					name += "."
					lookingForDot = False
				else:
					break
			else:
				if not token:
					raise ParseError("Unexpected end of tokens - trailing dot operator")
				elif token.type == "identifier":
					name += token.value
					lookingForDot = True
				elif token.type == ".":
					raise ParseError("Invalid identifier - two consecutive dot operators present")
				else: # end parsing dotted identifier
					break

			token = self.nextToken()

		if name == "":
			return None
		else:
			return name

	def parse(self, tokens):
		"""Return list of found imports by parsing a list of tokens.

		Arguments:
		tokens -- A list of Token instances.

		"""
		# If no tokens were given, don't bother trying to parse
		if len(tokens) == 0:
			return set()

		self.clear()
		self.tokens = tokens
		# While we have not reached the end of the token list
		while self.currentToken():
			token = self.currentToken()
			if token.type == "import":
				self.parseImport()
			elif token.type == "from":
				self.parseFrom()
			# Only go to next token if another parsing method was not called
			else:
				self.nextToken()

		temp = self.foundImports
		self.clear()

		return temp