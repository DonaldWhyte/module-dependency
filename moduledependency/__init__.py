"""Main import for Python module dependency program.

Contains main class for executing a project dependency search
as well as utility code for outputting the found results.

"""

import sys
import os
import collections

from fileprocessor.searchers import FileSearcher
from fileprocessor.filterers import ExtensionFilterer, IncludeListFilterer
from fileprocessor import FileProcessor
from .dependency_extractor import ModuleDependencyExtractor, WhitelistGenerator
from .import_resolver import ImportResolver


# Done so importing modules from library is easier
def getSubModulesAndPackages():
	"""Return list of all modules and packages contained within current package."""
	modulesToImport = []

	# Add all Python files in directory
	directoryName = os.path.dirname(__file__)
	for filename in os.listdir(directoryName):
		# Ignore filenames in exclude list
		if filename in ["__pycache__"]:
			continue
		# If filename ends with .py, we assume it's a Python module
		elif filename.endswith(".py"):
			modulesToImport.append(filename[:-3])
		# If filename is actually a directory, we assume it's a subpackage
		else:
			absolutePath = os.path.abspath( os.path.join(directoryName, filename) )
			if os.path.isdir(absolutePath):
				modulesToImport.append(filename)

	return modulesToImport
__all__ = getSubModulesAndPackages()


class ResultOutputter:

	"""Interface for outputting results of a dependency search."""

	def createOutput(self, dependencies):
		"""Output result of dependency search in some way.

		This method must be implemented by subclasses.

		Arguments:
		dependencies -- Dictionary where the keys are package/module
					    names and the values are packages/modules that
					    their respective keys imported.
					    Both keys and values should be strings.

		"""
		raise NotImplementedError


class Executor:

	"""Main execution class for performaing dependency search.

	Combines the different components of the moduledependency package
	to perform a dependency search for a project.

	"""

	def __init__(self):
		"""Construct new instance of Executor."""
		self.outputter = None

	def setOutputter(self, newOutputter):
		"""Change object which outputs results of dependency search.

		Arguments:
		newOutputter -- Instance of ResultOutputter which will
						create the result's output.

		"""
		self.outputter = newOutputter

	def searchForDependencies(self, projectDirectory):
		"""Search for dependencies in a project.

		Returns dictionary where the keys are the packages/modules
		in the project and the values are packages/modules that
		the respective key imported.

		Arguments:
		projectDirectory -- Absolute path to the root directory
							of the project to search for
							dependencies in.

		"""
		if not os.path.isdir(projectDirectory):
			raise IOError("'{}' is not a valid directory".format(projectDirectory))

		# Generate list of files to consider in project directory
		whitelistGenerator = WhitelistGenerator()
		whitelist = whitelistGenerator.generate(projectDirectory)
		# Extract dependencies for the project directory
		searcher = FileSearcher(True)
		filterers = [ ExtensionFilterer(["py"]), IncludeListFilterer(whitelist) ]
		extractor = ModuleDependencyExtractor()
		processor = FileProcessor(searcher, filterers, extractor)
		dependencies = processor.process(projectDirectory)
		# Resolve relative imports
		resolver = ImportResolver(projectDirectory)
		return resolver.resolve(dependencies)

	def execute(self, projectDirectory):
		"""Execute dependency search.

		If an outputter has been assigned to this executor, then
		the results of the dependency search are feed to the
		outputter as well.

		Returns dictionary where the keys are the packages/modules
		in the project and the values are packages/modules that
		the respective key imported.

		Arguments:
		projectDirectory -- Absolute path to the root directory
							of the project to search for
							dependencies.

		"""
		# Get the resolve dependencies
		dependencies = self.searchForDependencies(projectDirectory)
		# If an outputter has been assigned, feed the dependencies to it
		if self.outputter:
			self.outputter.createOutput(dependencies)

		return dependencies