"""Main import for Python module dependency program.

Contains main class for executing a project dependency search
as well as utility code for outputting the found results.

"""

import os

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
