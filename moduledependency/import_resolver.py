"""Contains functionality for resolving parsed imports to their full package names."""

import os
import re
import platform
from .parser import ParsedImport
from . import util

class ImportResolver:

	"""Class which resolves relative imports into full, absolute imports."""

	PRECEDING_DOT_REGEX = re.compile("^(\.+).*$")

	def __init__(self, rootDirectory):
		"""Construct instance of ImportResolver.

		Arguments:
		rootDirectory -- Absolute path to the project's root
						 directory.

		"""
		# Make sure to remove drive name from the filename if it's Windows
		if platform.system() == "windows":
			rootDirectory = rootDirectory[3:] # remove "C:/"
		# Sanitise root directory by ensuring only / is used
		# as a path separator
		self.rootDirectory = re.sub(r"(\\|/)", "/", rootDirectory)

	def getPackageName(self, packagePath):
		"""Return name of package (relative to project root) given Python.

		Arguments:
		packagePath -- Absolute path to the Python package

		"""
		# Ensure package path separators are forward slashes
		sanitisedPath = re.sub(r"(\\|/)", "/", packagePath)		
		# Ensure if package directory is actually inside the root directory
		if not sanitisedPath.startswith(self.rootDirectory):
			raise ValueError("Path '{}' is not inside project root '{}'".format(
				packagePath, self.rootDirectory))
		# Remove root directory from the package directory
		sanitisedPath = sanitisedPath[len(self.rootDirectory) + 1:]
		if len(sanitisedPath) == 0:
			raise ValueError("Root project directory '{}' was given - this is " \
				"not a valid package in the project".format(sanitisedPath))
		# Remove extension
		sanitisedPath = os.path.splitext(sanitisedPath)[0]
		# Ensure there is no trailing separators if path is directory
		if sanitisedPath.endswith("/"):
			sanitisedPath = sanitisedPath[:-1]

		return sanitisedPath.replace("/", ".")

	def addRootToPackage(self, package):
		"""Include project's root package in package name and return result.

		Arguments:
		package -- Package to get the full name of

		"""
		rootPackage = util.getProjectRoot(self.rootDirectory)
		if len(package) > 0:
			return "{}.{}".format(rootPackage, package)
		else:
			return rootPackage

	def resolveImport(self, dependantModulePath, importedModule):
		"""Resolve relative import to full package name (relaitve to project root).

		This is achieved using the project root directory and
		dependant module given as a directory.

		If dependantModulePath is not a string, a TypeError is raised.
		If importedModule is not a relative import, a ValueError is raised.

		Arguments:
		dependantModulePath -- Absolute path to the module (.py file)
							   which made the import. Must be a string.
		importedModule -- Instance of ParsedImport, which corresponds
						  to an import that the module pointed to by
						  dependantModulePath made.

		"""
		if not isinstance(dependantModulePath, str):
			raise TypeError("Path to dependant module must be a string")
		if not importedModule.isRelative():
			raise ValueError("Imported module '{}' should be a relative import".format(importedModule.moduleName))

		# Get full package name of dependant module (based on project root)
		dependantModule = self.getPackageName(dependantModulePath)
		# If the module is a package __init__.py file, then those filenames are
		# removed from the final dependant module name
		wasInit = False
		if dependantModule.endswith("__init__"):
			wasInit = True
			dependantModule = dependantModule[:-8]
			# Ensure there is no trailing dot
			if dependantModule.endswith("."):
				dependantModule = dependantModule[:-1]
		else:
			# Remove last component from name (as that's the module that has imported something)
			packageComponents = dependantModule.split(".")
			dependantModule = ".".join( packageComponents[:-1] )

		name = importedModule.moduleName

		# Extract preceding dots from module name
		match = self.PRECEDING_DOT_REGEX.match(importedModule.moduleName)
		if match:
			precedingDots = match.group(1)
		else:
			precedingDots = ""
		# If there are two or more dots, then a package from an upper
		# upper level is desired
		if len(precedingDots) >= 2:
			# Compute number of levels to go up package hierarchy
			levelsToGoUp = len(precedingDots) - 1
			dependantModuleComponents = dependantModule.split(".")
			# Check if it's possible to go up enough levels
			if len(dependantModuleComponents) < levelsToGoUp: 
				raise ValueError("Could not resolve import '{}' from '{}' - "
					"upper-level import out of project bounds".format(dependantModule, importedModule))
			# Remove preceding dots from module name
			name = name[len(precedingDots):]				
			# Reconstruct dependant module name by removing as many
			# components at the end as there are dots
			dependantModule = ".".join( dependantModuleComponents[:-levelsToGoUp] )
		# If there is a SINGLE preceding dot in the imported module,
		# then remove it since it's a relative import at the CURRENT
		# level of the package directory
		elif len(precedingDots) == 1:
			name = importedModule.moduleName[1:]

		if len(dependantModule) == 0:
			return self.addRootToPackage(name)
		else:
			return self.addRootToPackage( "{}.{}".format(dependantModule, name) )

	def resolveImports(self, dependencies):
		"""Resolves a collection of imports to their full package names.

		Note that this does not just resolve imports of modules, but 
		also transforms the absolute paths to modules to their full
		module names.

		By FULL module name, this includes the project's ROOT package
		(which is the name of the projec's root directory).

		If dependencies is not a dictionary, then a TypeError is raised.

		Arguments:
		dependencies -- Dictionary where the keys are the absolute
					   paths to Python modules and the values are
					   sets containing ParsedImport objects that
					   correspond to dependencies of the module
					   pointed to by the associated path.

		"""
		if not isinstance(dependencies, dict):
			raise TypeError("Module dependencies must be a dictionary")

		resolvedDependencies = {}
		for modulePath, moduleDepenendencies in dependencies.items():
			# Compute final package name of module.
			moduleName = self.getPackageName(modulePath)
			moduleName = self.addRootToPackage(moduleName)
			# Ensure that __init__ is removed to make it a PACKAGE
			if moduleName.endswith("__init__"):
				moduleName = moduleName[:-8]
				if moduleName.endswith("."):
					moduleName = moduleName[:-1]
			# Resolve all absolute and relative dependencies
			resolved = set()
			for dep in moduleDepenendencies:
				if dep.isRelative():
					resolved.add( self.resolveImport(modulePath, dep) )
				else:
					resolved.add( dep.moduleName )
			# Add resolve module and its dependencies to new dictionary
			resolvedDependencies[moduleName] = resolved
		return resolvedDependencies