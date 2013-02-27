import sys
import os
import unittest

def runTests(testDirectory, projectDirectory = None, testName = None, workingDirectory = None):
	"""Run unit tests from files with filenames of the form test_*.py.

	Arguments:
	testDirectory -- Absolute path to directory containing all the tests

	Keyword arguments:
	projectDirectory -- Path to directory containing project to test. If
						None, then no extra paths will be added to the
						system path for module imports. (default: None)
	testName -- Name of specific test to run. If None, then all the test
				files within the test directory will used. (default: None)
	workingDirectory -- Working directory tests must be executed in for
						them in function correctly (default: None)

	"""
	# Store current working directory so it can be restored later
	oldValue = os.environ.get("PROJECT_ROOT_DIRECTORY")
	try:
		# If test name provided, search for specific test
		if testName:
			searchPattern = "test_{}.py".format(testName)
		# Otherwise, select all tests in directory
		else:
			searchPattern = "test_*.py"
		# Before processing tests, ensure desired project directory has been set
		if projectDirectory:
			os.environ["PROJECT_ROOT_DIRECTORY"] = projectDirectory
		# Also ensure that the current working is changed if it was specified
		if workingDirectory:
			os.chdir( os.path.abspath(workingDirectory) )
		# Perform the search for desired test
		suites = unittest.defaultTestLoader.discover(testDirectory, pattern=searchPattern)
		# Run all found test suites
		mainSuite = unittest.TestSuite(suites)
		textTestRunner = unittest.TextTestRunner(stream=sys.stdout).run(mainSuite)
	# Restore old environment variable if it existed
	finally:
		if oldValue:
			os.environ["PROJECT_ROOT_DIRECTORY"] = oldValue

def main(projectDirectory, testName, workingDirectory):
	"""Entry point of test script."""
	# Run specified tests using file's current directory as searching point
	testDirectory = os.path.abspath( os.path.dirname(__file__) )
	runTests(testDirectory, projectDirectory, testName, workingDirectory)	



if __name__ == "__main__":
	# Parse command line arguments
	# Ensure arguments after program name are EVEN so it's all pairs
	if len(sys.argv) == 0:
		arguments = []
	else:
		arguments = sys.argv[1:]
		if (len(arguments) % 2) == 1: # if odd
			arguments = arguments[:-1] # take last arg off 
	# Look in pairs for deisred information
	projectDirectory = None
	testName = None
	workingDirectory = None
	for i in range(0, len(arguments), 2):
		if arguments[i] ==  "-d":
			projectDirectory = arguments[i + 1]
		elif arguments[i] == "-t":
			testName = arguments[i + 1]
		elif arguments[i] == "-w":
			workingDirectory = arguments[i + 1]
	# Run program
	main(projectDirectory, testName, workingDirectory)