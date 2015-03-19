# Writing Customer Outputters #

### Outputter is a Module ###

An **outputter** is a Python module which contains a class called `Outputter`. This class must be a subclass of `moduledependency.outputters.ResultOutputter` and implement the `createOutput()` method. This method takes the extracted dependencies as a Python dictionary and returns some new representation of the dependencies (e.g. outputting said dependencies to a file).

To be more specific, `createOutput()` takes a single argument `dependencies`, which is dictionary where the **keys** are package/module names and the values are lists of packages/modules that their respective keys imported. Both keys and values are **strings** containing the names of the packages/modules.

If `createOutput()` returns a value, that value will be outputted to **stdout** by the `moduledependency` program. If nothing is returned (e.g. the generated output was sent to a file instead), then `moduledependency` remains silent.

### Installing an Outputter ###

To install an outputter, place the module which contains the `Outputter` class into the `moduledependency/outttpuers` directory. Ensure that the name of the module/outputter does not clash with any existing outputters installed.

To use the outputter, use the **name** of the Python module containing the outputter as the outputter name in the command line arguments:

```
python -m moduledependency --project=<projectDir> --outputter=<outputterModuleName>
```

### Custom Outputter Arguments ###

It is possible to pass custom arguments to outputters through the command line. Any arguments with names that are _not reserved_ are treated as outputter arguments.

List of reserved argument names:
  * --project/-p
  * --depth/-d
  * --outputter/-o
  * --quiet/-q

Arguments are passed to the `Outputter` class' **constructor** as **keyword arguments**. This means that if an outputter argument is given, but the specified outputter's constructor _does not_ take that keyword argument, an error is raised. As such, user's should **only specify outputter arguments that their chosen outputter actually supports**.

### Example Outputter ###

Suppose we wanted to generate a JSON (JavaScript Object Notation) representation of a project's module dependencies. We could achieve this by creating a new outputter called `json`. To do this, we define a class called `Outputter` (which inherits from `ResultOutputter` and implements the `createOutput()` method) in a file called `json.py`.

Let's also say that we want the outputter to be able to store the generated JSON to a file **or** output the JSON via stdout. To do this, we'll define an outputter argument called `filename`. If this argument is given, then the generated JSON will be stored in a file. Otherwise, it will be displayed on the command line.

`json.py`:
```
from moduledependency.outputter import ResultOutputter
# Luckily Python has a module which can directly convert a Python dictionary to JSON already
import json

class Outputter(ResultOutputter):

    # This is where the outputter takes outputter arguments.
    # They MUST be keyword arguments.
    def __init__(self, filename=None):
        super().__init__() # call superclass constructor
        self.filename = filename

    def createOutput(self, dependencies):
        # Generate custom output
        generatedJSON = json.dumps(dependencies)
        # If user specified a filename, output JSON to file and not command line
        if self.filename:
            with open(self.filename, "w") as f:
                f.write(generatedJSON)
            return None
        # Otherwise, just output JSON to command line by returning it
        else:
            return generatedJSON

```

After writing the outputter, we place the module file (`json.py`) in `moduledependency/outputters`. Now the outputter can be used like so:

```
python -m moduledependency --project=<projectDir> --outputter=json {--filename=<jsonFilename>}
```

If a filename is provided through the command line, then the generated JSON will be written to a file with the given name. Otherwise, the JSON will be just be sent to **stdout** and displayed on the command line.

As an example, to extract dependencies from a project called `example`  and store them in a JSON file called `dependencies.js`, we would run `moduledependency` like so:

```
python -m moduledependency --project=example --outputter=json --filename=dependencies.js
```

And if we just wanted to output the JSON to the command line we'd use:

```
python -m moduledependency --project=example --outputter=json 
```