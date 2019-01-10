
from setuptools import setup, find_packages

VERSION = '0.0.1a0'

f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
  name='confdict',
  version=VERSION,
  description='Various utilities for automating common tasks during development of JotForm!',
  long_description=LONG_DESCRIPTION,
  long_description_content_type='text/markdown',
  author='Mehmet Can Ozdemir',
  author_email='mefu.ozd@gmail.com',
  url='https://github.com/mefu/confdict/',
  license='unlicensed',
  packages=find_packages(exclude=['ez_setup', 'tests*']),
  include_package_data=True,
)
