# Program Usage Guide #

### Invoking the Program ###

As well as being a package which can be used in other Python programs, `moduledependency` can be run as a standalone program. This program scans a given project directory recursively and extracts project-level module dependencies from any found Python packages/modules. These extracted dependencies are then outputted to the **stdout** stream or  to a file in a particular format (depending on how the program is configured using command line arguments).

Running `moduledependency` as a program can be achieved on the command line like so:

```
python -m moduledependency --project=<projectDir> {flags}
```

Note that this command assumes that the user's working directory is the directory which contains the `moduledependency` _package_. The `-m` Python flag means that we're using the `moduledependency` package as the main entry point to the program. `<projectDir>` should be a path to the root directory of the Python project/package to extract dependencies from.

In addition to specifying the project directory, there are a number of other arguments that can be used to configure how `moduledependency` runs.

List of arguments:
| **Argument** | **Description** |
|:-------------|:----------------|
| **--outputter={outputterName}** or **-o={outputterName}** | This specifies that a custom outputter should be used to generate the format of the extracted dependencies. `{outputterName`} is the name of custom outputter. See the "Using Custom Outputters" section for more information. |
| **--depth={depth}** or **-d={depth}** | `{depth`} is a number which specifies how deep the resultant dependency tree should go into the packages/modules. See the "Specifying Depth" section for more information. |
| **--quiet** or **-q** | If this flag is provided, then the only thing that will be outputted to **stdout** is the found dependencies. No additional reporting will be provided. |

### Using Different Outputters ###

An `outputter` is a plugin which determines how the extracted dependencies are presented to the user. The outputted data could be XML, a visual graph, JSON and so on. Within the `moduledependency` package there is a directory called `outputters`, which contains all of the outputters that can be used. The table below lists the built-in outputters that come with `moduledependency`.

| **Outputter** | **Description** |
|:--------------|:----------------|
| dot | Outputs dependencies as a `.dot` graph specification file. This file can used with graph rendering packages such as [GraphViz](http://www.graphviz.org/) to generate a visual representation of a project's dependencies. |
| python | Outputs dependencies as a Python dictionary contained inside a module. |
| xml | Outputs dependencies as an XML file. |

This means that the `outputters` directory initially contains three Python modules - `dot.py`, `python.py` and `xml.py`. The **name** of an outputter (to use in the command line arguments) is the **name** of the Python module which contains the outputter.

For example, to extract dependencies as a dot script file you'd run `moduledependency` like so:

```
python -m moduledependency --project=<projectDir> --outputter=dot
```

To add another outputter to use, simply add the Python module containing the outputter to the `outputters` directory. For more information about creating your own outputters, see WritingCustomerOutputters.

### Specifying Depth ###

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

This is why `moduledependency` has the ability to _abstract_ lower-level dependencies and limit how deep the extracted dependencies go. **depth** specifies how deep the displayed dependencies in the scanned project's package/module hierarchy will go. If `depth = 0` when extracting dependencies from `example`, only the top-level of the module hierarchy will be considered, resulting in the following dependencies:

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

To specify a depth limit, the `--depth={depth`} command line argument can be used (where `{depth`} is an integer >= 0).