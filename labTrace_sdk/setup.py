from distutils.core import setup
from setuptools import find_packages

setup(name='labtrace-sdk-py',
      version='1.0.0',
      packages=find_packages(),
      install_requires=['requests>=2.22.0,<3', 'PyJWT>=1.7.1,<2'],
      description='Labtrace Api sdk',
      author='Chainside',
      author_email='francesco.andreozzi@chainside.net',
      python_requires='>=3.8',
      keywords=['sdk', 'api', 'labtrace'])