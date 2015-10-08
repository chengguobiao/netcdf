import tests.base
import netcdf as nc
import os


class TestTailored(tests.base.TestCase):

    def setUp(self):
        super(TestTailored, self).setUp()
        self.dimensions = {
            "xc": [20, -20],
            "yc": [10, 50],
            "time": [None, 3]
        }

    def test_simple_file(self):
        root = nc.open('unittest00.nc')[0]
        t_root = nc.tailor(root, dimensions=self.dimensions)
        t_data = nc.getvar(t_root, 'data')
        data = nc.getvar(root, 'data')
        self.assertEquals(data.shape, (1, 100, 200))
        self.assertEquals(t_data.shape, (1, 40, 160))
        self.assertEquals(nc.getvar(t_root, 'time').shape, (1,))
        self.assertTrue((t_data[:] == data[:3, 10:50, 20:-20]).all())
        # The random values goes from 2.5 to 10 with 0.5 steps.
        t_data[:] = 1.5
        nc.sync(t_root)
        self.assertTrue((t_data[:] == 1.5).all())
        self.assertTrue((data[:3, 10:50, 20:-20] == 1.5).all())
        # self.assertTrue((data[:] != 1.5).any())
        nc.close(t_root)
        with nc.loader('unittest00.nc') as root:
            data = nc.getvar(root, 'data')
            self.assertTrue((data[:3, 10:50, 20:-20] == 1.5).all())
            # self.assertTrue((data[:] != 1.5).any())

    def test_multiple_files(self):
        root = nc.open('unittest0*.nc')[0]
        t_root = nc.tailor(root, dimensions=self.dimensions)
        t_data = nc.getvar(t_root, 'data')
        data = nc.getvar(root, 'data')
        nc.sync(root)
        self.assertEquals(data.shape, (5, 100, 200))
        self.assertEquals(t_data.shape, (3, 40, 160))
        self.assertEquals(nc.getvar(t_root, 'time').shape, (3, 1))
        self.assertTrue((t_data[:] == data[:3, 10:50, 20:-20]).all())
        # The random values goes from 2.5 to 10 with 0.5 steps.
        t_data[:] = 1.5
        self.assertTrue((t_data[:] == 1.5).all())
        self.assertTrue((data[:3, 10:50, 20:-20] == 1.5).all())
        self.assertTrue((data[:] != 1.5).any())
        nc.close(t_root)
        with nc.loader('unittest0*.nc') as root:
            data = nc.getvar(root, 'data')
            self.assertTrue((data[:3, 10:50, 20:-20] == 1.5).all())
            self.assertTrue((data[:] != 1.5).any())

    def test_compact_multiple_files(self):
        t_root = nc.tailor('unittest0*.nc', dimensions=self.dimensions)
        t_data = nc.getvar(t_root, 'data')
        data = nc.getvar(t_root.root, 'data')
        self.assertEquals(data.shape, (5, 100, 200))
        self.assertEquals(t_data.shape, (3, 40, 160))
        self.assertEquals(nc.getvar(t_root, 'time').shape, (3, 1))
        self.assertTrue((t_data[:] == data[:3, 10:50, 20:-20]).all())
        # The random values goes from 2.5 to 10 with 0.5 steps.
        t_data[:] = 1.5
        self.assertTrue((t_data[:] == 1.5).all())
        self.assertTrue((data[:3, 10:50, 20:-20] == 1.5).all())
        self.assertTrue((data[:] != 1.5).any())
        nc.close(t_root)
        with nc.loader('unittest0*.nc') as root:
            data = nc.getvar(root, 'data')
            self.assertTrue((data[:3, 10:50, 20:-20] == 1.5).all())
            self.assertTrue((data[:] != 1.5).any())

    def test_list_multiple_files(self):
        files = map(lambda i: 'unittest0%i.nc' % i, range(5))
        t_root = nc.tailor(files, dimensions=self.dimensions)
        t_data = nc.getvar(t_root, 'data')
        data = nc.getvar(t_root.root, 'data')
        self.assertEquals(data.shape, (5, 100, 200))
        self.assertEquals(t_data.shape, (3, 40, 160))
        self.assertEquals(nc.getvar(t_root, 'time').shape, (3, 1))
        self.assertTrue((t_data[:] == data[:3, 10:50, 20:-20]).all())
        # The random values goes from 2.5 to 10 with 0.5 steps.
        t_data[:] = 1.5
        self.assertTrue((t_data[:] == 1.5).all())
        self.assertTrue((data[:3, 10:50, 20:-20] == 1.5).all())
        self.assertTrue((data[:] != 1.5).any())
        nc.close(t_root)
        with nc.loader('unittest0*.nc') as root:
            data = nc.getvar(root, 'data')
            self.assertTrue((data[:3, 10:50, 20:-20] == 1.5).all())
            self.assertTrue((data[:] != 1.5).any())

    def test_file_with_readonly_restriction(self):
        # check the file is NOT read only.
        filename = 'unittest00.nc'
        can_write = os.access(filename, os.W_OK)
        self.assertTrue(can_write)
        # check if open an existent file.
        root = nc.tailor('unittest00.nc', dimensions=self.dimensions,
                         read_only=True)
        self.assertEquals(root.files, ['unittest00.nc'])
        self.assertEquals(root.pattern, 'unittest00.nc')
        self.assertEquals(len(root.roots), 1)
        self.assertFalse(root.is_new)
        self.assertTrue(root.read_only)
        with self.assertRaisesRegexp(Exception, u'NetCDF: Write to read only'):
            var = nc.getvar(root, 'data')
            var[:] = 0
        # check if close an existent file.
        nc.close(root)
        with self.assertRaisesRegexp(RuntimeError, u'NetCDF: Not a valid ID'):
            nc.close(root)

    def test_multiple_files_with_readonly_restriction(self):
        # check the files are NOT read only.
        filenames = map(lambda i: 'unittest0%i.nc' % i, range(5))
        can_write = map(lambda f: os.access(f, os.W_OK), filenames)
        self.assertTrue(all(can_write))
        # check if open the pattern selection using using a package instance.
        root = nc.tailor('unittest0*.nc', dimensions=self.dimensions,
                         read_only=True)
        self.assertEquals(root.files, ['unittest0%i.nc' % i for i in range(5)])
        self.assertEquals(root.pattern, 'unittest0*.nc')
        self.assertEquals(len(root.roots), 5)
        self.assertFalse(root.is_new)
        self.assertTrue(root.read_only)
        with self.assertRaisesRegexp(Exception, u'NetCDF: Write to read only'):
            var = nc.getvar(root, 'data')
            var[:] = 0
        # check if close the package with all the files.
        nc.close(root)
        with self.assertRaisesRegexp(RuntimeError, u'NetCDF: Not a valid ID'):
            nc.close(root)

    def test_using_with(self):
        # use the with to open the files.
        dims = self.dimensions
        with nc.loader('unittest0*.nc', dimensions=dims) as t_root:
            t_data = nc.getvar(t_root, 'data')
            data = nc.getvar(t_root.root, 'data')
            self.assertEquals(data.shape, (5, 100, 200))
            self.assertEquals(t_data.shape, (3, 40, 160))
            self.assertEquals(nc.getvar(t_root, 'time').shape, (3, 1))
            self.assertTrue((t_data[:] == data[:3, 10:50, 20:-20]).all())
            # The random values goes from 2.5 to 10 with 0.5 steps.
            t_data[:] = 1.5
            self.assertTrue((t_data[:] == 1.5).all())
            self.assertTrue((data[:3, 10:50, 20:-20] == 1.5).all())
            self.assertTrue((data[:] != 1.5).any())
        with nc.loader('unittest0*.nc') as root:
            data = nc.getvar(root, 'data')
            self.assertTrue((data[:3, 10:50, 20:-20] == 1.5).all())
            self.assertTrue((data[:] != 1.5).any())

    def test_using_with_and_readonly_restriction(self):
        # check the files are NOT read only.
        filenames = map(lambda i: 'unittest0%i.nc' % i, range(5))
        can_write = map(lambda f: os.access(f, os.W_OK), filenames)
        self.assertTrue(all(can_write))
        # use the with to open the files with readonly access.
        dims = self.dimensions
        with nc.loader('unittest0*.nc', dimensions=dims,
                       read_only=True) as t_root:
            self.assertTrue(t_root.read_only)
            t_data = nc.getvar(t_root, 'data')
            data = nc.getvar(t_root.root, 'data')
            self.assertEquals(data.shape, (5, 100, 200))
            self.assertEquals(t_data.shape, (3, 40, 160))
            self.assertEquals(nc.getvar(t_root, 'time').shape, (3, 1))
            self.assertTrue((t_data[:] == data[:3, 10:50, 20:-20]).all())
            with self.assertRaisesRegexp(Exception,
                                         u'NetCDF: Write to read only'):
                var = nc.getvar(t_root, 'data')
                var[:] = 0

    def test_getdim(self):
        dims = self.dimensions
        with nc.loader('unittest_dims.nc', dimensions=dims) as t_root:
            t_dim_x = nc.getdim(t_root, 'xc_k', 1)
            t_dim_y = nc.getdim(t_root, 'yc_k', 1)
            t_dim_time = nc.getdim(t_root, 'time', 1)
            self.assertEquals(len(t_dim_x[0]), 1)
            self.assertEquals(len(t_dim_y[0]), 1)
            self.assertEquals(len(t_dim_time[0]), 1)
            t_data = nc.getvar(t_root, 'only_one_pixel', 'f4',
                               ('time', 'yc_k', 'xc_k'))
            self.assertEquals(t_data.shape, (1, 1, 1))

    def test_getvar_source(self):
        dims = self.dimensions
        with nc.loader('unittest0*.nc', dimensions=dims) as t_root:
            ref_data = nc.getvar(t_root.root, 'data')
            t_data = nc.getvar(t_root, 'new_data', source=ref_data)
            data = nc.getvar(t_root.root, 'new_data')
            self.assertEquals(data.shape, (5, 100, 200))
            self.assertEquals(t_data.shape, (3, 40, 160))
            self.assertEquals(nc.getvar(t_root, 'time').shape, (3, 1))
            self.assertTrue((t_data[:] == data[:3, 10:50, 20:-20]).all())
            # The random values goes from 2.5 to 10 with 0.5 steps.
            t_data[:] = 1.5
            self.assertTrue((t_data[:] == 1.5).all())
            self.assertTrue((data[:3, 10:50, 20:-20] == 1.5).all())
            self.assertTrue((data[:] != 1.5).any())
        with nc.loader('unittest0*.nc') as root:
            data = nc.getvar(root, 'new_data')
            self.assertTrue((data[:3, 10:50, 20:-20] == 1.5).all())
            self.assertTrue((data[:] != 1.5).any())

    def test_getvar_source_to_single_file(self):
        dims = self.dimensions
        # TODO: It should spread the dimensions limits from the source.
        with nc.loader('unittest_other.nc') as new_root:
            with nc.loader('unittest0*.nc', dimensions=dims) as t_root:
                t_data = nc.getvar(t_root, 'data')
                data = nc.getvar(new_root, 'new_data', source=t_data)
                self.assertEquals(t_data.shape, (3, 40, 160))
                self.assertEquals(nc.getvar(t_root, 'time').shape, (3, 1))
                self.assertTrue(
                    (t_data[:] == data[0, :3, 10:50, 20:-20]).all())
                # The random values goes from 2.5 to 10 with 0.5 steps.
                data[0:2, -30:-20, -10:-5] = 1.5
                self.assertTrue((data[:] != 1.5).any())

    def test_getvar_source_to_multiple_files(self):
        dims = self.dimensions
        self.mult = [self.create_ref_file('unittest_ot%s.nc' %
                                          (str(i).zfill(2)))
                     for i in range(5)]
        # TODO: It should spread the dimensions limits from the source.
        with nc.loader('unittest_ot0*.nc') as new_root:
            with nc.loader('unittest0*.nc', dimensions=dims) as t_root:
                t_data = nc.getvar(t_root, 'data')
                data = nc.getvar(new_root, 'new_data', source=t_data)
                self.assertEquals(t_data.shape, (3, 40, 160))
                self.assertEquals(nc.getvar(t_root, 'time').shape, (3, 1))
                self.assertTrue((t_data[:] == data[:3, 10:50, 20:-20]).all())
                # The random values goes from 2.5 to 10 with 0.5 steps.
                data[0:2, -30:-20, -10:-5] = 1.5
                self.assertTrue((data[:] != 1.5).any())

    def test_specific_subindex_support(self):
        dims = self.dimensions
        with nc.loader('unittest0*.nc', dimensions=dims) as t_root:
            t_data = nc.getvar(t_root, 'data')
            data = nc.getvar(t_root.root, 'data')
            self.assertEquals(data.shape, (5, 100, 200))
            self.assertEquals(t_data.shape, (3, 40, 160))
            self.assertEquals(nc.getvar(t_root, 'time').shape, (3, 1))
            # The random values goes from 2.5 to 10 with 0.5 steps.
            t_data[0:2, 10, 3] = 1.5
            self.assertTrue((t_data[0:2, 10, 3] == 1.5).all())
            self.assertTrue((data[0:2, 20, 23] == 1.5).all())
            self.assertTrue((data[:] != 1.5).any())
        with nc.loader('unittest0*.nc') as root:
            data = nc.getvar(root, 'data')
            self.assertTrue((data[0, 20, 23] == 1.5).all())
            self.assertTrue((data[:] != 1.5).any())

    def test_specific_subindex_overflow_warning(self):
        dims = self.dimensions
        dims['time'] = [1, 3]
        with nc.loader('unittest0*.nc', dimensions=dims) as t_root:
            t_data = nc.getvar(t_root, 'data')
            data = nc.getvar(t_root.root, 'data')
            self.assertEquals(data.shape, (5, 100, 200))
            self.assertEquals(t_data.shape, (2, 40, 160))
            self.assertEquals(nc.getvar(t_root, 'time').shape, (2, 1))
            # The random values goes from 2.5 to 10 with 0.5 steps.
            with self.assertRaisesRegexp(Exception,
                                         'Overflow: Index outside of the tile '
                                         'dimensions.'):
                t_data[1:3, 10, 30] = 1.5
            with self.assertRaisesRegexp(Exception,
                                         'Overflow: Index outside of the tile '
                                         'dimensions.'):
                t_data[1:2, -41, 30] = 1.5
            with self.assertRaisesRegexp(Exception,
                                         'Overflow: Index outside of the tile '
                                         'dimensions.'):
                t_data[1:2, 10, -161] = 1.5
            with self.assertRaisesRegexp(Exception,
                                         'Overflow: Index outside of the tile '
                                         'dimensions.'):
                t_data[-3:-1, -10, -30] = 1.5
            with self.assertRaisesRegexp(Exception,
                                         'Overflow: Index outside of the tile '
                                         'dimensions.'):
                t_data[-2:, 41, -30] = 1.5
            with self.assertRaisesRegexp(Exception,
                                         'Overflow: Index outside of the tile '
                                         'dimensions.'):
                t_data[-2:, -10, 161] = 1.5
            self.assertTrue((t_data[:] != 1.5).all())

    def test_getvar_with_incomplete_limited_dimensions(self):
        self.dimensions.pop('time', None)
        root = nc.open('unittest0*.nc')[0]
        t_root = nc.tailor(root, dimensions=self.dimensions)
        t_data = nc.getvar(t_root, 'data')
        data = nc.getvar(root, 'data')
        nc.sync(root)
        self.assertEquals(data.shape, (5, 100, 200))
        self.assertEquals(t_data.shape, (5, 40, 160))
        self.assertEquals(nc.getvar(t_root, 'time').shape, (5, 1))
        self.assertTrue((t_data[:] == data[:, 10:50, 20:-20]).all())
        # The random values goes from 2.5 to 10 with 0.5 steps.
        t_data[:] = 1.5
        self.assertTrue((t_data[:] == 1.5).all())
        self.assertTrue((data[:, 10:50, 20:-20] == 1.5).all())
        self.assertTrue((data[:] != 1.5).any())
        nc.close(t_root)
        with nc.loader('unittest0*.nc') as root:
            data = nc.getvar(root, 'data')
            self.assertTrue((data[:, 10:50, 20:-20] == 1.5).all())
            self.assertTrue((data[:] != 1.5).any())


if __name__ == '__main__':
        tests.base.main()
