from os.path import join, dirname

from setuptools import setup, find_packages

long_description = open(join(dirname(__file__), 'README.rst'), 'r').read()


setup(name='ProxyTunneller',
      version='0.3.2',
      url='https://github.com/Seven45/ProxyTunneller',
      author='Dubrovin Semyon',
      author_email='seven45@mail.ru',
      description='Library for create proxy tunnels',
      long_description=long_description,
      packages=find_packages(),
      install_requires=['pproxy', 'aiohttp', 'aiosocksy'],
      python_requires='>=3.7')
