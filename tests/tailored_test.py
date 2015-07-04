import tests.base
import netcdf as nc
import numpy as np


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
        self.assertTrue((t_data[:] == data[:3,10:50,20:-20]).all())
        # The random values goes from 2.5 to 10 with 0.5 steps.
        t_data[:] = 1.5
        nc.sync(t_root)
        self.assertTrue((t_data[:] == 1.5).all())
        self.assertTrue((data[:3,10:50,20:-20] == 1.5).all())
        # self.assertTrue((data[:] != 1.5).any())
        nc.close(t_root)
        with nc.loader('unittest00.nc') as root:
            data = nc.getvar(root, 'data')
            self.assertTrue((data[:3,10:50,20:-20] == 1.5).all())
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
        self.assertTrue((t_data[:] == data[:3,10:50,20:-20]).all())
        # The random values goes from 2.5 to 10 with 0.5 steps.
        t_data[:] = 1.5
        self.assertTrue((t_data[:] == 1.5).all())
        self.assertTrue((data[:3,10:50,20:-20] == 1.5).all())
        self.assertTrue((data[:] != 1.5).any())
        nc.close(t_root)
        with nc.loader('unittest0*.nc') as root:
            data = nc.getvar(root, 'data')
            self.assertTrue((data[:3,10:50,20:-20] == 1.5).all())
            self.assertTrue((data[:] != 1.5).any())

    def test_compact_multiple_files(self):
        t_root = nc.tailor('unittest0*.nc', dimensions=self.dimensions)
        t_data = nc.getvar(t_root, 'data')
        data = nc.getvar(t_root.root, 'data')
        self.assertEquals(data.shape, (5, 100, 200))
        self.assertEquals(t_data.shape, (3, 40, 160))
        self.assertEquals(nc.getvar(t_root, 'time').shape, (3, 1))
        self.assertTrue((t_data[:] == data[:3,10:50,20:-20]).all())
        # The random values goes from 2.5 to 10 with 0.5 steps.
        t_data[:] = 1.5
        self.assertTrue((t_data[:] == 1.5).all())
        self.assertTrue((data[:3,10:50,20:-20] == 1.5).all())
        self.assertTrue((data[:] != 1.5).any())
        nc.close(t_root)
        with nc.loader('unittest0*.nc') as root:
            data = nc.getvar(root, 'data')
            self.assertTrue((data[:3,10:50,20:-20] == 1.5).all())
            self.assertTrue((data[:] != 1.5).any())

    def test_using_with(self):
        dims = self.dimensions
        with nc.loader('unittest0*.nc', dimensions=dims) as t_root:
            t_data = nc.getvar(t_root, 'data')
            data = nc.getvar(t_root.root, 'data')
            self.assertEquals(data.shape, (5, 100, 200))
            self.assertEquals(t_data.shape, (3, 40, 160))
            self.assertEquals(nc.getvar(t_root, 'time').shape, (3, 1))
            self.assertTrue((t_data[:] == data[:3,10:50,20:-20]).all())
            # The random values goes from 2.5 to 10 with 0.5 steps.
            t_data[:] = 1.5
            self.assertTrue((t_data[:] == 1.5).all())
            self.assertTrue((data[:3,10:50,20:-20] == 1.5).all())
            self.assertTrue((data[:] != 1.5).any())
        with nc.loader('unittest0*.nc') as root:
            data = nc.getvar(root, 'data')
            self.assertTrue((data[:3,10:50,20:-20] == 1.5).all())
            self.assertTrue((data[:] != 1.5).any())

    def test_getvar_source(self):
        dims = self.dimensions
        with nc.loader('unittest0*.nc', dimensions=dims) as t_root:
            ref_data = nc.getvar(t_root.root, 'data')
            t_data = nc.getvar(t_root, 'new_data', source=ref_data)
            data = nc.getvar(t_root.root, 'new_data')
            self.assertEquals(data.shape, (5, 100, 200))
            self.assertEquals(t_data.shape, (3, 40, 160))
            self.assertEquals(nc.getvar(t_root, 'time').shape, (3, 1))
            self.assertTrue((t_data[:] == data[:3,10:50,20:-20]).all())
            # The random values goes from 2.5 to 10 with 0.5 steps.
            t_data[:] = 1.5
            self.assertTrue((t_data[:] == 1.5).all())
            self.assertTrue((data[:3,10:50,20:-20] == 1.5).all())
            self.assertTrue((data[:] != 1.5).any())
        import os
        if os.path.exists('back'):
            os.system('cp -f unittest0* back/')
        with nc.loader('unittest0*.nc') as root:
            data = nc.getvar(root, 'new_data')
            self.assertTrue((data[:3,10:50,20:-20] == 1.5).all())
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
        import os
        if os.path.exists('back'):
            os.system('cp -f unittest0* back/')
        with nc.loader('unittest0*.nc') as root:
            data = nc.getvar(root, 'data')
            self.assertTrue((data[0, 20, 23] == 1.5).all())
            self.assertTrue((data[:] != 1.5).any())


if __name__ == '__main__':
        tests.base.main()


if __name__ == '__main__':
        tests.base.main()
