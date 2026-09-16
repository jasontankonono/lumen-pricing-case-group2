# LUMEN Germany Market Entry Simulator

An interactive web application to explore pricing and channel mix strategies for LUMEN's entry into the German functional beverage market.

## Overview

This simulator addresses the core decision challenge from the LUMEN case: determining the optimal price and channel mix given the tension between:
- **CMO's Objective**: Premium positioning (higher price, brand building)
- **CFO's Objective**: Fast payback (lower price, higher volume, quicker margin recovery)

The tool enables users to test different strategies and see their impact on contribution margin, revenue, volume, and payback period.

## Features

- Interactive price selection (predefined points or custom range)
- Dynamic channel budget allocation (DTC Online, Retail/Grocery, Gym & Office)
- Scenario testing (Base Case)
- Real-time financial projections and key metrics
- Visualizations showing trade-offs between different objectives
- Detailed channel-by-channel breakdowns
- Scenario comparison analysis
- Launch timing analysis with seasonal demand and competitor promotion insights
- Interactive visualization of monthly seasonality and competitor promotional activity

## Data Sources

The simulator integrates data from all 12 case exhibits:
- `price_test_results.csv`: Price sensitivity and acceptance data
- `channel_economics.csv`: Channel-specific economics and margins
- `cost_breakdown.csv`: Per-unit cost structure
- `marketing_funnel_monthly.csv`: Marketing performance metrics (CAC, LTV)
- `market_context.csv`: Market sizing and regional data
- `seasonality_and_weather.csv`: Monthly demand seasonality index and temperature correlations
- `competitor_price_history.csv`: Competitive pricing history and promotional activity over time

## Installation

1. Clone or download this repository
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure you're in the project directory (where `streamlit_app.py` is located)

## Usage

Run the simulator with:
```bash
streamlit run streamlit_app.py
```

The application will open in your default web browser at `http://localhost:8501`.

### How to Use

1. **Select Price**: Choose from the three candidate prices (€1.79, €2.19, €2.59) or set a custom price
2. **Allocate Budget**: Distribute your marketing budget across the three channels (must sum to 100%)
3. **Adjust Scenario**: Test Base Case scenario
4. **Set Launch Timing**: Choose launch month to factor in seasonality and competitor activity
5. **Explore Results**: Use the tabs to view detailed breakdowns, visualizations, scenario comparisons, and launch timing analysis
6. **Iterate**: Adjust parameters to explore different strategies and their outcomes

## Project Structure

- `streamlit_app.py`: Main application code
- `requirements.txt`: Python dependencies
- `data/`: Folder containing all CSV data files
- `DATA_ANALYSIS_FINDINGS.md`: Preliminary data analysis (for reference)
- `LUMEN_Case_Brief.md`: The original case brief

## Key Metrics Explained

- **Contribution Margin**: (Revenue - Variable Costs) / Revenue
- **Payback Period**: Months required to recover customer acquisition costs
- **LTV:CAC Ratio**: Lifetime Value to Customer Acquisition Cost ratio (>1 indicates profitable customer acquisition)
- **Expected Volume**: Forecasted unit sales based on TAM, channel allocation, acceptance rates, and seasonal factors

## Customization

To modify the simulation assumptions:
- Modify TAM assumptions by changing the market segment used in the code
- Adjust scenario multipliers in the sidebar controls
- Edit channel definitions in the calculation functions

## Deployment

The app can be deployed for free using:
- [Streamlit Community Cloud](https://streamlit.io/cloud)
- Heroku
- AWS, Azure, or Google Cloud platforms

Simply push the repository to GitHub and connect it to Streamlit Cloud for instant deployment.

## Team Contributions

### Monika

- Co-developed the case analysis, strategic direction, and overall scope of the pricing simulator with the team.
- Defined prompt-design guidelines, boundaries, and limitations to keep Codex outputs aligned with the case objectives.
- Structured the solution around the relevant sub-categories, decision areas, and strategic dimensions.
- Developed prompts for `lumen-launch-timeline.html`, translating recommendations into a phased launch plan by target segment.
- Developed prompts for `TARGET_SEGMENTATION_STRATEGY.md`, covering evidence-based customer segmentation, city and channel mix, segment positioning, and risks.
- Guided visualization enhancements for the pricing simulator to improve clarity, usability, and presentation.

### Vittoria Monaci

- Developed the Business Summary section, connecting simulator outputs to the wider Germany market-entry strategy.
- Summarised the market opportunity and the core pricing and channel trade-offs.
- Documented and interpreted the key metrics: revenue, expected volume, contribution margin, payback period, and LTV:CAC ratio.
- Integrated findings on pricing, channels, launch timing, seasonality, and competitor activity into decision-ready insights.
- Highlighted the simulator's key assumptions and limitations for decision-makers.

### Jason

- Led the integration and iterative development of the interactive pricing simulator and its decision-support features.
- Coordinated deployment and technical troubleshooting across Vercel, Streamlit, GitHub, dependencies, and repository access.
- Refined the pricing logic by introducing custom-price interpolation and distinct CFO, CMO, and Optimal strategy profiles.
- Reviewed the financial outputs and identified key modelling limitations around market-size units, volume, and payback calculations.
- Directed the evolution of the interface into a clearer executive decision cockpit for CMO/CFO strategy discussions.

## Notes

- All calculations are based on the provided case data
- The simulator makes reasonable extrapolations where German-specific data is unavailable
- Intended for educational and exploratory purposes in the case competition context
- Results should be interpreted as directional guidance rather than precise forecasts

---

*Built for the ATELIA × ESCP LUMEN Pricing & Go-to-Market Case*
