from setuptools import setup
from setuptools import Extension

from Cython.Build import cythonize

setup(
    name='yahtr',
    ext_modules=cythonize('core/*.pyx'),
)
