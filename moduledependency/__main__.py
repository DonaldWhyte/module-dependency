import sys

from .cli import ArgumentProcessor
from .executor import Executor
from .outputter import OutputterFactory

if __name__ == "__main__":
    # Process command line arguments
    argProcessor = ArgumentProcessor()
    try:
        argProcessor.process(sys.argv)
    except BaseException as e:
        sys.exit(str(e))

    outputterFactory = OutputterFactory("moduledependency/outputters")
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
        executor.setMaximumDepth(argProcessor.getOption("depth"))
    except KeyError:
        pass

    if not argProcessor.getOption("quiet"):
        print("starting dependency extraction...")
    # Search for dependencies in the specified directory
    dependencies = executor.execute(argProcessor.projectDirectory)
    if not argProcessor.getOption("quiet"):
        print("...dependency extraction complete!")