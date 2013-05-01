"""TODO"""

import os
import hashlib
import imp
import inspect


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


class OutputterFactory:

    """Constructs instances of outputters.

    Handles dynamically loading plugin modules and caching those
    modules to construct the desired instances.

    """

    def __init__(self, pluginDir):
        """Construct instance of OutputterFactory.

        Arguments:
        pluginDir -- Directory that contains outputter modules.
                     The constructed instance will use the given
                     directory to search for outputters.

        """
        if not isinstance(pluginDir, str):
            raise TypeError("Directory containing outputter plugins must be a string")
        absPluginDir = os.path.abspath(pluginDir)
        if not os.path.isdir(absPluginDir):
            raise IOError("'{}' is not a valid directory".format(pluginDir))

        self.pluginDirectory = absPluginDir
        self.moduleCache = {}

    def getOutputterFilename(self, outputterName):
        """Return filename of Python module containing requested outputter.

        Arguments:
        outputterName -- Name of the outputter to get the filename of

        """
        path = os.path.join( self.pluginDirectory, outputterName )
        return "{}.py".format(path)

    def loadOutputter(self, outputterName):
        """Dynamically load and return Python module containing outputter.

        Note that this method also stores the loaded module in
        the OutputterFactory instance's internal cache (moduleCache
        attribute).

        Raises IOError if the module doesn't exist.
        Raises RuntimeError if a class named Outputter is not defined
        by the loaded module or it is nota subclass of ResultOutputter

        Arguments:
        outputterName -- Name of the outputter whose module is to be
                         loaded

        """
        # Check if outputter is in the cache and loader
        if outputterName in self.moduleCache:
            return self.moduleCache[outputterName]

        # Compute filename of module to laodand check it exists
        moduleFilename = self.getOutputterFilename(outputterName)
        if not os.path.exists(moduleFilename):
            raise IOError("Outputter '{}' does not exist".format(outputterName))
        # Load the module
        hashedModuleName = hashlib.md5(moduleFilename.encode()).hexdigest()
        with open(moduleFilename, "rb") as fileStream:
            module = imp.load_source(hashedModuleName, moduleFilename, fileStream)
        # Check module has a class called "Outputter"
        outputterClassExists = False
        for name, obj in inspect.getmembers(module):
            outputterClassExists
            if inspect.isclass(obj) and name == "Outputter":
                outputterClassExists = True
        if not outputterClassExists:
            raise RuntimeError("Outputter '{}' did not contain a class called 'Outputter'".format(outputterName))
        # Check said class is a subclass of ResultOutputter
        if not issubclass(module.Outputter, ResultOutputter):
            raise RuntimeError("Outputter class must be a subclass of outputter.ResultOutputter")
        # Store module in cache
        self.moduleCache[outputterName] = module

        return module

    def createOutputter(self, outputterName, **kwargs):
        """Return new instance of outputter inside module with given name.

        Raises IOError if module for outputter with given game doesn't exist.
        Raises RuntimeError if a class named Outputter is not defined
        by the loaded module or it is not a subclass.

        Arguments:
        outputterName -- Name of the outputter to create

        Keyword arguments:
        kwargs -- Any keyword arguments to pass to the outputter class'
                  constructor can be passed in here.

        """
        #
        module = self.loadOutputter(outputterName)
        return module.Outputter(**kwargs)