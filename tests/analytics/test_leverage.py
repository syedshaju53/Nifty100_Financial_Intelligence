import unittest

from src.analytics.ratios import (
    debt_to_equity,
    high_leverage_flag,
    interest_coverage_ratio,
    icr_label,
    icr_warning,
    net_debt,
    asset_turnover
)


class TestLeverageRatios(unittest.TestCase):

    def test_debt_to_equity_normal(self):
        self.assertEqual(
            debt_to_equity(200, 100, 100),
            1.0
        )

    def test_debt_to_equity_debt_free(self):
        self.assertEqual(
            debt_to_equity(0, 100, 100),
            0
        )

    def test_debt_to_equity_negative_equity(self):
        self.assertIsNone(
            debt_to_equity(100, -100, 0)
        )

    def test_high_leverage_flag(self):
        self.assertTrue(
            high_leverage_flag(6, "Industrials")
        )

    def test_financial_sector_no_flag(self):
        self.assertFalse(
            high_leverage_flag(10, "Financials")
        )

    def test_interest_coverage_ratio(self):
        self.assertEqual(
            interest_coverage_ratio(100, 20, 10),
            12.0
        )

    def test_interest_zero(self):
        self.assertIsNone(
            interest_coverage_ratio(100, 20, 0)
        )

    def test_icr_label(self):
        self.assertEqual(
            icr_label(None),
            "Debt Free"
        )

    def test_icr_warning(self):
        self.assertTrue(
            icr_warning(1.2)
        )

    def test_net_debt(self):
        self.assertEqual(
            net_debt(500, 200),
            300
        )

    def test_asset_turnover(self):
        self.assertEqual(
            asset_turnover(1000, 500),
            2.0
        )

    def test_asset_turnover_zero_assets(self):
        self.assertIsNone(
            asset_turnover(1000, 0)
        )


if __name__ == "__main__":
    unittest.main()