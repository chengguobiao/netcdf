# -*- coding: utf-8 -*-
try:
    from setuptools import setup
    from setuptools import find_packages
except ImportError:
    from distutils.core import setup

import os
os.system('easy_install numpy==1.8.0')
os.system('pip install -r requirements.deployment.txt')

import platform as p
from urllib import FancyURLopener
import os
import progressbar as pb
import tarfile as tar
import multiprocessing

os_name = p.system()
title = '%s %s' % (os_name, p.architecture()[0])
bar = '-' * len(title)
print '+%s+' % bar
print '|%s|' % title
print '+%s+' % bar
source_path = '/usr/sources'
os.system('sudo mkdir -p %s' % source_path)
os.system('sudo chmod -R ugo+rwx %s' % source_path)

systems = {
    'Linux': {
        'update_shared_libs': 'sudo ldconfig',
        'libs': {
            'hdf5': '/usr/local/lib/libhdf5.so.8.0.1',
            'netcdf': '/usr/local/lib/libnetcdf.so.7.2.0'
        }
    },
    'Darwin': {
        'update_shared_libs': '',
        'libs': {
            'hdf5': '/usr/local/lib/libhdf5_hl.8.dylib',
            'netcdf': '/usr/local/lib/libnetcdf.7.dylib'
        }
    }
}


class FakeAgent(FancyURLopener, object):
    version = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.149 '
    'Safari/537.36'


downloader = FakeAgent()


def get(path, url, local_path):
    filename = '%s.tar.gz' % path
    local_filename = '%s/%s' % (local_path, filename)
    local_unpacked = '%s/%s' % (local_path, path)
    if not os.path.isfile('%s/%s' % (local_path, filename)):
        widgets = [filename, '  ', pb.Percentage(), ' ',
                   pb.Bar('#', u'\033[34m[', u']\033[0m'),
                   ' ', pb.ETA(), ' ', pb.FileTransferSpeed()]
        bar = pb.ProgressBar(maxval=20, widgets=widgets)

        def dlProgress(count, blockSize, totalSize):
            bar.maxval = totalSize
            status = (count * blockSize if totalSize >= count * blockSize
                      else totalSize)
            bar.update(status)
        downloader.retrieve('%s/%s' % (url, filename), local_filename,
                            reporthook=dlProgress)
    if not os.path.isdir(local_unpacked):
        tfile = tar.open(local_filename, mode='r:gz')
        tfile.extractall(local_path)
        tfile.close()


def build(path, pre_config='', post_config=''):
    lib_key = path.split('-')[0].split('/')[-1]
    filename = systems[os_name]['libs'][lib_key]
    if os.path.isfile(filename):
        os.system('sudo rm %s' % filename)
    ncores = multiprocessing.cpu_count()
    os.system('cd %s; %s ./configure %s; make -j %s;'
              ' sudo make install'  # check
              % (path, pre_config, post_config, ncores))
    update_shared_libs = systems[os_name]['update_shared_libs']
    if update_shared_libs:
        os.system(update_shared_libs)


def install_libs():
    global source_path
    # Deploy the hdf5 C library
    name = 'hdf5-%s' % '1.8.12'
    get(name,
        'http://www.hdfgroup.org/ftp/HDF5/releases/%s/src' % (name),
        source_path)
    build('%s/%s' % (source_path, name),
          post_config='--prefix=/usr/local --enable-shared --enable-hl')
    # Deploy the netcdf4 C library
    name = 'netcdf-%s' % '4.3.1-rc4'
    get(name, 'ftp://ftp.unidata.ucar.edu/pub/netcdf', source_path)
    build('%s/%s' % (source_path, name),
          pre_config='LDFLAGS=-L/usr/local/lib CPPFLAGS=-I/usr/local/include '
          'LD_LIBRARY_PATH=/usr/local',
          post_config='--enable-netcdf-4 --enable-dap --enable-shared'
          ' --prefix=/usr/local')

install_libs()
from pip.req import parse_requirements
reqs = [str(ir.req) for ir in parse_requirements('requirements.txt')]

# Try to transform the README from Markdown to reStructuredText.
try:
    import pandoc
    pandoc.core.PANDOC_PATH = 'pandoc'
    doc = pandoc.Document()
    doc.markdown = open('README.md').read()
    description = doc.rst
except Exception:
    description = open('README.md').read()

setup(
    name='netcdf',
    version='0.0.14',
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
    classifiers=[
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Physics",
    ],
)
