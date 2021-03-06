#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2014

# Author(s):

# Panu Lahtinen <panu.lahtinen@fmi.fi>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Setup for halostack
"""
from setuptools import setup
import imp
from halostack import __version__
# version = imp.load_source('halostack.version', 'halostack/version.py')

setup(name="halostack",
      version=__version__,
      description='Halostack for stacking and enhancing halo photos',
      author='Panu Lahtinen',
      author_email='pnuu+git@iki.fi',
      classifiers=["Development Status :: 3 - Alpha",
                   "Intended Audience :: Science/Research",
                   "License :: OSI Approved :: GNU General Public License v3 " +
                   "or later (GPLv3+)",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Topic :: Scientific/Photography"],
      url="https://github.com/pnuu/halostack",
      packages=['halostack'],
      zip_safe=False,
      install_requires=[],
      test_suite = 'nose.collector',
      )


