# -*- coding: utf-8 -*-
"""Setup for Drastic-Web

"""
__copyright__ = "Copyright (C) 2016 University of Maryland"
__license__ = "GNU AFFERO GENERAL PUBLIC LICENSE, Version 3"


from distutils.core import setup
from setuptools import setup


setup(
    name='drastic-web',
    version="1.1",
    description='Drastic web ui',
    extras_require={},
    long_description="Django web ui for Drastic",
    author='Archive Analytics',
    maintainer_email='jansen@umd.edu',
    license="GNU AFFERO GENERAL PUBLIC LICENSE, Version 3",
    url='https://github.com/UMD-DRASTIC/drastic-web',
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        "Topic :: System :: Archiving"
    ],
)
