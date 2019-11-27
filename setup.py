from setuptools import setup, find_packages
from os.path import join, dirname


setup(name='ProxyTunneller',
      version='0.0.1',
      url='https://github.com/Seven45/ProxyTunneller',
      author='Dubrovin Semyon',
      author_email='seven45@mail.ru',
      description='Library for create proxy tunnels',
      long_description=open(join(dirname(__file__), 'README.rst'), 'r').read(),
      packages=find_packages(),
      python_requires='>=3.7')
