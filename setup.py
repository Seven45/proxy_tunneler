from os.path import join, dirname

from pip._internal.network.session import PipSession
from pip._internal.req import parse_requirements
from setuptools import setup, find_packages

long_description = open(join(dirname(__file__), 'README.rst'), 'r').read()

requirements = parse_requirements('requirements.txt', session=PipSession())
install_requires = [str(req.req) for req in requirements]


setup(name='ProxyTunneller',
      version='0.2.1',
      url='https://github.com/Seven45/ProxyTunneller',
      author='Dubrovin Semyon',
      author_email='seven45@mail.ru',
      description='Library for create proxy tunnels',
      long_description=long_description,
      packages=find_packages(),
      install_requires=install_requires,
      python_requires='>=3.7')
