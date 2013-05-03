from moduledependency.outputter import ResultOutputter

# TODO: write docstrings
# TODO: in docstrings make sure to mention that the generated output
# can also be used as JSON as well as Python

class Outputter(ResultOutputter):

    def __init__(self, filename=None):
        self.filename = filename

    def createOutput(self, dependencies):
        output = self.generateDictionary(dependencies)
        # If a filename is set, be sure to write output to file
        if self.filename:
            with open(self.filename, "w") as f:
                f.write(output)
        return output

    def generateDependencyList(self, dependencyList):
        output = ""
        for dep in sorted(dependencyList):
            output += '"{}", '.format(dep)
        # Remove trailing comma
        if len(output) > 0:
            output = output[:-2]
        return "[ {} ]".format(output)

    def generateDictionaryEntry(self, dependantModuleName, dependencyList):
        generatedList = self.generateDependencyList(dependencyList)
        output = '"{}" : {}, '.format(dependantModuleName, generatedList)
        return output

    def generateDictionary(self, dependencies):
        output = ""
        # Sort all the dependant modules to ave consistent output
        dependantModules = sorted(dependencies.keys())
        for depModName in dependantModules:
            output += self.generateDictionaryEntry(depModName, dependencies[depModName])
        if len(output) > 0:
            output = output[:-2]
        return "{{ {} }}".format(output)