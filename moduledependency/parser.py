# TODO: add docstrings to this
import hashlib


class ParseError(ValueError):

	def __init__(self, *args):
		super().__init__(*args)


class ParsedImport:

	def __init__(self, moduleName, relative):
		self.moduleName = moduleName
		self.relative = relative

	def isRelative(self):
		return self.relative

	def __repr__(self):
		return str(self)

	def __str__(self):
		if self.isRelative():
			importTypeStr = "relative"
		else:
			importTypeStr = "absolute"
		return "({}, {})".format(self.moduleName, importTypeStr)

	def __eq__(self, other):
		return (self.moduleName == other.moduleName and self.relative == other.relative)

	def __ne__(self, other):
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

	def __init__(self):
		self.clear()

	def clear(self):
		self.foundImports = set()
		self.tokens = []
		self.index = 0

	def currentToken(self):
		if self.index < len(self.tokens):
			return self.tokens[self.index]
		else:
			return None

	def nextToken(self):
		self.index += 1
		return self.currentToken()

	def addImport(self, moduleName, isRelative):
		self.foundImports.add( ParsedImport(moduleName, isRelative) )

	def parse(self, tokens):
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

	def parseImport(self):
		"""Parse an absolute import."""
		#print("Parsing import statement...")
		# Skip "import" keyword
		self.nextToken()
		# Get the full name of the module being imported
		moduleName = self.parseDottedIdentifier()
		# Now construct the full module name and add the import
		# as one that was found by the parser
		self.addImport(moduleName, False)

		#print("...done parsing import statement.")

	def parseFrom(self):
		"""Parse "from" import statements.

		TODO: mention the fact no '.' exists at start of module UNLESS
		root is current package level and not a root module"""
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
			rootModuleName = self.parseDottedIdentifier()
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

		#print("...done parsing from statement")

	def parseImportedObjects(self):
		"""Parse series of dotted identifiers separated by commas.

		Return list of strings containing those dotted identifiers.

		"""
		#print("Parsing imported objects...")
		importedObjects = []
		importedObjects.append( self.parseDottedIdentifier() )
		token = self.currentToken()
		while self.currentToken() and self.currentToken().type == ",":
			self.nextToken() # skip comma operator
			importedObjects.append( self.parseDottedIdentifier() )

		#print("...done parsing imported objects.")

		return importedObjects

	def parseDottedIdentifier(self):
		"""Parse a series of identifiers separated with the "." operator.

		Returns this series of identifiers as a string. If no valid
		identifier could be found immediately, then None is returned.

		"""
		#print("Parsing dotted identifier...")
		token = self.currentToken()
		if not token:
			raise ParseError("Unexpected end of tokens")
		# Check straight away if the next token is the "all" wildcard.
		# if it is, just return "*" as the identifier
		elif token.type == "*":
			self.nextToken()
			return "*"
		# Also check if the first token is an identifier. A valid
		# dootted identifier must START with an "identifier" token
		elif token.type != "identifier":
			raise ParseError("Dotted identifier must start with an identifier token")

		name = ""
		lookingForDot = False
		while True:
			if lookingForDot:
				if not token: # if end of tokens has been reached
					break
				elif token.type == "identifier":
					break # this is valid - just means it's the end of the current dotted identifier
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