import unittest

import math
import numpy as np

from rmse import rmse

class RMSETestCase(unittest.TestCase):

    def setUp(self):
        self.test_obs = np.array([13.,17.,18.,20.,24.])
        self.test_sim = np.array([12.,15.,20.,22.,24.])

    def tearDown(self):
        pass

    def test_rmse(self):
        print(self.test_obs)
        print(self.test_sim)
        result = rmse(self.test_obs, self.test_sim)

        self.assertEqual(result, math.sqrt(2.6))

    def test_rmse_perfect(self):
        result = rmse(np.array([1.,2.,3.,4.,5.]),
            np.array([1.,2.,3.,4.,5.]))

        self.assertEqual(result, 0)


if __name__ == '__main__':
    unittest.main()
