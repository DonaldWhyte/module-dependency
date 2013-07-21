from distutils.core import setup
import os
import moduledependency


currentFileDirectory = os.path.dirname(__file__)
with open(os.path.join(currentFileDirectory, "README"), "r") as f:
	readme = f.read()

setup(
	name="moduledependency",
	version=moduledependency.VERSION,
	description="Tool used to search for and visualise dependencies between packages/modules in Python projects",
	long_description=readme,
	author="Donald Whyte",
	author_email="donaldwhyte0@gmail.com",
	url="http://code.google.com/p/module-dependency",
	classifiers=[
		"Development Status :: 3 - Alpha Development Status"
		"Intended Audience :: Developers",
		"Programming Language :: Python 3",
		"Programming Language :: Python 3.2",
		"Programming Language :: Python 3.3",
	],
	keywords="dependency module searcher project automatic code analysis generator",
	license="MIT",
	packages=("moduledependency",),
	data_files=[ (".", ["LICENCE"]) ]
)