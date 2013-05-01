"""Contains functionality for pruning dependencies with a certain
depth so higher-level views of dependencies can be constructed."""

class DepthPruner:

    """Used to prune dependencies with a specified depth.

    Prunes dependnecies in the project hiearhcy to provide varying
    levels of detail tp the results of dependency extractions.

    """

    def prunePackageName(self, packageName, depth):
        """Prune package name to a specified depth.

        Arguments:
        packageName -- Full name of the package, from the
                       project root, as a string
        depth -- Depth to prune name to. For example, if
                 depth = 1 then "a.b.c" will be pruned
                 to "a.b". Value must be an integer
                 greater than or equal to 0.

        """
        if depth < 0:
            raise ValueError("Cannot have negative depth")
        # Split name into its components
        components = packageName.split(".")
        # Prune components at the end based on desired depth
        end = min(depth + 1, len(packageName))
        return ".".join( components[:end] ) 

    def pruneDependencyList(self, dependantPackageName, dependencies, depth):
        """Prune name of package and its dependencies.

        A two-element tuple is returned, where the first element is the
        pruned name of the dependant package and the second element is
        a set containing the pruned names of any packages/modules that
        the dependant package dpeends on.

        Any duplicate entries in the dependency list after pruning are
        removed.

        Arguments:
        dependantPackageName -- Full name of the package, from the
                       project root, as a string
        dependencies -- Collection that contains the full names
                        names of any packages/modules that the
                        dependant package depends on
        depth -- Depth to prune name to. For example, if
                 depth = 1 then "a.b.c" will be pruned
                 to "a.b". Value must be an integer
                 greater than or equal to 0.


        """
        prunedDependantName = self.prunePackageName(dependantPackageName, depth)
        prunedDependencies = set()
        for dep in dependencies:
            prunedDep = self.prunePackageName(dep, depth)
            prunedDependencies.add(prunedDep)
        # Ensure recursive dependency isn't present
        if prunedDependantName in prunedDependencies:
            prunedDependencies.remove(prunedDependantName)
        return ( prunedDependantName, prunedDependencies )

    def prune(self, dependencies, depth):
        """Prune names of a collection of dependant modules and their dependencies.

        Any duplicate entries is the pruned dependency lists are moved.
        Additionally, the dependencies of any duplicate DEPENDANT package names
        are merged into a single dependency list.

        Arguments:
        dependencies -- Returns dictionary where the keys are the packages/modules
                        in the project and the values are packages/modules that
                        the respective key imported.
        depth -- Depth to prune package names to. For example, if depth = 1 then
                 "a.b.c" will be pruned to "a.b". Value must be an integer
                 greater than or equal to 0.

        """
        prunedDependencies = {}
        for dependantName, dependencyList in dependencies.items():
            prunedName, prunedSet = self.pruneDependencyList(
                dependantName, dependencyList, depth)
            try:
                # If there's alreayd some dependencies for the pruned dependant
                # module, merge the current pruned list with the existing list.
                # Duplicate values are removed using set union
                existingDeps = prunedDependencies[prunedName]
                mergedDeps = existingDeps.union( prunedSet )
                prunedDependencies[prunedName] = mergedDeps
            # If there are currently no dependencies for the pruned name
            except KeyError:
                prunedDependencies[prunedName] = prunedSet

        # Remove recursive dependencies that can result from pruning process
        # (e.g. "project.a -> project.a" is removed)
        for dependantName, dependencySet in prunedDependencies.items():
            if dependantName in dependencySet:
                dependencySet.remove(dependantName)

        return prunedDependencies