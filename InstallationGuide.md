# Installation Guide #

### Pre-requisites ###

moduledependency has a single dependency - the **[fileprocessor](https://code.google.com/p/fileprocessor)** package. This must be installed on your Python installation before using moduledependency.

Also note that moduledependency **only supports Python 3.0.0+**. There is **no** Python 2 support!

### Installation ###

Installing moduledependency package is achieved by running a Python installation script. After downloading moduledependency, open a terminal and navigate to the **root** directory of the project. This directory should contain a script called `setup.py`. Run the command:

```
python setup.py install
```

to install moduledependency on your existing Python installation. Note that you may need administrator/root access for this.

After running the script, the moduledependency package can be used by your other Python scripts and projects. To ensure the installation was successful, open an interaction Python session by calling `python` in a terminal and writing:

```
import moduledependency
```

If no error is thrown, then the installation was successful.