import unittest

from src.analytics.cagr import (
    calculate_cagr,
    revenue_cagr,
    pat_cagr,
    eps_cagr
)


class TestCAGR(unittest.TestCase):

    # 1 Normal CAGR
    def test_normal_cagr(self):
        value, flag = calculate_cagr(100, 200, 5)
        self.assertEqual(flag, "OK")
        self.assertAlmostEqual(value, 14.87, places=2)

    # 2 Revenue CAGR
    def test_revenue_cagr(self):
        value, flag = revenue_cagr(1000, 1500, 5)
        self.assertEqual(flag, "OK")
        self.assertAlmostEqual(value, 8.45, places=2)

    # 3 PAT CAGR
    def test_pat_cagr(self):
        value, flag = pat_cagr(100, 200, 5)
        self.assertEqual(flag, "OK")

    # 4 EPS CAGR
    def test_eps_cagr(self):
        value, flag = eps_cagr(10, 20, 5)
        self.assertEqual(flag, "OK")

    # 5 Zero Base
    def test_zero_base(self):
        value, flag = calculate_cagr(0, 100, 5)
        self.assertIsNone(value)
        self.assertEqual(flag, "ZERO_BASE")

    # 6 Positive -> Negative
    def test_decline_to_loss(self):
        value, flag = calculate_cagr(100, -50, 5)
        self.assertIsNone(value)
        self.assertEqual(flag, "DECLINE_TO_LOSS")

    # 7 Negative -> Positive
    def test_turnaround(self):
        value, flag = calculate_cagr(-100, 100, 5)
        self.assertIsNone(value)
        self.assertEqual(flag, "TURNAROUND")

    # 8 Negative -> Negative
    def test_both_negative(self):
        value, flag = calculate_cagr(-100, -50, 5)
        self.assertIsNone(value)
        self.assertEqual(flag, "BOTH_NEGATIVE")

    # 9 Insufficient Data
    def test_insufficient(self):
        value, flag = calculate_cagr(100, 200, 0)
        self.assertIsNone(value)
        self.assertEqual(flag, "INSUFFICIENT")

    # 10 Long-term CAGR
    def test_long_term(self):
        value, flag = calculate_cagr(500, 1000, 10)
        self.assertEqual(flag, "OK")


if __name__ == "__main__":
    unittest.main()