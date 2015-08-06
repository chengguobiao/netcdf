netcdf
======

[![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/gersolar/netcdf?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

[![License](https://img.shields.io/pypi/l/netcdf.svg)](https://raw.githubusercontent.com/gersolar/netcdf/master/LICENSE) [![Downloads](https://img.shields.io/pypi/dm/netcdf.svg)](https://pypi.python.org/pypi/netcdf/) [![Build Status](https://travis-ci.org/gersolar/netcdf.svg?branch=master)](https://travis-ci.org/gersolar/netcdf) [![Coverage Status](https://coveralls.io/repos/gersolar/netcdf/badge.png)](https://coveralls.io/r/gersolar/netcdf) [![Code Health](https://landscape.io/github/gersolar/netcdf/master/landscape.png)](https://landscape.io/github/gersolar/netcdf/master) [![PyPI version](https://badge.fury.io/py/netcdf.svg)](http://badge.fury.io/py/netcdf)
[![Stories in Ready](https://badge.waffle.io/gersolar/netcdf.png?label=ready&title=Ready)](https://waffle.io/gersolar/netcdf)


A python library that allow to use one or multiple NetCDF files in a transparent way through polimorphic methods.


Requirements
------------

If you want to use this library on any GNU/Linux or OSX system you just need to execute:

    $ pip install netcdf

If you want to improve this library, you should download the [github repository](https://github.com/gersolar/netcdf) and execute:

    $ make deploy

This library is builded over two **C libraries** (named **libhdf5** and **libnetcdf** in *aptitude*). To provide a cross-platform installation, the [setup.py](https://github.com/gersolar/netcdf/blob/master/setup.py) is going to require the **sudo** password to automate the installation of these two libraries.

On Ubuntu Desktop there are some other libraries not installed by default (zlibc curl libssl0.9.8 libbz2-dev libxslt*-dev libxml*-dev) which may need to be installed to use these library. Use the next command to automate the installation of the additional C libraries:

    $ make ubuntu deploy


Testing
-------

To test all the project you should use the command:

    $ make test

If you want to help us or report an issue join to us through the [GitHub issue tracker](https://github.com/gersolar/netcdf/issues).


Example
--------

It can open one or multiple files with the same statement. You can use a **pattern**:

```python
from netcdf import netcdf as nc
root, is_new = nc.open('file_*.nc')
print root.files

data = nc.getvar(root, 'data')
print "Matrix shape: ", data.shape
print "Matrix values: ", data[:]

nc.close(root)
```

Or you can open a **list of files**:

```python
from netcdf import netcdf as nc
root, is_new = nc.open(['file01.nc', 'file02.nc', 'file03.nc'])
nc.close(root)
```

Also, it is compatible with **numpy**:

```python
from netcdf import netcdf as nc
import numpy as np
root, is_new = nc.open('file_*.nc')
data = nc.getvar(root, 'data')

data[:] = data[:] + 3.
print "Matrix values: ", data[:]
# Bulk the data variable into the files.
nc.sync(root)

# Set to zero all the values of the matrix.
data[:] = np.zeros(data.shape)
print data[:]

nc.close(root)
```
It also can **join a variable distributed in multiple files** and save it in a single file:

```python
from netcdf import netcdf as nc
root, is_new = nc.open('file_*.nc')
print root.files
data = nc.getvar(root, 'data')
print "Matrix shape: ", data.shape

joined_root, is_new = nc.open('new_file.nc')
print joined_root.files
joined_data = nc.getvar(joined_root, 'copied_data', source=data)
print "Matrix shape: ", joined_data.shape

nc.close(joined_root)
nc.close(root)
```

Also, it can use a **with** statement to reduce the code and guarantee the call to the close function to save changes:

```python
from netcdf import netcdf as nc
import numpy as np
with nc.loader('new_file.nc') as joined_root:
    with nc.loader(['file01.nc', 'file02.nc', 'file03.nc']) as root:
        data = nc.getvar(root, 'data')
        joined_data = nc.getvar(joined_root, 'copied_data', source=data)
        joined_data[:] = joined_data[:] ** 3 + np.cos(joined_data[:]) * 2
```

Last, it can use a tiled access to the data through:

```python
from netcdf import netcdf as nc
import numpy as np
dims = {
    'xc': [20,-20],
    'yc': [10,50],
    'time': [-30, None]
}

with nc.loader('file0*.nc', dimensions=dims) as root:
    data = nc.getvar(root, 'data')
    print data.shape
```


About
-----

This software is developed by [GERSolar](http://www.gersol.unlu.edu.ar/). You can contact us to [gersolar.dev@gmail.com](mailto:gersolar.dev@gmail.com).
