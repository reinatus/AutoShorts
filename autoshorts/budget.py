from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_UP


MAX_COST_USD = Decimal("0.50")
TARGET_COST_USD = Decimal("0.40")


@dataclass(frozen=True)
class CostItem:
    name: str
    quantity: Decimal
    unit_cost_usd: Decimal

    @property
    def cost_usd(self) -> Decimal:
        return self.quantity * self.unit_cost_usd


class BudgetExceeded(ValueError):
    pass


def estimate_cost(items: list[CostItem]) -> Decimal:
    return sum((item.cost_usd for item in items), Decimal("0")).quantize(
        Decimal("0.0001"), rounding=ROUND_UP
    )


def enforce_budget(items: list[CostItem], cap_usd: Decimal = MAX_COST_USD) -> Decimal:
    total = estimate_cost(items)
    if total > cap_usd:
        raise BudgetExceeded(
            f"Coste previsto ${total} supera el tope estricto ${cap_usd}. No se ejecutó ningún proveedor."
        )
    return total


def optional_ai_seconds_allowed(
    price_per_second_usd: Decimal,
    reserved_cost_usd: Decimal = Decimal("0"),
    cap_usd: Decimal = MAX_COST_USD,
) -> int:
    if price_per_second_usd <= 0:
        raise ValueError("El precio por segundo debe ser mayor que cero")
    remaining = max(Decimal("0"), cap_usd - reserved_cost_usd)
    return int(remaining // price_per_second_usd)

