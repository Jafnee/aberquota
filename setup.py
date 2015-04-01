#!/usr/bin/env python3

from setuptools import setup

setup(name='aberquota',
      version='1.0',
      description='Python3 tool for getting internet usage off the Aberystwyth University network',
      url='https://github.com/Jafnee/aberquota',
      author='Jafnee Jesmee',
      author_email='jafneejesmee@gmail.com',
      packages=['aberquota'],
      install_requires=['requests', 'BeautifulSoup4'],
      scripts=['bin/aberquota'],
      zip_safe=False)