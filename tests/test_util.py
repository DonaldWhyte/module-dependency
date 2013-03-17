import unittest
import sys
import os
import platform
sys.path.append(os.environ.get("PROJECT_ROOT_DIRECTORY", "."))

from moduledependency.util import *

class TestUtil(unittest.TestCase):

	def test_getProjectRoot(self):
		# Test empty path
		with self.assertRaises(ValueError):
			getProjectRoot("")
		# Test root path
		if platform.system() == "Windows":
			self.assertEqual(getProjectRoot("C:\\"), "")
		elif platform.system() == "Unix" or platform.system() == "Linux":
			self.assertEqual(getProjectRoot("/"), "")
		# Test valid paths
		if platform.system() == "Windows":
			self.assertEqual(getProjectRoot("C:\\System\\Win32"), "Win32")
			self.assertEqual(getProjectRoot("C:\\System"), "System")		
		elif platform.system() == "Unix" or platform.system() == "Linux":
			self.assertEqual(getProjectRoot("/opt/python"), "python")
			self.assertEqual(getProjectRoot("/opt"), "opt")
