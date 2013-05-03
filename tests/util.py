"""Contains functionality useful for multiple test files."""

import unittest
import os

class OutputterTestHarness:

    """Test cases which test outputters can use this class to
    construct tests easily."""

    TEST_OUTPUT_FILE = ".__test_output"

    def __init__(self, outputterClass, inputsOutputs, assertEqual, testFiles=True):
        self.outputterClass = outputterClass
        self.inputsOutputs = inputsOutputs
        # Method from TestCase is stored here so assertions can be made
        # outside of main TestCase class
        self.assertEqual = assertEqual
        self.testFiles = testFiles

    def runTests(self):
        # Outputter configured to simply return output as string
        stdoutOutputter = self.outputterClass()
        # Outputter configured to place output in file
        if self.testFiles:
            fileOutputter = self.outputterClass(filename=self.TEST_OUTPUT_FILE)

        try:
            for inputData, outputData in self.inputsOutputs:
                self.assertEqual(stdoutOutputter.createOutput(inputData), outputData)
                if self.testFiles:
                    fileOutputter.createOutput(inputData)
                    self.assertEqual(os.path.exists(self.TEST_OUTPUT_FILE), True)
                    with open(self.TEST_OUTPUT_FILE, "r") as f:
                        self.assertEqual(f.read(), outputData)
        finally:
            # Ensure test file is deleted
            if self.testFiles:
                if os.path.exists(self.TEST_OUTPUT_FILE):
                    os.remove(self.TEST_OUTPUT_FILE)