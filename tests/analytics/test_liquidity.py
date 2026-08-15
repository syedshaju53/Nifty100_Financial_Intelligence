import unittest

from src.analytics.liquidity import (
    current_ratio,
    quick_ratio,
    cash_ratio,
    liquidity_label,
)


class TestLiquidity(unittest.TestCase):

    def test_current_ratio_normal(self):
        self.assertEqual(current_ratio(200, 100), 2.0)

    def test_current_ratio_fraction(self):
        self.assertEqual(current_ratio(150, 100), 1.5)

    def test_current_ratio_zero_liabilities(self):
        self.assertIsNone(current_ratio(200, 0))

    def test_quick_ratio_normal(self):
        self.assertEqual(quick_ratio(120, 100), 1.2)

    def test_quick_ratio_zero_liabilities(self):
        self.assertIsNone(quick_ratio(120, 0))

    def test_cash_ratio_normal(self):
        self.assertEqual(cash_ratio(50, 100), 0.5)

    def test_cash_ratio_zero_liabilities(self):
        self.assertIsNone(cash_ratio(50, 0))

    def test_liquidity_strong(self):
        self.assertEqual(liquidity_label(2.5), "Strong")

    def test_liquidity_adequate(self):
        self.assertEqual(liquidity_label(1.5), "Adequate")

    def test_liquidity_weak(self):
        self.assertEqual(liquidity_label(0.8), "Weak")

    def test_liquidity_exact_strong_boundary(self):
        self.assertEqual(liquidity_label(2), "Strong")

    def test_liquidity_exact_adequate_boundary(self):
        self.assertEqual(liquidity_label(1), "Adequate")

    def test_liquidity_unknown(self):
        self.assertEqual(liquidity_label(None), "Unknown")