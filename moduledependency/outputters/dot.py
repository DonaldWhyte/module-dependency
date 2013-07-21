import re
from moduledependency.outputter import ResultOutputter

# TODO: write docstrings
# TODO: in docstrings make sure to mention that the generated output
# can also be used as JSON as well as Python

class Outputter(ResultOutputter):

    GRAPH_FORMAT = "digraph dependencies {{\n{}}}"
    NODE_FORMAT = "\t{};\n"
    EDGE_FORMAT = "\t{} -> {};\n"

    EMPTY_NODE_ID = "__NULL__"
    DISALLOWED_NODE_CHARACTERS_REGEX = re.compile( r"\W" )
    DIGIT_REGEX = re.compile( r"\d" )
    REPLACEMENT_CHARACTER = "_"

    def __init__(self, filename=None):
        self.filename = filename

    def createOutput(self, dependencies):
        output = self.generateGraph(dependencies)
        # If a filename is set, be sure to write output to file
        if self.filename:
            with open(self.filename, "w") as f:
                f.write(output)
        return output

    def sanitiseNodeID(self, nodeID):
        # If ID is empty, return placeholder
        if len(nodeID) == 0:
            return self.EMPTY_NODE_ID
        # Only replace non-word characters INSIDE surrounding quotes
        if self.surroundedByQuotes(nodeID):
            return '"{}"'.format( self.replaceNonWordCharacters(nodeID[1:-1]) )
        # Replace first character if it's a digit
        if self.isDigit(nodeID[0]):
            nodeID = self.REPLACEMENT_CHARACTER + nodeID[1:]
        return self.replaceNonWordCharacters(nodeID)

    def isDigit(self, character):
        return self.DIGIT_REGEX.match(character)

    def surroundedByQuotes(self, string):
        return (len(string) >= 3 and string[0] == '"' and string[-1] == '"')

    def replaceNonWordCharacters(self, string):
        return self.DISALLOWED_NODE_CHARACTERS_REGEX.sub( self.REPLACEMENT_CHARACTER, string )

    def generateDependency(self, dependant, dependency):
        startNode = self.sanitiseNodeID(dependant)
        endNode = self.sanitiseNodeID(dependency)
        return self.EDGE_FORMAT.format(startNode, endNode)

    def generateDependant(self, dependant):
        node = self.sanitiseNodeID(dependant)
        return self.NODE_FORMAT.format(node)

    def generateGraph(self, dependencies):
        output = ""
        dependants = sorted(dependencies.keys()) # sorted so results are consistent
        # Now make each dependency an edge in the graph
        for dependant in dependants:
            currentDependencies = dependencies[dependant]
            # If the module has NO dependencies,  generate a single node for it.
            if len(currentDependencies) == 0:
                output += self.generateDependant(dependant)
            else:
                for dependency in currentDependencies:
                    output += self.generateDependency(dependant, dependency)
        return self.GRAPH_FORMAT.format(output)
