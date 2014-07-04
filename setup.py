# -*- coding: utf-8 -*-
try:
    from setuptools import setup
    from setuptools import find_packages
except ImportError:
    from distutils.core import setup

import os
os.system('make libs-and-headers')

from pip.req import parse_requirements
reqs = [str(ir.req) for ir in parse_requirements('requirements.txt')]

# Try to transform the README from Markdown to reStructuredText.
try:
    import pandoc
    pandoc.core.PANDOC_PATH = 'pandoc'
    doc = pandoc.Document()
    doc.markdown = open('README.md').read()
    description = doc.rst
except ImportError:
    description = open('README.md').read()

setup(
    name='netcdf',
    version='0.0.0',
    author=u'Eloy Adonis Colell',
    author_email='eloy.colell@gmail.com',
    packages=find_packages(),
    url='https://github.com/ecolell/netcdf',
    license='MIT License, see LICENCE.txt',
    description='A python library that allow to use one or multiple NetCDF '
                'files in a transparent way through polimorphic methods.',
    long_description=description,
    zip_safe=False,
    include_package_data=True,
    install_requires=reqs,
)
