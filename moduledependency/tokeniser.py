"""Contains functionality for tokenising Python source code."""


import re


VALID_TOKEN_TYPES = (
	"identifier", "from", "import", ".", ",", "*", "other"
)
VALID_STRING_DELIMITERS = (
	"\'", "\"", "\'\'\'", "\"\"\""
)
END_OF_STRING_REGEX_PREFIX = r'[^\\]'
END_OF_STRING_REGEXES = {}
for delimeter in VALID_STRING_DELIMITERS:
	regexStr = END_OF_STRING_REGEX_PREFIX + delimeter
	END_OF_STRING_REGEXES[delimeter] = re.compile(regexStr)

class Token:

	"""Represents a single token."""

	def __init__(self, tokenType, value = None):
		"""Construct a new instance of Token.

		Arguments:
		tokenType -- String value dneoting the TYPE of the token.
					 If this string is not in VALID_TOKEN_TYPES,
					 then a ValueError is raised.

		Keyword arguments:
		value -- Value of the token (exact meaning depends on the
				 token's type). If not provided, then the token's
				 type also becomes its value. (default: None)

		"""
		if not tokenType in VALID_TOKEN_TYPES:
			raise ValueError("Invalid token type '{}' given".format(tokenType))

		self.type = tokenType
		if value:
			self.value = value
		else:
			self.value = self.type

	def __eq__(self, other):
		"""Return True if both instances of token have equivalent types and values.

		Arguments:
		other -- Instance of Token to compare with

		"""
		return (self.type == other.type and self.value == other.value)

	def __ne__(self, other):
		"""Return True if both instances of token do NOT have equivalent types and values.

		Arguments:
		other -- Instance of Token to compare with

		"""
		return (self.type != other.type or self.value != other.value)

	def __repr__(self):
		"""Return human-readable represetation of Token instance."""
		return str(self)

	def __str__(self):
		"""Return string representation of Token instance."""
		return "({}, {})".format(self.type, self.value)


class Tokeniser:

	"""Class used to tokenise textual Python source code.

	Note that the tokens returned do not represent full Python source
	code - it is merely a stripped down set of tokens intended
	to be used purely for identifying import dependencies.

	"""

	IDENTIFIER_REGEX = re.compile( r"[a-zA-Z_][a-zA-Z0-9_]*" )

	def __init__(self):
		"""Construct new instance of Tokeniser."""
		self.clear()

	def clear(self):
		"""Reset tokeniser's state, making it ready to tokenise another source."""
		self.tokens = []
		self.source = ""
		self.index = 0

	def currentChar(self):
		"""Return current character from source, or None if index is out of bounds."""
		if self.index < len(self.source):
			return self.source[self.index]
		else:
			return None

	def nextChar(self):
		"""Increment character index and returns the new character."""
		self.index += 1
		return self.currentChar()

	def tokenise(self, source):
		"""Return list of Token objects by tokensing Python source code.

		Arguments:
		source -- Python source code to tokenise

		"""
		if not isinstance(source, str):
			raise TypeError("Source to tokenise must be a string")

		self.clear()
		self.source = source

		# Maintain buffer which stores currently scanned token
		buff = []
		ch = self.currentChar() # get first character
		# Go through each character of source string
		while ch:
			if ch in (" ", "\n", "\t", "\r"): # ignore whitespace - breaks current token
				self.addTokenFromBuffer(buff)
			elif ch in VALID_STRING_DELIMITERS:
				self.addTokenFromBuffer(buff)
				# Perform a look-ahead by three characters to check
				# exactly which delimiter is being used
				start = self.index
				end = min(start + 3, len(self.source))
				full = self.source[start:end]
				# If the three characters represent a valid delimiter,
				# use that. If it's not, then just use the single character
				if full in VALID_STRING_DELIMITERS:
					self.skipString(full)	
				else:
					self.skipString(ch)
			elif ch == "#":
				self.addTokenFromBuffer(buff)
				self.skipComment()
			elif ch in (".", ",", "*"): # if character is operator we care about
				self.addTokenFromBuffer(buff)
				self.addToken(ch, ch)
			elif ch.isalnum() or ch == "_": # if character IS a word character (alphanumeric or "_")
				buff.append(ch)
			else: # if character is not a word character
				self.addTokenFromBuffer(buff)
				self.addToken("other", ch)

			# Get the next character
			ch = self.nextChar()

		# Dump whatever is remaining in the buffer to a token
		self.addTokenFromBuffer(buff)

		# Clear the token list for later tokenisations
		foundTokens = self.tokens
		self.clear()
		return foundTokens

	def addToken(self, tokenType, value):
		"""Add token to tokeniser's store.

		Arguments:
		tokenType -- Type the newly added token should have
		value -- Value the newly added token should have

		"""
		self.tokens.append( Token(tokenType, value) )

	def addTokenFromBuffer(self, buff):
		"""Look into contents of buffer and use it to construct a new token.

		If buffer is empty, nothing is done. Calling this clears the
		buffer afterwards.

		Arguments:
		buff -- List containing all the characters currently in the
				token buffer

		"""
		# If buffer is empty, we don't bother adding it as a token
		if len(buff) == 0:
			return

		# Get contents of buffer as a string
		bufferStr = "".join(buff)
		# Check if buffer is a keyword we care about
		if bufferStr == "from":
			self.tokens.append( Token("from") )
		elif bufferStr == "import":
			self.tokens.append( Token("import") )
		else:
			# Check if buffer is a valid identifier.
			if self.IDENTIFIER_REGEX.search(bufferStr):
				tokenType = "identifier"
			else:
				tokenType = "other"
			# Add token with the found type and make sure to clear the buffer
			self.tokens.append( Token(tokenType, bufferStr) )
		# Clear buffer
		del buff[:]

	def skipComment(self):
		"""Skip characters until end of comment (newline) is found.

		Assumes current character is a "#". Ends on newline chararacter
		or end of source.

		"""
		ch = self.nextChar()
		while ch and ch != "\n":
			ch = self.nextChar()

	def skipString(self, startingChar):
		"""Skip characters until end of string literal is found.

		Assumes current character is the LAST character of the
		starting string literal. Ends on the LAST character
		of the closing string delimiter or end of source.

		Arguments:
		startingChar -- The quote character(s) that started
						the literal. Used to determine when
						the literal ends. ValueError is
						raised if this is not a valid string
						delimiter.

		"""
		if not startingChar in VALID_STRING_DELIMITERS:
			raise ValueError("{} is not a valid string delimiter".format(startingChar))

		# Find first occurrence of required string delimeter
		# from the remaining string, wheere it DOES NOT precede
		# with an escapet character (\)
		remainingString = self.source[(self.index + 1):]
		match = END_OF_STRING_REGEXES[startingChar].search(remainingString)

		if match:
			self.index += match.end()
		# If an occurrence was not found, we've reached the end of the string	
		else:
			self.index = len(self.source)