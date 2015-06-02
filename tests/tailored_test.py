import tests.base
import netcdf as nc
import numpy as np


class TestTailored(tests.base.TestCase):

    def setUp(self):
        super(TestTailored, self).setUp()
        self.tails = {
            "1": {
                "machine": "*",
                    "dimensions": {
                        "xc": [20, -20],
                        "yc": [10, 50],
                        "time": [None, 3]
                    }
                }
            }

    def test_simple_file(self):
        root = nc.open('unittest00.nc')[0]
        t_root = nc.tailor(root, tails=self.tails)
        t_data = nc.getvar(t_root, 'data')
        data = nc.getvar(root, 'data')
        self.assertEquals(data.shape, (1, 100, 200))
        self.assertEquals(t_data.shape, (1, 40, 160))
        self.assertEquals(nc.getvar(t_root, 'time').shape, (1,))
        self.assertTrue((t_data[:] == data[:3,10:50,20:-20]).all())
        t_data[:] = 3.5
        self.assertTrue((t_data[:] == 3.5).all())
        self.assertTrue((t_data[:] == 3.5).all())
        self.assertTrue((data[:3,10:50,20:-20] == 3.5).all())
        self.assertTrue((data[:] != 3.5).any())
        nc.close(root)

        pass


if __name__ == '__main__':
        tests.base.main()
