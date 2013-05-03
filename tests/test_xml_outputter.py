import unittest
import sys
import os

sys.path.append(os.environ.get("PROJECT_ROOT_DIRECTORY", "."))
from moduledependency.outputters.xml import Outputter
from tests.util import OutputterTestHarness


class TestXMLOutputter(unittest.TestCase):

    def test_createOutput(self):
        tester = OutputterTestHarness(Outputter,
            # Empty input
            [
                ({}, "<xml><dependencies></dependencies></xml>"),
                ( {"moda" :["modb", "modc"], "modb" : [], "modc" : ["modd"] },
                  '<xml><dependencies><dependant name="moda"><dependency>modb</dependency><dependency>modc</dependency></dependant><dependant name="modb"></dependant><dependant name="modc"><dependency>modd</dependency></dependant></dependencies></xml>'
                )
            ],
            self.assertEqual,
            True)
        tester.runTests()