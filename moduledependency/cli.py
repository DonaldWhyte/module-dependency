"""Contains functionality for parsing commmand line arguments
into data that can be retrieved easily.

"""

import re

class ArgumentProcessor:

    """Processes command line arguments and stores processed data in fields that can be accessed."""

    # Options that must be specified. Each value is a tuple of strings,
    # where each tuple rperesents the possible names of a mandatory option.
    MANDATORY_OPTIONS = [("p", "project")]

    # Message printed when help option specified or there are 
    # not enough arguments
    USAGE_MESSAGE = """
    Usage: python test.py

    Type -h or --help to display this message.

    ===REQUIRED ARGUMENTS===
    Set project to generate dependencies for:
    -p=[project_directory]
    --project=[project_directory]

    ===OPTIONAL ARGUMENTS===
    Silence command line output:
    -q
    --quiet

    Set depth of produced dependency data:
    -d=[depth]
    --depth=[depth]

    Set outputter to produce representation of dependency data:
    -o=[outputter_name]
    --outputter=[outputter]

    Set custom parameters for chosen outputter:
    --[outputter_param_name]=[outputter_param_value]

    """
    # Reglar expression used to match values wrapped by quotes
    STRING_REGEX = re.compile(r"^([\"\']).*\1$")

    def __init__(self):
        """Construct instance of ArgumentProcessor."""
        self.options = {}
        
    def process(self, args):
        """Raises RuntimeError if there's an error in the arguments
        given that cannot be recovered from.

        Arguments:
        args -- List of command line arguments given

        """
        self.checkForUsageMessage(args)
        self.options = self.parseOptions(args[1:]) # remove the program name
        # Check for specific options and validate them
        if "d" in self.options:
            self.maxDepth = self.validateDepth(self.options["d"])
        elif "depth" in self.options:
            self.maxDepth = self.validateDepth(self.options["depth"])
        if "o" in self.options:
            self.outputterName = self.options["o"]
        elif "outputter" in self.options:
            self.outputterName = self.options["outputter"]
        else:
            self.outputterName = None

        if not self.checkMandatoryOptions(self.options):
            raise RuntimeError("Not all mandatory options have been specified")

    def getOption(self, optionName):
        """Return value of option with given name parsed from arguments.

        If no vaue for that option exists, then a KeyError is raised.

        Arguments:
        optionName -- Name of option whose value should be returned

        """
        return self.options[optionName]

    def checkMandatoryOptions(self, options):
        """Return True if all mandatory options are present and False otherwise."""
        # Ensure all mandatory options have been specified
        for optionNames in self.MANDATORY_OPTIONS:
            present = False
            for option in optionNames:
                if option in self.options:
                    present = True
                    break
            if not present:
                return False
        return True # if we reach here, all options are present

    def checkForUsageMessage(self, args):
        """Check arguments and raise RuntimeError containing usage/help message if appropriate.

        If command line arguments are empty (apart from program name)
        or "-h" or "--help" was specified, then the exception is raised.

        Arguments:
        args -- List of command line arguments given

        """
        if (len(args) < 2) or ("-h" in args) or ("--help" in args):
            raise RuntimeError(self.USAGE_MESSAGE)

    def parseOptions(self, args):
        """Parse command line arguments into key-value pairs.

        Returns dictionary where the keys are the names of the
        options anddthe vlaues are the value specified for the
        associated option.

        For example, "-d=3 --something=test" would return the
        dictionary { "d" : "3", "something" : "test }.

        A RuntimeError is raised if the options are syntactically
        incorrect.

        Arguments:
        args -- List of command line arguments given

        """
        options = {}
        # Process each argument
        for arg in args:
            keyAndValue = arg.split("=")
            key = self.sanitiseKey( keyAndValue[0] )
            if len(keyAndValue) == 1:
                raise RuntimeError("No value specified for option '{}'".format(key))
            elif len(keyAndValue) == 2:
                value = ""
                try:
                    value = self.sanitiseValue( keyAndValue[1] )
                except ValueError:
                    raise RuntimeError("No value for option '{}' specified".format(key))
                options[key] = value
            else:
                raise RuntimeError("More than one '=' for option '{}', cannot determine value".format(key))
        return options

    def sanitiseKey(self, key):
        """Return sanitised option name, raising RuntimeError if name is invalid.

        Arguments:
        key -- Name of the option to sanitise

        """
        # Count number of dashes key begins with
        numPrefixDashes = 0
        while key[numPrefixDashes] == "-":
            numPrefixDashes += 1

        if numPrefixDashes == 0:
            raise ValueError("Invalid option name given (no dashes)")
        elif numPrefixDashes > 2:
            raise ValueError("Too many dashes prefix option name ({})".format(numPrefixDashes))

        # Remove prefixing dashes
        sanitisedKey = key[numPrefixDashes:]
        # If the sanitised key's length is greather than one and only one
        # dash is used, this is invalid use of command line arguments
        if numPrefixDashes == 1 and len(sanitisedKey) > 1:
            raise ValueError("Option name must be a single character if short arg name given (one dash prefixing)")

        return sanitisedKey

    def sanitiseValue(self, value):
        """Return sanitised option value, removing surrounding quotes.

        Arguments:
        value -- Value to sanitise

        """
        if len(value) == 0:
            raise ValueError("No value for option specified")
        if self.STRING_REGEX.match(value):
            return value[1:-1]
        else:
            return value

    def validateDepth(self, depth):
        """Convert string into positive integer and return result.

        If string does not represent an integer or that integer
        is negative, then a ValueError is raised.

        Arguments:
        depth -- Stirng containing positive integer

        """
        try:
            depth = int(depth)
        except ValueError: # make error message nicer
            raise ValueError("Invalid depth '{}' provided".format(depth))
        if depth < 0:
            raise ValueError("Maximum depth cannot be negative")
        return depth