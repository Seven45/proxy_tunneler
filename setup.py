from os.path import join, dirname

from setuptools import setup, find_packages

long_description = open(join(dirname(__file__), 'README.rst'), 'r').read()

install_requires = open((join(dirname(__file__), 'requirements.txt')), 'r').readlines()
install_requires = list(map(lambda line: line.replace('\n', ''), install_requires))


setup(name='ProxyTunneller',
      version='0.2.0',
      url='https://github.com/Seven45/ProxyTunneller',
      author='Dubrovin Semyon',
      author_email='seven45@mail.ru',
      description='Library for create proxy tunnels',
      long_description=long_description,
      packages=find_packages(),
      install_requires=install_requires,
      python_requires='>=3.7')
