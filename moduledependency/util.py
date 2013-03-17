"""Contains miscellaneous functionality used by more than one module."""

import os

def getProjectRoot(projectDirectory):
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
