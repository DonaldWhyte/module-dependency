import sys
sys.path.append("../../fileprocessor") # TODO: remove
import re
from collections import Iterable
from fileprocessor.extractors import TextExtractor

class ModuleDependencyExtractor(TextExtractor):

	# Pre-compiled regexes for finding module imports
	IMPORT_REGEX = re.compile( r"import ([\w\.]+?)[^\w\.]" )
	FROM_IMPORT_REGEX = re.compile( r"from ([\w\.]+?) import ((([\w\.]+?)[^\w\.])|\*)" )

	def __init__(self, whitelist = None):
		if whitelist != None and not isinstance(whitelist, Iterable):
			raise TypeError("Whitelist must be an iterable collection of strings")
		self.whitelist = whitelist				

	def usingWhitelist(self):
		return (self.whitelist != None)

	def filterModules(self, modules):
		# NOTE: modules list is modified in place

		# TODO: might have to be more intelligent here. For example, if
		# "foo.bar" is not in whitelist, but "foo" is, "foo.bar" should
		# be allowed! So we check the "highest level" module from the
		i = 0
		while i < len(modules):
			# Get name of each level of the module (e.g. "foo.bar" is ["foo", "bar"])
			moduleLevels = modules[i].split(".")
			# Go through module levels, checking if they're in the
			# whitelist. Start from the highest level
			allowed = False
			for i in range(len(moduleLevels)):
				# Only combine module levels for the current level
				trimmedModuleLevels = moduleLevels[:i]
				# If this module level is in the whitelist, set a
				# flag and break from the loop
				if ".".join(trimmedModuleLevels) in self.whitelist:
					allowed = True
					break
			# If one of the module levels was in the whitelist,
			# simply move to the next module. Otherwise, delete the
			# the module!
			if allowed:
				i += 1
			else:
				del modules[i]

	def extractFromString(self, data):
		# Search code for any import statements and add each match as a
		# dependency of this source file
		foundDependencies = set()
		for match in self.IMPORT_REGEX.finditer(data):
			foundDependencies.add(match.group(1))
		for match in self.FROM_IMPORT_REGEX.finditer(data):
			fullModuleName = "{}.{}".format(match.group(1), match.group(2))
			# Get rid of any extra whitespace regex may have caused
			fullModuleName = fullModuleName.strip()
			# If ends with "*", we just use the package name as the dependency
			if fullModuleName.endswith("*"):
				fullModuleName = fullModuleName[:-2]
			foundDependencies.add(fullModuleName)

		# Add higher-level modules of dependencies too
		higherLevelDependencies = set()
		for dependency in foundDependencies:
			levels = dependency.split(".")
			for i in range(len(levels)):
				fullLevelName = ".".join(levels[:i])
				higherLevelDependencies.add(fullLevelName)
		foundDependencies = foundDependencies.union(higherLevelDependencies)

		# Filter the dependencies so only modules in this project are present.
		# Only do this if a whitelist was provided though
		print(foundDependencies)
		if self.usingWhitelist():
			self.filterModules(foundDependencies)

		# Convert list of found dependencies to set to ensure there is no duplication
		return foundDependencies