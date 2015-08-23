import unittest

import numpy as np

from . import nse

class NSETestCase(unittest.TestCase):

    def setUp(self):
        self.test_obs = np.array([5,4,6,1,3,6,8,1,7,3,4,0.5])
        self.test_sim = np.array([3,4.5,4,2,4,5,9,2,8,3,4,0.8])

    def tearDown(self):
        pass

    def test_nse(self):
        result = nse(self.test_obs, self.test_sim)

        self.assertEqual(result, 0.783479081472161)

    def test_nse_perfect(self):
        result = nse(np.array([1.,2.,3.,4.,5.]),
                np.array([1.,2.,3.,4.,5.]))

        self.assertEqual(result, 1)

    def test_nse_bad(self):
        m = np.mean([1.,2.,3.,4.,5.])
        sim = np.array([m, m, m, m, m])
        result = nse(np.array([1.,2.,3.,4.,5.]),
                    sim
                )

        # Score of zero when no better than the mean.
        self.assertEqual(result, 0)


if __name__ == '__main__':
    unittest.main()
