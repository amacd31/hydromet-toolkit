import unittest
import pandas as pd

from numpy.testing import assert_array_equal

from hydromet import stats as hm_stats

class StatsTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_dist_free_cusum(self):
        test_data = pd.Series([5,3,5,4,4,4,4,3,6,3,3,3,2])

        r = hm_stats.dist_free_cusum(test_data)

        self.assertEqual(r['max'], 5.0)
        self.assertEqual(r['idxmax'], 6)
        assert_array_equal(r['dist_free_cusum'], [1,0,1,2,3,4,5,4,5,4,3,2,1])

        self.assertAlmostEqual(r['significance_level'][0.1], 4.39877, 5)


