#!/usr/bin/env python3

from setuptools import setup

setup(name='aberquota',
      version='1.01',
      description='Python3 tool for getting internet usage off the Aberystwyth University network',
      classifiers=[
      	'Development Status :: 3 - Alpha',
      	'Programming Language :: Python :: 3 :: Only'
      ],
      url='https://github.com/Jafnee/aberquota',
      author='Jafnee Jesmee',
      author_email='jafneejesmee@gmail.com',
      packages=['aberquota'],
      install_requires=['requests', 'BeautifulSoup4'],
      scripts=['bin/aberquota'],
      zip_safe=False)