from moduledependency.outputter import ResultOutputter

# TODO: write docstrings

class Outputter(ResultOutputter):

    XML_TEMPLATE = "<xml><dependencies>{}</dependencies></xml>"
    DEPENDANT_TEMPLATE = '<dependant name="{}">{}</dependant>'
    DEPENDENCY_TEMPLATE = '<dependency>{}</dependency>'

    def __init__(self, filename=None):
        self.filename = filename

    def createOutput(self, dependencies):
        output = self.generateXML(dependencies)
        # If a filename is set, be sure to write output to file
        if self.filename:
            with open(self.filename, "w") as f:
                f.write(output)
        return output

    def generateDependency(self, dependencyName):
        return self.DEPENDENCY_TEMPLATE.format(dependencyName)

    def generateDependant(self, dependantModuleName, dependencyList):
        # Ensure list is sorted f
        xmlList = "".join( [ self.generateDependency(dep) for dep in sorted(dependencyList) ] )
        return self.DEPENDANT_TEMPLATE.format(dependantModuleName, xmlList)

    def generateXML(self, dependencies):
        xmlList = ""
        dependantModules = sorted(dependencies.keys())
        for dependantName in dependantModules:
            xmlList += self.generateDependant(dependantName, dependencies[dependantName])
        return self.XML_TEMPLATE.format(xmlList)        