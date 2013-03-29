"""TODO"""

class ResultOutputter:

    """Interface for outputting results of a dependency search."""

    def createOutput(self, dependencies):
        """Output result of dependency search in some way.

        This method must be implemented by subclasses.

        Arguments:
        dependencies -- Dictionary where the keys are package/module
                        names and the values are packages/modules that
                        their respective keys imported.
                        Both keys and values should be strings.

        """
        raise NotImplementedError