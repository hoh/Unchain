#!/usr/bin/env python3
# coding: utf-8

# Copyright (c) 2015 "Hugo Herter http://hugoherter.com"
#
# This file is part of Unchain.
#
# Intercom is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup

setup(name='Unchain',
      version='0.1',
      description='Websocket companion for Django',
      long_description=open('README.rst').read(),
      author='Hugo Herter',
      author_email='@hugoherter.com',
      url='https://github.com/hoh/Unchain/',
      packages=['unchain'],
      entry_points={'console_scripts': ['unchain=unchain.__main__:run']},
      install_requires=['aiohttp', 'pyyaml'],
      license='AGPLv3',
      keywords="websocket django publish subscribe",
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Console',
                   'Programming Language :: Python :: 3',
                   'Intended Audience :: Developers',
                   'Intended Audience :: Information Technology',
                   'Natural Language :: English',
                   'Operating System :: POSIX :: Linux',
                   'License :: OSI Approved :: GNU Affero General Public License v3',
                   'Topic :: Internet :: WWW/HTTP',
                   ],
      )
