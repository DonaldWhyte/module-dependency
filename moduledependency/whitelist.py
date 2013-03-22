"""Contains functionalty to generate and use whitelists for filtering
module dependencies."""

import os
import re
from . import util


class WhitelistGenerator:

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
		# __init__ is not added  since that is the root of a package,
		# but __main__ isn't
		if filename != "__init__.py":
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
		rootPackage = util.getProjectRoot(projectDirectory)

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


class WhitelistApplier:

	"""Class which applies automatically generated whitelists to module dependencies."""

	def inWhitelist(self, dependency, whitelist):
		"""Return True if the dependency is in the given whitelist and False otherwise.

		A dependency is "in" the whitelist if there in element that
		which matches the dependency's name OR the dependency is
		CONTAINED within one of the whitelisted packages/modules.
		For example:

		inWhiteList("sys", ["sys", "os"])
		returns True because dependency matches an element in the whitelist.

		inWhiteList("sys.path", ["sys", "os"])
		returns True because dependency "sys.path" is CONTAINED
		within the module "sys".

		IMPORTANT NOTE: This only applies at a SINGLE package level.
		This means the following:
		inWhiteList("sys.path.abspath", ["sys", "os"])
		fails. White "sys.path.abspath" may be contained within "sys",
		"abspath" is not in "sys" but "sys.path", which is NOT
		whitelisted.

		Arguments:
		dependency -- String containing package name of dependency. 
		whitelist -- List containing names of all allowed packages
					 and modules

		"""
		# If there's a direct match in the whitelist, return True
		# straight away
		if dependency in whitelist:
			return True
		# Otherwise, check if the dependency has a direct parent
		# in the whitelist
		else:
			# Split the dependency into components and remove the
			# last component if there is more than one component
			components = dependency.split(".")
			if len(components) > 1:
				del components[-1]
			# Reconstruct dependency name and check if it's in the whitelist
			upperLevelDependency = ".".join(components)
			return (upperLevelDependency in whitelist)

	def applyToProject(self, projectRoot, dependencies):
		"""Filter modules and dependencies that aren't contained in a project.

		A dictionary, where the keys are packages/modules in
		the given project and values are lists of dependencies
		also in the project, is retured.

		Arguments:
		projectRoot -- Absolute path to the root directory
					   of the project
		dependencies -- Dependencies found in project, given
						as a dictionary where the keys are
						strings containing the full names 

		"""
		# Generate whitelist for the desired project
		generator = WhitelistGenerator()
		allowedPackages = generator.generate(projectRoot)
		# Apply the whitelist to the project's dependencies
		projectDependencies = {} 
		for key, value in dependencies.items():
			# Only add if the module name is in the whitelist
			if self.inWhitelist(key, allowedPackages):
				# Use whitelist to filter any of the module's dependencies too
				filteredSet = set()
				for dep in value:
					if self.inWhitelist(dep, allowedPackages):
						filteredSet.add(dep)
				projectDependencies[key] = filteredSet
		return projectDependencies