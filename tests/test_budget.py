from decimal import Decimal
import unittest

from autoshorts.budget import BudgetExceeded, CostItem, enforce_budget, estimate_cost, optional_ai_seconds_allowed


class BudgetTests(unittest.TestCase):
    def test_procedural_pipeline_has_no_api_cost(self) -> None:
        self.assertEqual(enforce_budget([]), Decimal("0.0000"))

    def test_full_paid_video_is_blocked(self) -> None:
        items = [CostItem("video API", Decimal("40"), Decimal("0.05"))]
        self.assertEqual(estimate_cost(items), Decimal("2.0000"))
        with self.assertRaises(BudgetExceeded):
            enforce_budget(items)

    def test_optional_seconds_respect_cap(self) -> None:
        self.assertEqual(optional_ai_seconds_allowed(Decimal("0.05"), Decimal("0.10")), 8)


if __name__ == "__main__":
    unittest.main()

