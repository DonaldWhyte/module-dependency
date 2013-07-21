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
                ({}, "digraph dependencies {\n}"),
                ( {"mod.a" :["mod.b", "mod.c"], "mod.b" : [], "mod.c" : ["mod.d"] },
                  'digraph dependencies {\n\tmod_a -> mod_b;\n\tmod_a -> mod_c;\n\tmod_b;\n\tmod_c -> mod_d;\n}' ),
            ],
            self.assertEqual,
            True)
        tester.runTests()

    def test_sanitiseNodeID(self):
        outputter = Outputter()
        # Empty input
        self.assertEqual(Outputter.EMPTY_NODE_ID, outputter.sanitiseNodeID(""))
        # Node with disallowed characters (e.g. dots and dashes, quotes)
        # Should be replaced with underscores!
        self.assertEqual("a_b", outputter.sanitiseNodeID("a.b"))
        self.assertEqual("a_b", outputter.sanitiseNodeID("a-b"))
        self.assertEqual("a_b_c", outputter.sanitiseNodeID("a_b%c"))
        self.assertEqual("a_b_c_", outputter.sanitiseNodeID("a_b\"c\""))
        self.assertEqual("_xy", outputter.sanitiseNodeID("\'xy"))
        self.assertEqual("_xy_", outputter.sanitiseNodeID("\'xy\'"))
        self.assertEqual("_", outputter.sanitiseNodeID("."))
        # Node starting with a digit
        self.assertEqual("_n", outputter.sanitiseNodeID("3n"))
        self.assertEqual("_n_x", outputter.sanitiseNodeID("3n.x"))
        # Node with surrounded by DOUBLE quotes (allowed)
        self.assertEqual("__", outputter.sanitiseNodeID("\"\""))
        self.assertEqual("\"hello\"", outputter.sanitiseNodeID("\"hello\""))
        self.assertEqual("\"a_b\"", outputter.sanitiseNodeID("\"a.b\""))
