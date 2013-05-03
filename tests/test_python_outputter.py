import unittest
import sys
import os

sys.path.append(os.environ.get("PROJECT_ROOT_DIRECTORY", "."))
from moduledependency.outputters.python import Outputter
from tests.util import OutputterTestHarness


class TestPythonOutputter(unittest.TestCase):

    def test_createOutput(self):
        tester = OutputterTestHarness(Outputter,
            # Empty input
            [
                ({}, "{  }"),
                ( {"moda" :["modb", "modc"], "modb" : [], "modc" : ["modd"] },
                  '{ "moda" : [ "modb", "modc" ], "modb" : [  ], "modc" : [ "modd" ] }' ),
            ],
            self.assertEqual,
            True)
        tester.runTests()