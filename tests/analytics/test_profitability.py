import unittest
from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
    validate_operating_profit_margin,
    roce_benchmark
)


class TestProfitabilityRatios(unittest.TestCase):

    # 1. Normal Net Profit Margin
    def test_net_profit_margin(self):
        self.assertEqual(net_profit_margin(200, 1000), 20.00)

    # 2. Zero Sales
    def test_net_profit_margin_zero_sales(self):
        self.assertIsNone(net_profit_margin(100, 0))

    # 3. Normal ROE
    def test_return_on_equity(self):
        self.assertEqual(
            return_on_equity(
                200,
                100,
                900
            ),
            20.00
        )

    # 4. Negative Equity
    def test_negative_equity(self):
        self.assertIsNone(
            return_on_equity(
                100,
                -200,
                100
            )
        )

    # 5. ROCE
    def test_return_on_capital_employed(self):
        self.assertEqual(
            return_on_capital_employed(
                300,
                100,
                900,
                500
            ),
            20.00
        )

    # 6. ROA
    def test_return_on_assets(self):
        self.assertEqual(
            return_on_assets(
                100,
                1000
            ),
            10.00
        )

    # 7. Zero Assets
    def test_return_on_assets_zero(self):
        self.assertIsNone(
            return_on_assets(
                100,
                0
            )
        )

    # 8. Operating Profit Margin
    def test_operating_profit_margin(self):
        self.assertEqual(
            operating_profit_margin(
                250,
                1000
            ),
            25.00)
        
        # OPM mismatch (>1%)
    def test_opm_crosscheck(self):

        computed, mismatch = validate_operating_profit_margin(
            operating_profit=200,
            sales=1000,
            source_opm=25
        )

        self.assertEqual(computed, 20.00)
        self.assertTrue(mismatch)
    
    def test_roce_benchmark_good(self):
        self.assertEqual(
            roce_benchmark(18, "Industrials"),
            "Good"
         )

    def test_roce_benchmark_average(self):
        self.assertEqual(
            roce_benchmark(12, "Industrials"),
            "Average"
        )

    def test_roce_benchmark_poor(self):
        self.assertEqual(
            roce_benchmark(8, "Industrials"),
            "Poor"
        )

    def test_roce_benchmark_financials(self):
        self.assertEqual(
            roce_benchmark(8, "Financials"),
            "Sector Relative"
        )

if __name__ == "__main__":
    unittest.main()