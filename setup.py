#!/usr/bin/env python

from distutils.core import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='Dotatmo',
      version='0.1',
      description='Indoor environment monitor',
      author='Bastien Wirtz',
      author_email='bastien.wirtz@gmail.com',
      url='https://github.com/bastienwirtz/dotatmo',
      packages=['dotatmo'],
      install_requires=requirements,
      entry_points={
          'console_scripts': [
              'dotatmo = dotatmo.app'
          ]
      },
     )
