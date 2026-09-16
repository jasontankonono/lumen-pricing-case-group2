"""Evidence-based price strategy recommendations for LUMEN.

The three profiles are deliberately complete strategies, rather than an
acceptance-rate scenario applied to one manually selected price.
"""

from __future__ import annotations

from statistics import median

import pandas as pd


# €1.99 and €2.39 are interpolated between the three survey-tested prices.
# Prices outside €1.79–€2.59 should be tested before being recommended.
CANDIDATE_PRICES = (1.79, 1.99, 2.19, 2.39, 2.59)

PROFILE_DEFINITIONS = {
    "CFO — Cash efficiency": {
        "objective": "Highest revenue while protecting payback",
        "allocations": {"DTC Online": 30, "Retail/Grocery": 55, "Gym & Office": 15},
        "acceptance_multiplier": 1.05,
        "candidates": (1.79, 1.99, 2.19, 2.39),
        "weights": {"revenue": 0.60, "payback": 0.30, "contribution": 0.10},
    },
    "CMO — Premium positioning": {
        "objective": "Premium price and margin, with a credible demand floor",
        "allocations": {"DTC Online": 45, "Retail/Grocery": 20, "Gym & Office": 35},
        "acceptance_multiplier": 0.90,
        "candidates": (2.39, 2.59),
        "weights": {"price": 0.45, "margin": 0.35, "contribution": 0.20},
    },
    "Optimal — Balanced recommendation": {
        "objective": "Best combined revenue, contribution, margin, payback, and premium-market fit",
        "allocations": {"DTC Online": 40, "Retail/Grocery": 35, "Gym & Office": 25},
        "acceptance_multiplier": 1.00,
        "candidates": CANDIDATE_PRICES,
        "weights": {"revenue": 0.30, "contribution": 0.25, "margin": 0.20, "payback": 0.15, "premium_fit": 0.10},
    },
}


def _interpolate(channel_rows: pd.DataFrame, price: float, column: str) -> float:
    """Linear interpolation restricted to the observed price-test range."""
    rows = channel_rows.sort_values("price_eur")
    lower, upper = rows["price_eur"].iloc[0], rows["price_eur"].iloc[-1]
    if not lower <= price <= upper:
        raise ValueError(f"Price €{price:.2f} is outside the validated €{lower:.2f}–€{upper:.2f} test range.")
    below = rows[rows["price_eur"] <= price].iloc[-1]
    above = rows[rows["price_eur"] >= price].iloc[0]
    if below["price_eur"] == above["price_eur"]:
        return float(below[column])
    share = (price - below["price_eur"]) / (above["price_eur"] - below["price_eur"])
    return float(below[column] + share * (above[column] - below[column]))


def interpolate_price_data(price_df: pd.DataFrame, price: float) -> pd.DataFrame:
    """Create channel economics for any price inside the survey-tested range.

    This is deliberately interpolation, not a nearest-price fallback: a €2.31
    selection gets economics between the €2.19 and €2.59 observations.
    """
    lower, upper = float(price_df["price_eur"].min()), float(price_df["price_eur"].max())
    if not lower <= price <= upper:
        raise ValueError(f"Price must be within the validated €{lower:.2f}–€{upper:.2f} range.")

    rows = []
    for channel in price_df["channel"].unique():
        channel_rows = price_df[price_df["channel"] == channel]
        net_price = _interpolate(channel_rows, price, "net_price_to_lumen_eur")
        unit_contribution = _interpolate(channel_rows, price, "unit_contribution_eur")
        rows.append({
            "price_eur": price,
            "channel": channel,
            "estimated_acceptance_pct_of_survey": _interpolate(channel_rows, price, "estimated_acceptance_pct_of_survey"),
            "net_price_to_lumen_eur": net_price,
            "unit_contribution_eur": unit_contribution,
            "contribution_margin_pct": unit_contribution / net_price * 100 if net_price else 0,
        })
    return pd.DataFrame(rows)


def calculate_profile_outcome(
    price_df: pd.DataFrame,
    tam_eur: float,
    avg_cac: float,
    avg_ltv: float,
    price: float,
    allocations: dict[str, float],
    acceptance_multiplier: float,
    seasonal_factor: float,
    competitive_impact: float,
) -> dict:
    """Calculate an annual strategy outcome from a price and channel package."""
    total_allocation = sum(allocations.values())
    if total_allocation <= 0:
        raise ValueError("Strategy channel allocations must be positive.")

    result = {"price_eur": price, "total_revenue": 0.0, "total_contribution": 0.0, "total_units": 0.0,
              "channel_breakdown": []}
    for channel, allocation_pct in allocations.items():
        rows = price_df[price_df["channel"] == channel]
        allocation = allocation_pct / total_allocation
        acceptance = min(
            _interpolate(rows, price, "estimated_acceptance_pct_of_survey") / 100
            * acceptance_multiplier * seasonal_factor * competitive_impact,
            1.0,
        )
        net_price = _interpolate(rows, price, "net_price_to_lumen_eur")
        unit_contribution = _interpolate(rows, price, "unit_contribution_eur")
        # The market data is in EUR, so convert it to an estimated consumer-unit base.
        expected_units_k = (tam_eur / price) * allocation * acceptance / 1000
        revenue = expected_units_k * net_price * 1000
        contribution = expected_units_k * unit_contribution * 1000
        result["total_units"] += expected_units_k
        result["total_revenue"] += revenue
        result["total_contribution"] += contribution
        result["channel_breakdown"].append({"channel": channel, "allocation_pct": allocation * 100,
                                            "acceptance_pct": acceptance * 100, "net_price_eur": net_price,
                                            "unit_contribution_eur": unit_contribution,
                                            "expected_units_k": expected_units_k,
                                            "expected_revenue_eur": revenue,
                                            "expected_contribution_eur": contribution})

    result["total_margin_pct"] = result["total_contribution"] / result["total_revenue"] * 100
    weighted_contribution = sum(
        item["unit_contribution_eur"] * item["allocation_pct"] / 100 for item in result["channel_breakdown"]
    )
    result["payback_months"] = avg_cac / weighted_contribution
    result["ltv_cac_ratio"] = avg_ltv / avg_cac
    return result


def _scaled(values: dict[float, float], invert: bool = False) -> dict[float, float]:
    low, high = min(values.values()), max(values.values())
    if high == low:
        return {key: 1.0 for key in values}
    scaled = {key: (value - low) / (high - low) for key, value in values.items()}
    return {key: 1 - value for key, value in scaled.items()} if invert else scaled


def generate_strategy_recommendations(
    price_df: pd.DataFrame,
    competitor_prices: pd.DataFrame,
    tam_eur: float,
    avg_cac: float,
    avg_ltv: float,
    seasonal_factor: float = 1.0,
    competitive_impact: float = 1.0,
) -> list[dict]:
    """Return one distinct, transparent recommendation for each stakeholder."""
    premium_reference = median(
        competitor_prices.loc[competitor_prices["positioning"].str.contains("Premium", case=False), "price_eur"]
    )
    chosen_prices: set[float] = set()
    recommendations = []

    for name, profile in PROFILE_DEFINITIONS.items():
        outcomes = {
            price: calculate_profile_outcome(price_df, tam_eur, avg_cac, avg_ltv, price,
                                             profile["allocations"], profile["acceptance_multiplier"],
                                             seasonal_factor, competitive_impact)
            for price in profile["candidates"]
        }
        metrics = {
            "price": _scaled({price: outcome["price_eur"] for price, outcome in outcomes.items()}),
            "revenue": _scaled({price: outcome["total_revenue"] for price, outcome in outcomes.items()}),
            "contribution": _scaled({price: outcome["total_contribution"] for price, outcome in outcomes.items()}),
            "margin": _scaled({price: outcome["total_margin_pct"] for price, outcome in outcomes.items()}),
            "payback": _scaled({price: outcome["payback_months"] for price, outcome in outcomes.items()}, invert=True),
            "premium_fit": _scaled({price: -abs(price - premium_reference) for price in outcomes}),
        }
        scores = {price: sum(profile["weights"].get(metric, 0) * metrics[metric][price] for metric in metrics)
                  for price in outcomes}
        available = [price for price in outcomes if price not in chosen_prices] or list(outcomes)
        selected = max(available, key=lambda price: scores[price])
        chosen_prices.add(selected)
        result = outcomes[selected]
        result.update({"strategy": name, "objective": profile["objective"], "score": scores[selected],
                       "allocations": profile["allocations"], "price_basis": "Survey-tested" if selected in (1.79, 2.19, 2.59) else "Interpolated between survey-tested prices"})
        recommendations.append(result)
    return recommendations
