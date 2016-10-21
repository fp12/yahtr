from distutils.core import setup
from Cython.Build import cythonize

setup(
    name='yahtr',
    ext_modules=cythonize('core/*.pyx'),
)
