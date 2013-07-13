"""Contains main execution logic for dependency extraction."""

import sys
import os
import collections

from fileprocessor.searchers import FileSearcher
from fileprocessor.filterers import ExtensionFilterer, IncludeListFilterer
from fileprocessor import FileProcessor
from .dependency_extractor import ModuleDependencyExtractor
from .whitelist import WhitelistApplier
from .import_resolver import ImportResolver
from .depth_pruner import DepthPruner

class Executor:

    """Main execution class for performaing dependency search.

    Combines the different components of the moduledependency package
    to perform a dependency search for a project.

    """

    def __init__(self):
        """Construct new instance of Executor."""
        self.outputter = None
        self.maximumDepth = None

    def setOutputter(self, newOutputter):
        """Change object which outputs results of dependency search.

        Arguments:
        newOutputter -- Instance of ResultOutputter which will
                        create the result's output.

        """
        self.outputter = newOutputter

    def setMaximumDepth(self, maxDepth):
        """Set maximum depth of dependencies to return. 

        Arguments:
        maxDepth -- Positive integer representing maximum depth
                    of dependencies to produce. If None, then
                    no maximum limit on depth will be applied.

        """
        # If None is given, we clear the depth limit
        if maxDepth == None:
            self.maximumDepth = None
            return
            
        if not isinstance(maxDepth, int):
            raise TypeError("Maximum depth must be an integer")
        if maxDepth < 0:
            raise ValueError("Maximum depth cannot be negative")
        self.maximumDepth = maxDepth

    def searchForDependencies(self, projectDirectory):
        """Search for dependencies in a project.

        Returns dictionary where the keys are the packages/modules
        in the project and the values are packages/modules that
        the respective key imported.

        Arguments:
        projectDirectory -- Absolute path to the root directory
                            of the project to search for
                            dependencies in.

        """
        if not os.path.isdir(projectDirectory):
            raise IOError("'{}' is not a valid directory".format(projectDirectory))
        # Important to make the project directory an absolute path
        projectDirectory = os.path.abspath(projectDirectory)
        
        # Extract dependencies for the project directory
        searcher = FileSearcher(True)
        filterers = [ ExtensionFilterer(["py"]) ]
        extractor = ModuleDependencyExtractor()
        processor = FileProcessor(searcher, filterers, extractor)
        dependencies = processor.process(projectDirectory)
        # Resolve relative imports
        resolver = ImportResolver(projectDirectory)
        dependencies = resolver.resolveImports(dependencies)
        # Finally, apply a whitelist to the dependencies to only
        # include modules that belong to the scanned project
        whitelistApplier = WhitelistApplier()
        return whitelistApplier.applyToProject(projectDirectory, dependencies)

    def execute(self, projectDirectory):
        """Execute dependency search.

        If an outputter has been assigned to this executor, then
        the results of the dependency search are feed to the
        outputter as well.

        Returns dictionary where the keys are the packages/modules
        in the project and the values are packages/modules that
        the respective key imported.

        Arguments:
        projectDirectory -- Absolute path to the root directory
                            of the project to search for
                            dependencies.

        """
        # Get the resolved dependencies
        dependencies = self.searchForDependencies(projectDirectory)
        # If a maximum depth was specified, use a DepthPruner to prune
        # dependencies found
        if self.maximumDepth:
            pruner = DepthPruner()
            dependencies = pruner.prune(dependencies, self.maximumDepth)
        # If an outputter has been assigned, feed the dependencies to it
        if self.outputter:
            output = self.outputter.createOutput(dependencies)
            if output:
                print(output)

        return dependencies