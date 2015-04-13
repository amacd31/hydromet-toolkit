import unittest

import numpy as np

from hydromet.skillscore import kge

class KGETestCase(unittest.TestCase):

    def setUp(self):
        self.test_obs = np.array([1,2,3,4,5,6,7,6,5,4,3,2,1], dtype=np.float)
        self.test_sim = np.array([1,2,3,4,5,6,6,6,5,4,3,2,1], dtype=np.float)

    def tearDown(self):
        pass

    def test_kge(self):
        result = kge(self.test_obs, self.test_sim)

        self.assertAlmostEqual(result, 0.93444, 5)

    def test_kge_perfect(self):
        result = kge(np.array([1.,2.,3.,4.,5.,6.,7.]),
                np.array([1.,2.,3.,4.,5.,6.,7.]))

        self.assertEqual(result, 1)

    def test_kge_bad(self):
        m = np.mean([1.,2.,3.,4.,5.])
        sim = np.array([m-0.01, m, m, m, m+0.01])
        result = kge(np.array([1.,2.,3.,4.,5.]),
                    sim
                )

        # Score of (almost) zero when no better than the (almost) mean.
        self.assertAlmostEqual(result, -0.001276, 5)


if __name__ == '__main__':
    unittest.main()
