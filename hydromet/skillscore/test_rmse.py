import unittest

import math
import numpy as np

from . import rmse

class RMSETestCase(unittest.TestCase):

    def setUp(self):
        self.test_obs = np.array([13.,17.,18.,20.,24.])
        self.test_sim = np.array([12.,15.,20.,22.,24.])

    def tearDown(self):
        pass

    def test_rmse(self):
        result = rmse(self.test_obs, self.test_sim)

        self.assertEqual(result, math.sqrt(2.6))

    def test_rmse_perfect(self):
        result = rmse(np.array([1.,2.,3.,4.,5.]),
            np.array([1.,2.,3.,4.,5.]))

        self.assertEqual(result, 0)

    def test_rmse_bad(self):
        m = np.mean([1.,2.,3.,4.,5.])
        sim = np.array([m, m, m, m, m])
        result = rmse(np.array([1.,2.,3.,4.,5.]),
                    sim
                )

        self.assertEqual(result, math.sqrt(2))


if __name__ == '__main__':
    unittest.main()
