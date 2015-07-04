import unittest
from netCDF4 import Dataset
import stat
import os
import numpy as np


class TestCase(unittest.TestCase):

    def create_ref_file(self, filename):
        ref = Dataset(
            filename,
            mode="w",
            clobber=True,
            format='NETCDF3_CLASSIC')
        ref.createDimension('auditCount', 2)
        ref.createDimension('auditSize', 80)
        ref.createDimension('xc', 200)
        ref.createDimension('yc', 100)
        ref.createDimension('time')
        var = ref.createVariable(
            'time',
            'i4',
            dimensions=('time',),
            zlib=True,
            fill_value=0)
        var[0] = 1
        var = ref.createVariable(
            'lat',
            'f4',
            dimensions=('yc', 'xc'),
            zlib=True,
            fill_value=0.0)
        var[:] = 1
        var = ref.createVariable(
            'lon',
            'f4',
            dimensions=('yc', 'xc'),
            zlib=True,
            fill_value=0.0)
        var[:] = 1
        var = ref.createVariable(
            'data',
            'f4',
            dimensions=('time', 'yc', 'xc'),
            zlib=True,
            fill_value=0.0)
        var[:] = self.data
        var = ref.createVariable(
            'auditTrail',
            'S1',
            dimensions=('auditCount', 'auditSize'),
            zlib=True,
            fill_value=0.0)
        var[:] = self.auditTrail
        return ref

    def setUp(self):
        audit = np.array([['1', '4', '0', '0', '1', ' ', '2', '3', '2', '3',
                           '5', '2', ' ', 'I', 'M', 'G', 'C', 'O', 'P', 'Y',
                           ' ', 'D', 'E', 'L', 'I', 'V', 'E', 'R', 'Y', '/',
                           'I', 'N', '1', '2', '6', '7', '8', '3', '3', '1',
                           '9', '4', '.', '1', ' ', 'D', 'E', 'L', 'I', 'V',
                           'E', 'R', 'Y', '/', 'N', 'C', '1', '2', '6', '7',
                           '8', '3', '3', '1', '9', '4', '.', '1', ' ', 'L',
                           'I', 'N', 'E', 'L', 'E', '=', '1', '1', '0', '1'],
                          [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
                           ' ', ' ', ' ', '0', ' ', '1', '6', '8', '5', '2',
                           ' ', 'I', ' ', 'P', 'L', 'A', 'C', 'E', '=', 'U',
                           'L', 'E', 'F', 'T', ' ', 'B', 'A', 'N', 'D', '=',
                           '1', ' ', 'D', 'O', 'C', '=', 'Y', 'E', 'S', ' ',
                           'M', 'A', 'G', '=', '-', '1', ' ', '-', '1', ' ',
                           'S', 'I', 'Z', 'E', '=', '1', '0', '6', '7', ' ',
                           '2', '1', '6', '6', ' ', ' ', ' ', ' ', ' ', ' ']])
        self.auditTrail = audit
        values = map(lambda x: x/2., range(5, 20))
        self.data = np.random.choice(values, (1, 100, 200))
        # Append a static square for a visible control.
        x = 5
        self.data[0:1,x:x+10,x:x+10] = 2.5
        # Create the files.
        self.refs = [self.create_ref_file('unittest%s.nc' % (str(i).zfill(2)))
                     for i in range(5)]
        list(map(lambda ref: ref.sync(), self.refs))
        self.ro_ref = self.create_ref_file('ro_unittest.nc')
        self.ro_ref.sync()

    def tearDown(self):
        list(map(lambda ref: ref.close(), self.refs))
        self.ro_ref.close()
        os.chmod('ro_unittest.nc', stat.S_IWRITE | stat.S_IRUSR |
                 stat.S_IRGRP | stat.S_IROTH)
        os.system('rm *.nc')


def main():
    unittest.main()
