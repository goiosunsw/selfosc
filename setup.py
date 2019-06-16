
from setuptools import setup

import unittest
def my_tests():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    return test_suite

setup(name='selfosc',
      version='0.1',
      description='Self oscillating valves coupled to acoustic resonators',
      url='http://github.com/goiosunw/selfosc',
      author='Andre Goios',
      author_email='a.almeida@unsw.edu.au',
      license='GPL v3',
      packages=['selfosc' ],
      test_suite = 'setup.my_tests',
      zip_safe=False)

