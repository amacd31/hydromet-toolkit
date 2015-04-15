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

        self.assertAlmostEqual(result, 0.93444, 2)

    def test_kge_perfect(self):
        result = kge(np.array([1.,2.,3.,4.,5.,6.,7.]),
                np.array([1.,2.,3.,4.,5.,6.,7.]))

        # Score of 1 for a perfect match.
        self.assertEqual(result, 1)

    def test_kge_climatology(self):
        m = np.mean([1.,2.,3.,4.,5.])
        sim = np.array([m, m, m, m, m])
        result = kge(np.array([1.,2.,3.,4.,5.]),
                    sim
                )

        # Score of 1 - sqrt(2) when no better than the mean.
        self.assertAlmostEqual(result, 1 - np.sqrt(2), 5)

    def test_kge_biased_climatology(self):
        m = np.mean([1.,2.,3.,4.,5.])
        sim = np.array([m, m, m, m, m]) * 2
        result = kge(np.array([1.,2.,3.,4.,5.]),
                    sim
                )

        # Score of 1 - sqrt(3) when no better than the biased mean.
        self.assertAlmostEqual(result, 1 - np.sqrt(3), 5)


if __name__ == '__main__':
    unittest.main()
