import unittest
from types import ModuleType
import sys
import os
sys.path.append(os.environ.get("PROJECT_ROOT_DIRECTORY", "."))

from moduledependency.outputter import OutputterFactory
from .outputters import test



class TestDepthPruner(unittest.TestCase):

    def setUp(self):
        self.outputterFactory = OutputterFactory("outputters")

    def tearDown(self):
        self.outputterFactory = None

    def test_construction(self):
        # Test non-string directory name
        with self.assertRaises(TypeError):
            OutputterFactory(45)
        # Test non-existent directory
        with self.assertRaises(IOError):
            OutputterFactory("non-existent_dir8329879rhfe9hw9h9gh")
        # Test factory constructed in setUp() is correct
        self.assertEqual(self.outputterFactory.pluginDirectory, os.path.abspath("outputters"))

    def test_getOutputterFilename(self):
        # Trivial function difficult to construct stub values for true
        # unit testing (due to the nature of the file path consturction).
        # Also, this ends up being tested in 
        pass

    def test_loadOutputter(self):
        # Test non-existent outputter name
        with self.assertRaises(IOError):
            self.outputterFactory.loadOutputter("non-existent")
        # Test outputter name with Python module but no outputter class
        with self.assertRaises(RuntimeError):
            self.outputterFactory.loadOutputter("no-class")
        # Test outputter name with Python module but the outputter is
        # NOT a subclass of ResultOutputter
        with self.assertRaises(RuntimeError):
            self.outputterFactory.loadOutputter("not-subclass")
        # Test outputter with output class
        module = self.outputterFactory.loadOutputter("test")
        self.assertTrue( isinstance(module, ModleType) )
        # Ensure factory's cache was updated
        self.assertTrue( "test" in self.outputterFactory.moduleCache )

        # Fudge the cache to include a module so we can test loading from
        # the cache
        self.outputterFactory.moduleCache.update( {"cache-test" : sys } )
        module = self.outputterFactory.loadOutputter("cache-test")
        self.assertTrue( isinstance(module, ModleType) )

    def test_createOutputter(self):
        # Test non-existent outputter
        with self.assertRaises(IOError):
            self.outputterFactory.createOutputter("non-existent")
        # Test outputter with Python module but no outputter class
        with self.assertRaises(RuntimeError):
            self.outputterFactory.createOutputter("no-class")
        # Test outputter with output class
        outputter = self.outputterFactory.createOutputter("test")
        self.assertTrue( isinstance(outputter, test.Outputter) )
        self.assertEqual( outputter.createOutput("TEST"), "TEST" )