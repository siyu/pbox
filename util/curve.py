__author__ = 'siy'

import unittest as test

def max_drop_in_curve(curve):
    peak = -99999999999999999999
    max_drop = 0

    for v in curve:
        if v > peak:    # new peak, so reset curr_drop
            peak = v
        else:
            curr_drop = (v - peak) / peak
            if curr_drop < max_drop:
                max_drop = curr_drop

    return max_drop


class CurveTest(test.TestCase):
    def test_max_drop_in_curve(self):
        self.assertEquals(-0.4375, max_drop_in_curve([1,2,3,4,5,6,5,4,5,6,7,8,7,6,5,4.5,6,8,10,7]))
        self.assertEquals(-0.5, max_drop_in_curve([1,2,3,4,5,6,5,3,5,6,7,8,7,6,5,4.5,6,8,10,7]))
        self.assertEquals(-0.8, max_drop_in_curve([1,2,3,4,5,6,5,3,5,6,7,8,7,6,5,4.5,6,8,10,2]))






