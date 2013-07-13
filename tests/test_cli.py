import unittest
import sys
import os

sys.path.append(os.environ.get("PROJECT_ROOT_DIRECTORY", "."))
from moduledependency.cli import ArgumentProcessor


class TestArgumentProcessor(unittest.TestCase):

    # Name of test source file
    TEST_SCRIPT_NAME = "test.py"

    def checkForErrors(self, argLists, expectedError, exceptionType = RuntimeError):
        for args in argLists:
            with self.assertRaises(exceptionType) as cm:
                self.processor.process([self.TEST_SCRIPT_NAME, "--project=."] + args)
            self.assertEqual(str(cm.exception), expectedError)            

    def setUp(self):
        self.processor = ArgumentProcessor()

    def test_sanitiseKey(self):
        # Test key with no "-" prefix
        with self.assertRaises(ValueError):
            self.processor.sanitiseKey("depth")        
        # Test keys with valid prefixes
        self.assertEqual(self.processor.sanitiseKey("-d"), "d")
        self.assertEqual(self.processor.sanitiseKey("--depth"), "depth")
        # Test single dash with greather than one character for key name
        with self.assertRaises(ValueError):
            self.processor.sanitiseKey("-depth")
        # Test key with too many dashes in prefix
        with self.assertRaises(ValueError):
            self.processor.sanitiseKey("---depth")

    def test_sanitiseValue(self):
        # Test valid values
        self.assertEqual(self.processor.sanitiseValue("3"), "3")
        self.assertEqual(self.processor.sanitiseValue("test"), "test")
        self.assertEqual(self.processor.sanitiseValue("hello world"), "hello world")
        # Ensure wrapping quotes (single and double) are removed from values
        self.assertEqual(self.processor.sanitiseValue("\'3\'"), "3")
        self.assertEqual(self.processor.sanitiseValue("\"3\""), "3")

    def test_parseOptions(self):
        # Test empty list
        self.assertEqual( self.processor.parseOptions([]), {} )
        # Test no equals sign
        with self.assertRaises(RuntimeError):
            self.processor.parseOptions(["-d"])
        # Test too many equals signs
        with self.assertRaises(RuntimeError):
            self.processor.parseOptions(["-d=4=6"])
        # Test exactly right
        self.assertEqual( self.processor.parseOptions(["-d=3"]),
            { "d" : "3" } )
        # Test multiple correct arguments
        self.assertEqual( self.processor.parseOptions(["-d=3", "--max-stuff=3000", "--outputter='dot'"]),
            { "d" : "3", "max-stuff": "3000", "outputter" : "dot" } )        
        # Test multiple arguments where one is incorrect
        with self.assertRaises(RuntimeError):
            self.processor.parseOptions(["-d=3", "--max-boxes=10", "--name=donald", "--invalid="])

    def test_help(self):
        for args in [ [], ["-h"], ["--help"], ["test.py", "o=dot", "-h"], ["test.py" "o=dot", "--help"] ]:
            with self.assertRaises(RuntimeError) as cm:
                self.processor.process(args)
            self.assertEqual(str(cm.exception), ArgumentProcessor.USAGE_MESSAGE)

    def test_invalid_arguments(self):
        # Test invalid depth values
        self.checkForErrors([ ["-d=haha"], ["--depth=haha"] ], "Invalid depth 'haha' provided", ValueError) # not integer
        self.checkForErrors([ ["-d=-1"], ["--depth=-441"] ], "Maximum depth cannot be negative", ValueError) # negative integers
        # Test absence of mandatory parameters
        with self.assertRaises(RuntimeError) as cm:
            self.processor.process(["test.py", "-o=dot" ])
        self.assertEqual(str(cm.exception), "Not all mandatory options have been specified")

    def test_valid_arguments_and_option_retrieval(self):
        # Test non-existent directory
        with self.assertRaises(IOError):
            self.processor.process(["test.py", "-p=test", "-d=0"])
        # Test valid depth values
        self.processor.process(["test.py", "-p=.", "-d=0"])
        self.assertEqual(self.processor.maxDepth, 0)
        self.processor.process(["test.py", "-p=.", "-d=1"])
        self.assertEqual(self.processor.maxDepth, 1)
        self.processor.process(["test.py", "-p=.", "-d=29483"])
        self.assertEqual(self.processor.maxDepth, 29483)
        # Test valid outputter name
        self.processor.process(["test.py", "-p=.", "-o=dot"])
        self.assertEqual(self.processor.outputterName, "dot")
        # Test arbitrary options
        self.processor.process(["test.py", "-p=.", "--some-option=hello!", "-j=4"])
        self.assertEqual(self.processor.getOption("some-option"), "hello!")
        self.assertEqual(self.processor.getOption("j"), "4")
        self.assertEqual(self.processor.outputterName, None)

        # Test non-existent option
        self.assertEqual(self.processor.getOption("non-existent"), None)
        # Test getting the same option but just using multiple names for it
        self.assertEqual(self.processor.getOption("p"), ".")
        self.assertEqual(self.processor.getOption("project"), ".") # wasn't directly specified
        # Test getting option with only one name
        self.assertEqual(self.processor.getOption("some-option"), "hello!")

        expectedArgs = { "some-option" : "hello!", "j" : "4" }
        self.assertEqual(self.processor.getOutputterArguments(), expectedArgs)