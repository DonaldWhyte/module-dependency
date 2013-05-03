from moduledependency.outputter import ResultOutputter

# TODO: write docstrings
# TODO: in docstrings make sure to mention that the generated output
# can also be used as JSON as well as Python

class Outputter(ResultOutputter):

    GRAPH_FORMAT = "graph dependencies {{\n{}}}"
    NODE_FORMAT = "\t{};\n"
    EDGE_FORMAT = "\t{} -> {};\n"

    def __init__(self, filename=None):
        self.filename = filename

    def createOutput(self, dependencies):
        output = self.generateGraph(dependencies)
        # If a filename is set, be sure to write output to file
        if self.filename:
            with open(self.filename, "w") as f:
                f.write(output)
        return output

    def generateDependency(self, dependant, dependancy):
        return self.EDGE_FORMAT.format(dependant, dependancy)

    def generateDependant(self, dependant):
        return self.NODE_FORMAT.format(dependant)

    def generateGraph(self, dependencies):
        output = ""
        dependants = sorted(dependencies.keys()) # sorted so results are consistent
        # First make sure all dependants are defined
        for dependant in dependants:
            output += self.generateDependant(dependant)
        # Now make each dependency an edge in the graph
        for dependant in dependants:
            for dependency in dependencies[dependant]:
                output += self.generateDependency(dependant, dependency)
        return self.GRAPH_FORMAT.format(output)