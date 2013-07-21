"""Contains entrypoint logic for running moduledependency as a program."""

import sys
import os

from .cli import ArgumentProcessor
from .executor import Executor
from .outputter import OutputterFactory
from . import MODULEDEPENDENCY_DIR

# Directory which stores all the outputters
OUTPUTTER_DIRECTORY = os.path.join(MODULEDEPENDENCY_DIR, "outputters")

def run():
    """Main entrypoint into moduledependency program."""
    # Process command line arguments
    argProcessor = ArgumentProcessor()
    try:
        argProcessor.process(sys.argv)
    except BaseException as e:
        sys.exit(str(e))

    outputterFactory = OutputterFactory(OUTPUTTER_DIRECTORY)
    # If an outputter was specified, try and load it
    if argProcessor.outputterName:
        # Get all arguments that may be for the outputter (options
        # not recognised as being anythiing else by the argument processor)
        outputter = outputterFactory.createOutputter(argProcessor.outputterName, **argProcessor.getOutputterArguments())
    else:
        outputter = None

    # Create and configuration main dependency searcher
    executor = Executor()
    if outputter:
        executor.setOutputter(outputter)        
    try:
        executor.setMaximumDepth(argProcessor.maxDepth)
    except KeyError:
        pass

    if not argProcessor.getOption("quiet"):
        print("starting dependency extraction...")
    # Search for dependencies in the specified directory
    dependencies = executor.execute(argProcessor.projectDirectory)
    if not argProcessor.getOption("quiet"):
        print("...dependency extraction complete!")	