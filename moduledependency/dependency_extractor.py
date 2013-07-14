"""Contains functionalty to identify dependencies in Python source code."""

import os.path
import re
from collections import Iterable

from fileprocessor.extractors import TextExtractor
from .tokeniser import Tokeniser
from .parser import ImportParser, ParsedImport
from . import util

class ModuleDependencyExtractor(TextExtractor):

	def __init__(self, whitelist = None):
		"""Create new instance of ModuleDependencyExtractor.

		Keyword arguments:
		whitelist -- List of strings denoting the names of packages
					 or modules that are allowed. If not provided,
					 no whitelist will be used to filter results.
					 (default: None)

		"""
		if whitelist != None and not isinstance(whitelist, Iterable):
			raise TypeError("Whitelist must be an iterable collection of strings")
		self.whitelist = whitelist				

		self.tokeniser = Tokeniser()
		self.parser = ImportParser()

	def usingWhitelist(self):
		"""Return True if this extractor is using a whitelist to filter depedencies."""
		return (self.whitelist != None)

	def belongsTo(self, package, module):
		"""Check if module belongs to package based on their full names.

		Returns True if module belongs to package and False otherwise.
		If package name is empty (""), then True is always returned.
		If module name is empty (""), then False is always returned
		unless the package name is also empty.

		Example:
		belongsTo("packageA.foo", "packageA.foo.bar") = True
		belongsTo("packageA.foo", "foo") = False

		Arguments:
		package -- Full name of package
		module -- Full name of module

		"""
		if len(package) == 0:
			return True
		if len(module) == 0:
			return False
		packageComponents = package.split(".")
		moduleComponents = module.split(".")
		# If there are more components in the package, then it's not
		# possible for the module to belong to the package
		if len(packageComponents) > len(moduleComponents):
			return False
		# Now get a sub list of the module components and compare it with
		# the package components. If they're equal, then that means the
		# module belongs to the package.
		return (packageComponents == moduleComponents[:len(packageComponents)])

	def packageHasComponent(self, package, component):
		"""Check if module component is part of a package's name.

		Returns True if the package has that component and False otherwise.
		If package name OR module name is empty (""), then False is always
		returned. If they're BOTH empty, True is returned

		Arguments:
		package -- Full name of package
		component -- Component to check if it

		"""
		if len(package) == 0 and len(component) == 0:
			return True
		elif len(package) == 0 or len(component) == 0:
			return False
		else:
			return (component in package.split("."))

	def inWhitelist(self, dependency):
		"""Check if dependency is in the extractor's whitelist.

		Returns True if it is in the whitelist and False otherwise.
		If the extractor is not using a whitelist, then this
		method will always return True as all modules are allowed.

		Arguments:
		dependency -- instance of ParsedImport

		"""
		if not self.usingWhitelist():
			return True

		moduleName = dependency.moduleName
		if dependency.relative:
			# Check if the relative import was of the form "from . import X".
			# If so, remove the "." prefix
			if moduleName[0] == ".":
				moduleName = moduleName[1:]
			for name in self.whitelist:
				# Check if whitelisted package contains the relative module OR it
				# at least contains the relative module somewhere
				if self.belongsTo(name, moduleName) or self.packageHasComponent(name, moduleName):
					return True
		else:
			for name in self.whitelist:
				# Check if module name belongs to the whitelisted package/module
				if self.belongsTo(name, moduleName):
					return True
		return False

	def applyWhitelist(self, dependencies):
		"""Filter dependencies not in extractor's whitelist and return filtered dependencies

		Arguments:
		dependencies -- Set containing the dependencies to filter

		"""
		# Do nothing if we're not even using a whitelist
		if not self.usingWhitelist:
			return
		allowedDependencies = [ dep for dep in dependencies if self.inWhitelist(dep) ]
		return set(allowedDependencies)

	def extractFromString(self, data):
		"""Take Python source code as text and return the code's set of dependencies.

		Arguments:
		data -- String containing Python source code to analyse

		"""
		tokens = self.tokeniser.tokenise(data)
		if self.usingWhitelist():
			return self.applyWhitelist(foundDepdendencies)
		else:
			return foundDepdendencies