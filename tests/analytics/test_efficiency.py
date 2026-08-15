import unittest

from src.analytics.efficiency import (
    asset_turnover,
    inventory_turnover,
    receivables_turnover,
    days_sales_outstanding,
    working_capital_turnover,
)


class TestEfficiency(unittest.TestCase):

    def test_asset_turnover_normal(self):
        self.assertEqual(asset_turnover(1000, 500), 2.0)

    def test_asset_turnover_zero_assets(self):
        self.assertIsNone(asset_turnover(1000, 0))

    def test_inventory_turnover_normal(self):
        self.assertEqual(inventory_turnover(800, 200), 4.0)

    def test_inventory_turnover_zero_inventory(self):
        self.assertIsNone(inventory_turnover(800, 0))

    def test_receivables_turnover_normal(self):
        self.assertEqual(receivables_turnover(1000, 250), 4.0)

    def test_receivables_turnover_zero_receivables(self):
        self.assertIsNone(receivables_turnover(1000, 0))

    def test_dso_normal(self):
        self.assertEqual(
            days_sales_outstanding(100, 1000),
            36.5
        )

    def test_dso_zero_revenue(self):
        self.assertIsNone(
            days_sales_outstanding(100, 0)
        )

    def test_working_capital_turnover_normal(self):
        self.assertEqual(
            working_capital_turnover(1000, 250),
            4.0
        )

    def test_working_capital_turnover_zero(self):
        self.assertIsNone(
            working_capital_turnover(1000, 0)
        )