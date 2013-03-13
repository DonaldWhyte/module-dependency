"""Contains functionality for resolving parsed imports to their full package names."""

import os
import re
from .parser import ParsedImport

class ImportResolver:

	"""TODO"""

	def __init__(self, rootDirectory):
		"""Construct instance of ImportResolver.

		Arguments:
		rootDirectory -- Absolute path to the project's root
						 directory.

		"""
		# Sanitise root directory by ensuring only / is used
		# as a path separator
		self.rootDirectory = re.sub(r"(\\|/)",
			os.sep.replace("\\", "\\\\"), rootDirectory)

	def getPackageName(self, packagePath):
		"""Return name of package (relative to project root) given Python.

		Arguments:
		packagePath -- Absolute path to the Python package

		"""
		# Ensure package path separators are forward slashes
		sanitisedPath = re.sub(r"(\\|/)", os.sep.replace("\\", "\\\\"), packagePath)		
		# Ensure if package directory is actually inside the root directory
		if not sanitisedPath.startswith(self.rootDirectory):
			raise ValueError("Path '{}' is not inside project root '{}'".format(
				packagePath, self.rootDirectory))
		# Remove root directory from the package directory
		sanitisedPath = sanitisedPath[len(self.rootDirectory) + 1:]
		if len(sanitisedPath) == 0:
			raise ValueError("Root project directory '{}' was given - this is" \
				"not a valid package in the project".format(sanitisedPath))
		# Remove extension
		sanitisedPath = os.path.splitext(sanitisedPath)[0]
		# If path ends with __init__ or __main__, remove them to make
		# to make the name correspond to just that package
		if sanitisedPath.endswith("__init__") or sanitisedPath.endswith("__main__"):
			sanitisedPath = sanitisedPath[:-8]
		# Ensure there is no trailing separators if path is directory
		if sanitisedPath.endswith("/"):
			sanitisedPath = sanitisedPath[:-1]

		return sanitisedPath.replace("/", ".")

	def resolveImport(self, dependantModulePath, importedModule):
		"""TODO

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
		# Remove last component from name (as that's the module that has imported something)
		packageComponents = dependantModule.split(".")
		dependantModule = ".".join( packageComponents[:-1] )
		# Ensure there is no preceding dot in imported module name
		if importedModule.moduleName.startswith("."):
			name = importedModule.moduleName[1:]
		else:
			name = importedModule.moduleName
			
		if len(dependantModule) == 0:
			return name
		else:
			return "{}.{}".format(dependantModule, name)