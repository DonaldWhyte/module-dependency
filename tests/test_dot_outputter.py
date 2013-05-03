import unittest
import sys
import os

sys.path.append(os.environ.get("PROJECT_ROOT_DIRECTORY", "."))
from moduledependency.outputters.dot import Outputter
from tests.util import OutputterTestHarness


class TestDotOutputter(unittest.TestCase):

    def test_createOutput(self):
        tester = OutputterTestHarness(Outputter,
            # Empty input
            [
                ({}, "graph dependencies {\n}"),
                ( {"moda" :["modb", "modc"], "modb" : [], "modc" : ["modd"] },
                  'graph dependencies {\n\tmoda;\n\tmodb;\n\tmodc;\n\tmoda -> modb;\n\tmoda -> modc;\n\tmodc -> modd;\n}' ),
            ],
            self.assertEqual,
            True)
        tester.runTests()