import unittest
import pandas as pd

from src.screener.presets import quality_compounder


class TestPresets(unittest.TestCase):

    def test_quality_compounder(self):

        df = pd.DataFrame({

            "return_on_equity_pct":[20],
            "debt_to_equity":[0.5],
            "free_cash_flow":[100],
            "revenue_cagr_5yr":[15]

        })

        result = quality_compounder(df)

        self.assertEqual(len(result),1)


if __name__ == "__main__":
    unittest.main()