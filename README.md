# moduledependency

moduledependency is a Python program that scans Python projects and extracts
inter-project dependencies between packages/modules.

### Install

**NOTE**: moduledependency only supports Python 3.0.0+. There is *no* Python 2 support!

Clone the repository and execute the setup file:

```
python setup.py install
```

The [fileprocessor](https://github.com/DonaldWhyte/fileprocessor) package must also be installed.

### Usage

As well as being a package which can be used in other Python programs, moduledependency can be run as a standalone program. This program scans a given project directory recursively and extracts project-level module dependencies from any found Python packages/modules. These extracted dependencies are then outputted to stdout or to a file in a particular format.

Running moduledependency as a program can be achieved on the command line like so:

```
python -m moduledependency --project=<projectDir> {flags}
```

Note that this command assumes that the user's working directory is the directory which contains the moduledependency package. The `-m` Python flag means that we're using the moduledependency package as the main entry point to the program. `<projectDir>` should be a path to the root directory of the Python project/package to extract dependencies from.

In addition to specifying the project directory, there are a number of other arguments that can be used to configure how moduledependency runs, which are listed in the table below.

| **Argument** | **Description** |
| ------------ | --------------- |
| `--outputter={outputterName}` or `-o={outputterName}` | This specifies that a custom outputter should be used to generate the format of the extracted dependencies. `{outputterName{` is the name of custom outputter. See the "Using Custom Outputters" section for more information. |
| `--depth={depth}` or `-d={depth}` | `{depth}` is a number which specifies how deep the resultant dependency tree should go into the packages/modules. See the "Specifying Depth" section for more information. |
| `--quiet` or `-q` | If this flag is provided, then the only thing that will be outputted to *stdout* is the found dependencies. No additional reporting will be provided. |

#### Using Different Outputters

An `outputter` is a plugin which determines how the extracted dependencies are presented to the user. The outputted data could be XML, a visual graph, JSON and so on. Within the moduledependency package there is a directory called `outputters`, which contains all of the outputters that can be used. The table below lists the built-in outputters that come with moduledependency.

| **Outputter** | **Description** |
| ------------ | --------------- |
| dot | Outputs dependencies as a .dot graph specification file. This file can used with graph rendering packages such as GraphViz to generate a visual representation of a project's dependencies. |
| python | Outputs dependencies as a Python dictionary contained inside a module. |
| xml | Outputs dependencies as an XML file. |

This means that the `outputters` directory initially contains three Python modules - `dot.py`, `python.py` and `xml.py`. The *name* of an outputter (to use in the command line arguments) is the *name* of the Python module which contains the outputter.

For example, to extract dependencies as a dot script file you'd run moduledependency like so:

`
python -m moduledependency --project=<projectDir> --outputter=dot
`

To add another outputter to use, simply add the Python module containing the outputter to the `outputters` directory. For more information about creating your own outputters, see the "Writing Custom Outputters" section.

#### Specifying Depth

Suppose we were scanning a project called `example`, which has the following module hierarchy:

  * a
    * b
       * c
       * d
           * e
    * f
  * g
    * h
        * i
  * j

Now suppose the dependencies between these modules are like so:

  * a.b -> g.h.i
  * a.b -> j
  * a.b -> a.f
  * a.b.c -> a.b.d
  * a.b.d.e -> g.h
  * g -> j
  * g.h.i -> a.b.c
  * g.h.i -> a.b.d.e

The list of dependencies above goes quite deep into the module hierarchy. If you have a large Python project with deep module hierarchies, the list of dependencies can sometimes become very large. These large lists don't really tell you much about the _high level structure_ of dependencies in your project. 

This is why moduledependency has the ability to _abstract_ lower-level dependencies and limit how deep the extracted dependencies go. *depth* specifies how deep the displayed dependencies in the scanned project's package/module hierarchy will go. If `depth = 0` when extracting dependencies from `example`, only the top-level of the module hierarchy will be considered, resulting in the following dependencies:

`example` project with `depth = 0`:

* a -> g
* a -> j
* g -> a
* g -> j

Note how the `a` package never used `g` directly, but it's still considered a dependency. This is because `a`'s sub-modules did; if the `a` package indirectly uses `g` through its children, then it's said that `a` uses `g` when depth is limited.

Further examples illustrating how depth limiting works are shown below.

`example` project with `depth = 1`:

* a.b -> g.h
* a.b -> j
* a.b -> a.f
* g -> j
* g.h -> a.b

`example` project with `depth = 2`:

* a.b -> g.h.i
* a.b -> j
* a.b -> a.f
* a.b.c -> a.b.d
* a.b.d -> g.h
* g -> j
* g.h.i -> a.b.c
* g.h.i -> a.b.d

`example` project with `depth = 3`:

* a.b -> g.h.i
* a.b -> j
* a.b -> a.f
* a.b.c -> a.b.d
* a.b.d.e -> g.h
* g -> j
* g.h.i -> a.b.c
* g.h.i -> a.b.d.e

Notice how with `depth = 3`, we have the same dependency list as we when we never limited the depth. This is because the depth has become large enough to include the lowest levels of the module tree in `example`.

A depth limit can be specified using the `--depth` command line argument.

### Writing Custom Outputters

#### An Outputter is a Module

An *outputter* is a Python module which contains a class called `Outputter`. This class must be a subclass of `moduledependency.outputters.ResultOutputter` and implement the `createOutput()` method. This method takes the extracted dependencies as a Python dictionary and returns some new representation of the dependencies (e.g. outputting said dependencies to a file).

To be more specific, `createOutput()` takes a single argument `dependencies`, which is dictionary where the *keys* are package/module names and the values are lists of packages/modules that their respective keys imported. Both keys and values are *strings* containing the names of the packages/modules.

If `createOutput()` returns a value, that value will be outputted to *stdout* by the moduledependency program. If nothing is returned (e.g. the generated output was sent to a file instead), then moduledependency remains silent.

#### Installing an Outputter

To install an outputter, place the module which contains the `Outputter` class into the `moduledependency/outttpuers` directory. Ensure that the name of the module/outputter does not clash with any existing outputters installed.

To use the outputter, use the *name* of the Python module containing the outputter as the outputter name in the command line arguments:

```
python -m moduledependency --project=<projectDir> --outputter=<outputterModuleName>
```

#### Custom Outputter Arguments

It is possible to pass custom arguments to outputters through the command line. Any arguments with names that are *not reserved* are treated as outputter arguments.

Reserved argument names:

* --project/-p
* --depth/-d
* --outputter/-o
* --quiet/-q

Arguments are passed to the `Outputter` class' *constructor* as *keyword arguments*. This means that if an outputter argument is given, but the specified outputter's constructor *does not* take that keyword argument, an error is raised. As such, users should only specify outputter arguments that their chosen outputter actually supports.

#### Example Outputter

Suppose we wanted to generate a JSON representation of a project's module dependencies. We could achieve this by creating a new outputter called `json`. To do this, we define a class called `Outputter` (which inherits from `ResultOutputter` and implements the `createOutput()` method) in a file called `json.py`.

Let's also say that we want the outputter to be able to store the generated JSON to a file *or* output the JSON via stdout. To do this, we'll define an outputter argument called `filename`. If this argument is given, then the generated JSON will be stored in a file. Otherwise, it will be displayed on the command line.

**json.py:**

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

If a filename is provided through the command line, then the generated JSON will be written to a file with the given name. Otherwise, the JSON will be just be sent to stdout and displayed on the command line.

As an example, to extract dependencies from a project called `example` and store them in a JSON file called `dependencies.js`, we would run moduledependency like so:

```
python -m moduledependency --project=example --outputter=json --filename=dependencies.js
```

And if we just wanted to output the JSON to the command line we'd use:

```
python -m moduledependency --project=example --outputter=json 
```

### Tests

Unit tests are provided in the 'tests' directory. To run all the unit tests simply navigate into the 'tests' directory and invoke the following command:

```
python run_test.py -d .. -w .
```

To run a single test file, invoke the following command in the 'tests' directory:

```
python run_test.py -d .. -w . -t TEST_NAME
```

`TEST_NAME` is the name of the test file without the "test_" prefix or ".py" suffix. For example, if `TEST_NAME = filterers`, then the test file "test_filterers.py" will be executed.

### Architecture

A diagram illustrating moduledependency's architecture is given below.

![moduledependency Architecture Diagram](https://raw.github.com/DonaldWhyte/module-dependency/master/docs/moduledependency_architecture.png)

### Source Code

Git repository can be accessed here: https://github.com/DonaldWhyte/module-dependency/

LICENCE
-------

fileprocess is licensed under the MIT License. See LICENCE for more information.
