import platform as p
from urllib import FancyURLopener
import os
import progressbar as pb
import tarfile as tar
import multiprocessing

update_shared_libs = ''

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

os_name = p.system()
title = '%s %s' % (os_name, p.architecture()[0])
bar = '-' * len(title)
print '+%s+' % bar
print '|%s|' % title
print '+%s+' % bar


class FakeAgent(FancyURLopener, object):
    version = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.149 '
    'Safari/537.36'


downloader = FakeAgent()


def get(path, url):
    filename = '%s.tar.gz' % path
    if not os.path.isfile(filename):
        widgets = [filename, '  ', pb.Percentage(), ' ',
                   pb.Bar('#', u'\033[34m[', u']\033[0m'),
                   ' ', pb.ETA(), ' ', pb.FileTransferSpeed()]
        bar = pb.ProgressBar(maxval=20, widgets=widgets)

        def dlProgress(count, blockSize, totalSize):
            bar.maxval = totalSize
            status = (count * blockSize if totalSize >= count * blockSize
                      else totalSize)
            bar.update(status)
        downloader.retrieve('%s/%s' % (url, filename), filename,
                            reporthook=dlProgress)
    if not os.path.isdir(path):
        tfile = tar.open(filename, mode='r:gz')
        tfile.extractall('.')
        tfile.close()


def build(path, pre_config='', post_config=''):
    filename = systems[os_name]['libs'][path.split('-')[0]]
    print filename
    if not os.path.isfile(filename):
        ncores = multiprocessing.cpu_count()
        os.system('cd %s; %s ./configure %s; make -j %s;'
                  ' sudo make check install'
                  % (path, pre_config, post_config, ncores))
        if update_shared_libs:
            os.system(systems[os_name]['update_shared_libs'])


def install_hdf5():
    name = 'hdf5-%s' % '1.8.12'
    get(name,
        'http://www.hdfgroup.org/ftp/HDF5/releases/%s/src' % (name))
    build(name,
          post_config='--prefix=/usr/local --enable-shared --enable-hl')


def install_netcdf4():
    install_hdf5()
    name = 'netcdf-%s' % '4.3.1-rc4'
    get(name, 'ftp://ftp.unidata.ucar.edu/pub/netcdf')
    build(name,
          pre_config='LDFLAGS=-L/usr/local/lib CPPFLAGS=-I/usr/local/include',
          post_config='--enable-netcdf-4 --enable-dap --enable-shared'
          ' --prefix=/usr/local')
