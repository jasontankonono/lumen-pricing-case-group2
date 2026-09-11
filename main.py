"""Vercel entrypoint for the LUMEN pricing simulator."""

from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field


ROOT = Path(__file__).parent
DATA = ROOT / "data"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

app = FastAPI(title="LUMEN Germany Market Entry Simulator")


class SimulationInput(BaseModel):
    price: float = Field(default=2.19, gt=0)
    dtc_pct: float = Field(default=40, ge=0)
    retail_pct: float = Field(default=40, ge=0)
    gym_pct: float = Field(default=20, ge=0)
    launch_month: int = Field(default=6, ge=1, le=12)


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA / name)


price_df = read_csv("price_test_results.csv")
marketing_df = read_csv("marketing_funnel_monthly.csv")
market_df = read_csv("market_context.csv")
seasonality_df = read_csv("seasonality_and_weather.csv")
competitor_df = read_csv("competitor_price_history.csv")

recent_marketing = marketing_df.tail(6)
avg_cac = float(recent_marketing["cac_eur"].mean())
avg_ltv = float(recent_marketing["ltv_estimate_eur"].mean())
tam_energy = float(
    market_df[
        (market_df["dimension_type"] == "subcategory")
        & (market_df["name"] == "Energy / focus")
        & (market_df["year"] == 2026)
    ]["value"].iloc[0]
)

competitor_df["month"] = pd.to_datetime(competitor_df["month"])
competitor_df["month_num"] = competitor_df["month"].dt.month
promo_by_month = competitor_df[competitor_df["promo_active"]].groupby("month_num").size()


def calculate_outcomes(inputs: SimulationInput) -> dict:
    total = inputs.dtc_pct + inputs.retail_pct + inputs.gym_pct
    if total <= 0:
        raise HTTPException(status_code=422, detail="At least one channel allocation must be greater than zero.")

    # Preserve the original simulator's behavior: normalize an allocation that is not 100%.
    allocations = {
        "DTC Online": inputs.dtc_pct / total,
        "Retail/Grocery": inputs.retail_pct / total,
        "Gym & Office": inputs.gym_pct / total,
    }
    price_options = sorted(float(price) for price in price_df["price_eur"].unique())
    selected_price = min(price_options, key=lambda value: abs(value - inputs.price))
    price_data = price_df[price_df["price_eur"] == selected_price]
    seasonal_factor = float(
        seasonality_df.loc[seasonality_df["month"] == inputs.launch_month, "seasonality_index_100_avg"].iloc[0]
        / 100
    )

    result = {
        "price_eur": selected_price,
        "total_contribution": 0.0,
        "total_revenue": 0.0,
        "total_units": 0.0,
        "weighted_acceptance": 0.0,
        "weighted_net_price": 0.0,
        "weighted_unit_contribution": 0.0,
        "channel_breakdown": [],
        "allocation_normalized": total != 100,
        "seasonal_factor": seasonal_factor,
    }

    for _, row in price_data.iterrows():
        channel = str(row["channel"])
        allocation = allocations[channel]
        acceptance = min(float(row["estimated_acceptance_pct_of_survey"]) / 100 * seasonal_factor, 1.0)
        net_price = float(row["net_price_to_lumen_eur"])
        unit_contribution = float(row["unit_contribution_eur"])
        expected_units_k = tam_energy * allocation * acceptance / 1000
        revenue = expected_units_k * net_price * 1000
        contribution = expected_units_k * unit_contribution * 1000

        result["total_contribution"] += contribution
        result["total_revenue"] += revenue
        result["total_units"] += expected_units_k
        result["weighted_acceptance"] += acceptance * allocation
        result["weighted_net_price"] += net_price * allocation
        result["weighted_unit_contribution"] += unit_contribution * allocation
        result["channel_breakdown"].append(
            {
                "channel": channel,
                "allocation_pct": allocation * 100,
                "acceptance_pct": acceptance * 100,
                "net_price_eur": net_price,
                "unit_contribution_eur": unit_contribution,
                "expected_units_k": expected_units_k,
                "expected_revenue_eur": revenue,
                "expected_contribution_eur": contribution,
            }
        )

    result["total_margin_pct"] = result["total_contribution"] / result["total_revenue"] * 100
    result["payback_months"] = avg_cac * result["total_units"] * 1000 / result["total_contribution"]
    result["ltv_cac_ratio"] = avg_ltv / avg_cac
    return result


@app.get("/")
def home() -> FileResponse:
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/config")
def config() -> dict:
    return {
        "prices": sorted(float(price) for price in price_df["price_eur"].unique()),
        "months": MONTHS,
    }


@app.get("/api/launch-timing")
def launch_timing() -> dict:
    seasonality = [
        float(seasonality_df.loc[seasonality_df["month"] == month, "seasonality_index_100_avg"].iloc[0])
        for month in range(1, 13)
    ]
    promotions = [int(promo_by_month.get(month, 0)) for month in range(1, 13)]
    return {"months": MONTHS, "seasonality": seasonality, "promotions": promotions}


@app.post("/api/calculate")
def calculate(inputs: SimulationInput) -> dict:
    return calculate_outcomes(inputs)
