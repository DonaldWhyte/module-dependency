import unittest
import sys
import os
sys.path.append(os.environ.get("PROJECT_ROOT_DIRECTORY", "."))

from moduledependency.depth_pruner import DepthPruner



class TestDepthPruner(unittest.TestCase):

    def setUp(self):
        self.pruner = DepthPruner()

    def tearDown(self):
        self.pruner = None

    def test_prunePackageName(self):
        # Test negative value for depth
        with self.assertRaises(ValueError):
            self.pruner.prunePackageName("project.pack1.a", -1)
        # Test empty package name
        self.assertEqual( self.pruner.prunePackageName("", 0), "" )
        self.assertEqual( self.pruner.prunePackageName("", 1), "" )
        self.assertEqual( self.pruner.prunePackageName("", 2), "" )
        # Test zero, one and two depth
        self.assertEqual( self.pruner.prunePackageName("project.pack1.a", 0), "project" )
        self.assertEqual( self.pruner.prunePackageName("project.pack1.a", 1), "project.pack1" )
        self.assertEqual( self.pruner.prunePackageName("project.pack1.a", 2), "project.pack1.a" )
        # Test five depth where there isn't actually a depth of five in the name
        self.assertEqual( self.pruner.prunePackageName("project.pack1.a", 5), "project.pack1.a" )
        # Test five depth where there is EXACTLY a depth of five
        self.assertEqual( self.pruner.prunePackageName("project.pack1.a.b.c.d", 5), "project.pack1.a.b.c.d" )
        # Test five depth where the depth of the name is greater than five
        self.assertEqual( self.pruner.prunePackageName("project.pack1.a.b.c.d.e", 5), "project.pack1.a.b.c.d" )
        
    def test_pruneDependency(self):
        # Test with no dependencies
        self.assertEqual( self.pruner.pruneDependencyList("project.pack1.a", [], 1),
            ("project.pack1", set()) )

        PRUNED_DEPENDANT_NAME = "project.pack1"
        PRUNED_DEPENDENCIES = set(["project.z", "project.pack2"])

        # Test with many dependencies
        self.assertEqual( self.pruner.pruneDependencyList(
            "project.pack1.a", ["project.z", "project.pack2.a"], 1),
            (PRUNED_DEPENDANT_NAME, PRUNED_DEPENDENCIES) )
        # Test dependencies where two of them will end up identical
        # Ensures that the method removes duplicates that may result
        # from pruning
        self.assertEqual( self.pruner.pruneDependencyList(
            "project.pack1.a", ["project.z", "project.pack2.a", "project.pack2.b"], 1),
              (PRUNED_DEPENDANT_NAME, PRUNED_DEPENDENCIES) )
        # Test dependencies which results in a recursive dependency
        # Ensure that the method removes recursive dependencies form
        # pruned results
        self.assertEqual( self.pruner.pruneDependencyList(
            "project.pack1.a", ["project.z", "project.pack2.a", "project.pack2.b", "project.pack1.b"], 1),
            (PRUNED_DEPENDANT_NAME, PRUNED_DEPENDENCIES) )

    def test_prune(self):
        DEPENDENCIES = {
            "project" : set(["project.pack", "project.pack2"]),
            "project.__main__" : set(["project.a", "project.pack.subpack2"]),
            "project.a" : set(["project.a", "project.pack"]),
            "project.pack.subpack2" : set(["project.pack.subpack2.subsubpack.c", "project.pack.subpack2.d"]),
            "project.pack.subpack2.d" : set(["project.pack.subpack2.subsubpack.c", "project.pack2.e", "project.pack"]),
            "project.pack.subpack2.subsubpack.c" : set(),
            "project.pack2.e" : set(["project.pack2.subpack.f"]),
            "project.pack2.subpack.f" : set(["project.pack2.e"])
        }
        DEPTH1_DEPENDENCIES = {
            "project" : set(["project.pack", "project.pack2"]),
            "project.__main__" : set(["project.a", "project.pack"]),
            "project.a" : set(["project.pack"]),
            "project.pack" : set(["project.pack2"]),
            "project.pack2" : set()
        }
        DEPTH2_DEPENDENCIES = {
            "project" : set(["project.pack", "project.pack2"]),
            "project.__main__" : set(["project.a", "project.pack.subpack2"]),
            "project.a" : set(["project.pack"]),
            "project.pack.subpack2" : set(["project.pack2.e", "project.pack"]),
            "project.pack2.e" : set(["project.pack2.subpack"]),
            "project.pack2.subpack" : set(["project.pack2.e"]),
        }

        # Test with negative value for depth
        with self.assertRaises(ValueError):
            self.pruner.prune(DEPENDENCIES, -1)
        # Test with empty dependencies
        self.assertEqual( self.pruner.prune({}, 0), {})
        # Test with depth 0 (should just be "project => []")
        self.assertEqual( self.pruner.prune(DEPENDENCIES, 0), {"project" : set()})
        # Test with depth 1 (this will MERGE many of the dependency lists together)
        self.assertEqual( self.pruner.prune(DEPENDENCIES, 1), DEPTH1_DEPENDENCIES )
        # Test with depth 2
        self.assertEqual( self.pruner.prune(DEPENDENCIES, 2), DEPTH2_DEPENDENCIES)