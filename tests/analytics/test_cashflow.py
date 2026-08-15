import unittest

from src.analytics.cashflow_kpis import (
    free_cash_flow,
    cfo_quality_score,
    capex_intensity,
    fcf_conversion_rate,
    capital_allocation_pattern,
)


class TestCashFlowKPIs(unittest.TestCase):

    # --------------------------------------------------
    # FREE CASH FLOW
    # --------------------------------------------------

    def test_free_cash_flow_positive(self):
        self.assertEqual(
            free_cash_flow(8500, -3200),
            5300
        )

    def test_free_cash_flow_negative(self):
        self.assertEqual(
            free_cash_flow(1000, -2000),
            -1000
        )

    # --------------------------------------------------
    # CFO QUALITY
    # --------------------------------------------------

    def test_cfo_quality_high(self):
        score, label = cfo_quality_score(1200, 1000)

        self.assertEqual(score, 1.2)
        self.assertEqual(label, "High Quality")

    def test_cfo_quality_moderate(self):
        score, label = cfo_quality_score(700, 1000)

        self.assertEqual(score, 0.7)
        self.assertEqual(label, "Moderate")

    def test_cfo_quality_accrual_risk(self):
        score, label = cfo_quality_score(300, 1000)

        self.assertEqual(score, 0.3)
        self.assertEqual(label, "Accrual Risk")

    def test_cfo_quality_zero_pat(self):
        score, label = cfo_quality_score(1000, 0)

        self.assertIsNone(score)
        self.assertIsNone(label)

    # --------------------------------------------------
    # CAPEX INTENSITY
    # --------------------------------------------------

    def test_capex_asset_light(self):
        intensity, label = capex_intensity(-500, 25000)

        self.assertEqual(intensity, 2.0)
        self.assertEqual(label, "Asset Light")

    def test_capex_moderate(self):
        intensity, label = capex_intensity(-1500, 25000)

        self.assertEqual(intensity, 6.0)
        self.assertEqual(label, "Moderate")

    def test_capex_capital_intensive(self):
        intensity, label = capex_intensity(-3000, 25000)

        self.assertEqual(intensity, 12.0)
        self.assertEqual(label, "Capital Intensive")

    def test_capex_zero_sales(self):
        intensity, label = capex_intensity(-3000, 0)

        self.assertIsNone(intensity)
        self.assertIsNone(label)

    # --------------------------------------------------
    # FCF CONVERSION
    # --------------------------------------------------

    def test_fcf_conversion(self):
        result = fcf_conversion_rate(5000, 10000)

        self.assertEqual(result, 50.0)

    def test_fcf_conversion_zero_operating_profit(self):
        result = fcf_conversion_rate(5000, 0)

        self.assertIsNone(result)

    # --------------------------------------------------
    # CAPITAL ALLOCATION
    # --------------------------------------------------

    def test_capital_allocation_shareholder_returns(self):
        result = capital_allocation_pattern(
            1000,
            -500,
            -300,
            "High Quality"
        )

        self.assertEqual(
            result["pattern_label"],
            "Shareholder Returns"
        )

    def test_capital_allocation_reinvestor(self):
        result = capital_allocation_pattern(
            1000,
            -500,
            -300,
            "Moderate"
        )

        self.assertEqual(
            result["pattern_label"],
            "Reinvestor"
        )

    def test_capital_allocation_liquidating_assets(self):
        result = capital_allocation_pattern(
            1000,
            500,
            -300
        )

        self.assertEqual(
            result["pattern_label"],
            "Liquidating Assets"
        )

    def test_capital_allocation_distress(self):
        result = capital_allocation_pattern(
            -1000,
            500,
            300
        )

        self.assertEqual(
            result["pattern_label"],
            "Distress Signal"
        )

    def test_capital_allocation_growth_debt(self):
        result = capital_allocation_pattern(
            -1000,
            -500,
            300
        )

        self.assertEqual(
            result["pattern_label"],
            "Growth Funded by Debt"
        )

    def test_capital_allocation_cash_accumulator(self):
        result = capital_allocation_pattern(
            1000,
            500,
            300
        )

        self.assertEqual(
            result["pattern_label"],
            "Cash Accumulator"
        )

    def test_capital_allocation_pre_revenue(self):
        result = capital_allocation_pattern(
            -1000,
            -500,
            -300
        )

        self.assertEqual(
            result["pattern_label"],
            "Pre-Revenue"
        )

    def test_capital_allocation_mixed(self):
        result = capital_allocation_pattern(
            1000,
            -500,
            300
        )

        self.assertEqual(
            result["pattern_label"],
            "Mixed"
        )

        def test_free_cash_flow_zero_values(self):
            self.assertEqual(
                free_cash_flow(0, 0),
                0
            )

        def test_cfo_quality_exact_boundary(self):
            score, label = cfo_quality_score(500, 1000)

            self.assertEqual(score, 0.5)
            self.assertEqual(label, "Moderate")

        def test_capex_intensity_exact_boundary(self):
            intensity, label = capex_intensity(-2000, 25000)

            self.assertEqual(intensity, 8.0)
            self.assertEqual(label, "Moderate")

if __name__ == "__main__":
    unittest.main()