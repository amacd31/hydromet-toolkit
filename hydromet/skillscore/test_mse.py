import unittest

import numpy as np

from mse import mse

class MSETestCase(unittest.TestCase):

    def setUp(self):
        self.test_obs = np.array([13.,17.,18.,20.,24.])
        self.test_sim = np.array([12.,15.,20.,22.,24.])

    def tearDown(self):
        pass

    def test_mse(self):
        print(self.test_obs)
        print(self.test_sim)
        result = mse(self.test_obs, self.test_sim)

        self.assertEqual(result, 2.6)

    def test_mse_perfect(self):
        result = mse(np.array([1.,2.,3.,4.,5.]),
            np.array([1.,2.,3.,4.,5.]))

        self.assertEqual(result, 0)


if __name__ == '__main__':
    unittest.main()