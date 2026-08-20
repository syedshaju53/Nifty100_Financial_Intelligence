# ============================================
# Nifty100 Financial Intelligence
# Valuation Tests
# ============================================

import unittest

from src.analytics.valuation import (
    price_to_earnings,
    price_to_book,
    earnings_yield,
    peg_ratio,
    enterprise_value,
    ev_to_ebitda,
    valuation_label,
    valuation_summary,
)


class TestValuation(unittest.TestCase):

    # ----------------------------------------
    # P/E
    # ----------------------------------------

    def test_pe_normal(self):
        self.assertEqual(
            price_to_earnings(1000, 50),
            20.0
        )

    def test_pe_zero_eps(self):
        self.assertIsNone(
            price_to_earnings(1000, 0)
        )

    def test_pe_negative_eps(self):
        self.assertIsNone(
            price_to_earnings(1000, -10)
        )

    # ----------------------------------------
    # P/B
    # ----------------------------------------

    def test_pb_normal(self):
        self.assertEqual(
            price_to_book(600, 200),
            3.0
        )

    def test_pb_zero_book_value(self):
        self.assertIsNone(
            price_to_book(600, 0)
        )

    def test_pb_negative_book_value(self):
        self.assertIsNone(
            price_to_book(600, -100)
        )

    # ----------------------------------------
    # Earnings Yield
    # ----------------------------------------

    def test_earnings_yield_normal(self):
        self.assertEqual(
            earnings_yield(50, 1000),
            5.0
        )

    def test_earnings_yield_zero_price(self):
        self.assertIsNone(
            earnings_yield(50, 0)
        )

    # ----------------------------------------
    # PEG
    # ----------------------------------------

    def test_peg_normal(self):
        self.assertEqual(
            peg_ratio(20, 10),
            2.0
        )

    def test_peg_zero_growth(self):
        self.assertIsNone(
            peg_ratio(20, 0)
        )

    def test_peg_negative_growth(self):
        self.assertIsNone(
            peg_ratio(20, -5)
        )

    # ----------------------------------------
    # Enterprise Value
    # ----------------------------------------

    def test_enterprise_value_normal(self):
        self.assertEqual(
            enterprise_value(
                100000,
                20000,
                10000
            ),
            110000
        )

    def test_enterprise_value_no_debt(self):
        self.assertEqual(
            enterprise_value(
                100000,
                None,
                10000
            ),
            90000
        )

    def test_enterprise_value_no_cash(self):
        self.assertEqual(
            enterprise_value(
                100000,
                20000,
                None
            ),
            120000
        )

    # ----------------------------------------
    # EV / EBITDA
    # ----------------------------------------

    def test_ev_ebitda_normal(self):
        self.assertEqual(
            ev_to_ebitda(100000, 10000),
            10.0
        )

    def test_ev_ebitda_zero(self):
        self.assertIsNone(
            ev_to_ebitda(100000, 0)
        )

    def test_ev_ebitda_negative(self):
        self.assertIsNone(
            ev_to_ebitda(100000, -1000)
        )

    # ----------------------------------------
    # Valuation Labels
    # ----------------------------------------

    def test_valuation_undervalued(self):
        self.assertEqual(
            valuation_label(
                pe_ratio=12,
                pb_ratio=2
            ),
            "Undervalued"
        )

    def test_valuation_fair(self):
        self.assertEqual(
            valuation_label(
                pe_ratio=20,
                pb_ratio=4
            ),
            "Fairly Valued"
        )

    def test_valuation_expensive(self):
        self.assertEqual(
            valuation_label(
                pe_ratio=40,
                pb_ratio=8
            ),
            "Expensive"
        )

    def test_valuation_unknown(self):
        self.assertEqual(
            valuation_label(),
            "Unknown"
        )

    def test_valuation_peg_signal(self):
        self.assertEqual(
            valuation_label(
                pe_ratio=30,
                pb_ratio=7,
                peg=0.8
            ),
            "Undervalued"
        )

    # ----------------------------------------
    # Complete Summary
    # ----------------------------------------

    def test_valuation_summary(self):

        result = valuation_summary(
            price=1000,
            eps=50,
            book_value_per_share=250,
            earnings_growth=10,
            market_cap=100000,
            total_debt=20000,
            cash=10000,
            ebitda=11000,
        )

        self.assertEqual(
            result["pe_ratio"],
            20.0
        )

        self.assertEqual(
            result["pb_ratio"],
            4.0
        )

        self.assertEqual(
            result["earnings_yield"],
            5.0
        )

        self.assertEqual(
            result["peg_ratio"],
            2.0
        )

        self.assertEqual(
            result["enterprise_value"],
            110000
        )

        self.assertEqual(
            result["ev_to_ebitda"],
            10.0
        )

        self.assertEqual(
            result["valuation_label"],
            "Fairly Valued"
        )

    def test_valuation_summary_loss_making_company(self):

        result = valuation_summary(
            price=1000,
            eps=-20,
            book_value_per_share=200,
            earnings_growth=-5,
        )

        self.assertIsNone(
            result["pe_ratio"]
        )

        self.assertEqual(
            result["pb_ratio"],
            5.0
        )

        self.assertIsNone(
            result["peg_ratio"]
        )

        self.assertEqual(
            result["valuation_label"],
            "Fairly Valued"
        )


if __name__ == "__main__":
    unittest.main()
    
    
    