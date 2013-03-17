"""Contains functionalty to identify dependencies in Python source code and
filter external and standard library dependencies."""

import os.path
import re
from collections import Iterable

from fileprocessor.extractors import TextExtractor
from .tokeniser import Tokeniser
from .parser import ImportParser, ParsedImport

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
		foundDepdendencies = self.parser.parse(tokens)
		if self.usingWhitelist():
			return self.applyWhitelist(foundDepdendencies)
		else:
			return foundDepdendencies

class WhitelistGenerator:

	def getProjectRoot(self, projectDirectory):
		"""Return name of root project package using the project's directory.

		Arguments:
		projectDirectory -- *Absolute* path to the project which
							stores source code being scanned.

		"""
		if len(projectDirectory) == 0:
			raise ValueError("Path to project is empty")
		# Split directory into path components
		components = os.path.split(projectDirectory)
		# Check if path is a root
		if len(components) == 2 and components[1] == "":
			return ""
		# If not root, just return last path component
		else:
			return components[-1]

	def getPackageName(self, filename):
		"""Convert filename to Python package/module name.

		Arguments:
		filename -- Filename of package/module to generate name of.
					Note that this must be *relative* to the *root*
					of the project.

		"""
		if len(filename) == 0:
			raise ValueError("Filename of package or module is empty")
		extension = os.path.splitext(filename)[1]
		if len(extension) > 0 and extension != ".py":
			raise ValueError("Filename must point to a valid Python file with the extension '.py' or a directory")

		directory, filename = os.path.split(filename)	
		# Construct package name
		packageName = ""
		if len(directory) > 0:
			# Replace path separators with "."
			packageName += re.sub(r"(\\|/)", ".", directory)
		if filename != "__init__.py" and filename != "__main__.py":
			if len(packageName) > 0:
				packageName += "."
			# Remove extension from filename
			packageName += os.path.splitext(filename)[0]
		return packageName

	def generate(self, projectDirectory):
		"""Generate a list of all packages/modules.

		projectDirectory -- *Absolute* path to the project whose
							whitelist we need to generate.

		"""
		if not os.path.isdir(projectDirectory):
			raise IOError("Directory '{}' does not exist".format(projectDirectory))

		# Pre-compute root package using project directory
		rootPackage = self.getProjectRoot(projectDirectory)

		whitelist = []
		for root, directories, filenames in os.walk(projectDirectory):
			for name in (directories + filenames):
				# Make sure that the root directory (of current directories/files)
				# and the project directory use the same path separator
				sanitisedRoot = re.sub(r"(\\|/)", os.sep.replace("\\", "\\\\"), root)
				partToRemove = re.sub(r"(\\|/)", os.sep.replace("\\", "\\\\"), projectDirectory)
				# Remove project directory from the root directory, as we only care
				# aobut the file's RELATIVE position in the project
				trimmedRoot = sanitisedRoot[len(partToRemove) + 1:]
				# Create the full RELATIVE path to the directory/file by combining
				# the directory the current file is contained with the name
				# of it the file itself
				name = os.path.join(trimmedRoot, name)
				# Get package name for the file being processed
				packageName = None
				try:
					packageName = self.getPackageName(name)
				# If invalid package name, we just ignore that module
				except ValueError:
					continue
				# Add root package to the name and add it to the whitelist
				if len(packageName) > 0:
					packageName = "{}.{}".format(rootPackage, packageName)
				else:
					packageName = rootPackage
				whitelist.append(packageName)

		return whitelist