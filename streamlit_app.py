from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from restaurant_model import RestaurantDiagnosticModel, RestaurantInputs


st.set_page_config(
    page_title="Restaurant Feasibility Dashboard",
    page_icon="🍽",
    layout="wide",
)


SCENARIO_PRESETS = {
    "Excel Sample": {
        "area_name": "Sindhubhavan",
        "cuisine_type": "South Indian",
        "target_segment": "Family",
        "average_spend": 500,
        "location_demand_score": 9,
        "seating_capacity": 50,
        "table_turnover_per_day": 2.0,
        "occupancy_rate": 0.7,
        "operating_days_per_month": 26,
        "rent": 85000,
        "staff_salaries": 120000,
        "food_and_beverage_cost": 150000,
        "utilities": 50000,
        "marketing": 25000,
        "maintenance": 10000,
        "packaging_delivery": 10000,
        "other_operating_costs": 50000,
        "interior_ambience_setup": 800000,
        "kitchen_equipment_setup": 600000,
        "furniture_fixtures": 300000,
        "licensing_compliance": 80000,
        "technology_setup": 80000,
        "working_capital_reserve": 200000,
        "other_setup_costs": 50000,
        "food_quality_score": 8,
        "price_market_fit_score": 7,
        "ambience_design_score": 8,
        "service_quality_score": 8,
        "menu_variety_score": 7,
        "online_presence_score": 9,
        "word_of_mouth_score": 6,
        "operational_readiness_score": 7,
        "concept_differentiation_score": 7,
    },
    "Strong Case": {
        "area_name": "Sindhubhavan",
        "cuisine_type": "Multi-Cuisine",
        "target_segment": "Premium",
        "average_spend": 750,
        "location_demand_score": 9,
        "seating_capacity": 70,
        "table_turnover_per_day": 2.4,
        "occupancy_rate": 0.82,
        "operating_days_per_month": 28,
        "rent": 120000,
        "staff_salaries": 220000,
        "food_and_beverage_cost": 320000,
        "utilities": 70000,
        "marketing": 60000,
        "maintenance": 25000,
        "packaging_delivery": 30000,
        "other_operating_costs": 40000,
        "interior_ambience_setup": 1200000,
        "kitchen_equipment_setup": 700000,
        "furniture_fixtures": 450000,
        "licensing_compliance": 100000,
        "technology_setup": 120000,
        "working_capital_reserve": 350000,
        "other_setup_costs": 80000,
        "food_quality_score": 9,
        "price_market_fit_score": 8,
        "ambience_design_score": 9,
        "service_quality_score": 8,
        "menu_variety_score": 8,
        "online_presence_score": 9,
        "word_of_mouth_score": 8,
        "operational_readiness_score": 8,
        "concept_differentiation_score": 9,
    },
    "Average Case": {
        "area_name": "Navrangpura",
        "cuisine_type": "Casual Dining",
        "target_segment": "Mixed",
        "average_spend": 450,
        "location_demand_score": 7,
        "seating_capacity": 55,
        "table_turnover_per_day": 1.8,
        "occupancy_rate": 0.62,
        "operating_days_per_month": 26,
        "rent": 95000,
        "staff_salaries": 130000,
        "food_and_beverage_cost": 140000,
        "utilities": 45000,
        "marketing": 18000,
        "maintenance": 12000,
        "packaging_delivery": 15000,
        "other_operating_costs": 30000,
        "interior_ambience_setup": 750000,
        "kitchen_equipment_setup": 500000,
        "furniture_fixtures": 250000,
        "licensing_compliance": 70000,
        "technology_setup": 80000,
        "working_capital_reserve": 220000,
        "other_setup_costs": 60000,
        "food_quality_score": 7,
        "price_market_fit_score": 7,
        "ambience_design_score": 7,
        "service_quality_score": 6,
        "menu_variety_score": 7,
        "online_presence_score": 6,
        "word_of_mouth_score": 6,
        "operational_readiness_score": 6,
        "concept_differentiation_score": 6,
    },
    "Weak Case": {
        "area_name": "Peripheral Ahmedabad",
        "cuisine_type": "Niche Cafe",
        "target_segment": "Gen-Z",
        "average_spend": 350,
        "location_demand_score": 4,
        "seating_capacity": 40,
        "table_turnover_per_day": 1.3,
        "occupancy_rate": 0.38,
        "operating_days_per_month": 24,
        "rent": 110000,
        "staff_salaries": 100000,
        "food_and_beverage_cost": 90000,
        "utilities": 40000,
        "marketing": 8000,
        "maintenance": 7000,
        "packaging_delivery": 12000,
        "other_operating_costs": 45000,
        "interior_ambience_setup": 650000,
        "kitchen_equipment_setup": 350000,
        "furniture_fixtures": 200000,
        "licensing_compliance": 60000,
        "technology_setup": 70000,
        "working_capital_reserve": 150000,
        "other_setup_costs": 50000,
        "food_quality_score": 6,
        "price_market_fit_score": 4,
        "ambience_design_score": 6,
        "service_quality_score": 5,
        "menu_variety_score": 5,
        "online_presence_score": 4,
        "word_of_mouth_score": 4,
        "operational_readiness_score": 5,
        "concept_differentiation_score": 4,
    },
}

AREA_DEMAND_MAP = {
    "Sindhubhavan": 9,
    "Satellite": 8,
    "Prahladnagar": 8,
    "Bodakdev": 8,
    "Navrangpura": 7,
    "Vastrapur": 7,
    "Bopal": 6,
    "Gota": 5,
    "Maninagar": 6,
    "Chandkheda": 5,
    "Peripheral Ahmedabad": 4,
}


def format_currency(value: float) -> str:
    return f"Rs {value:,.0f}"


def load_sample_json() -> dict[str, object]:
    path = Path("sample_input.json")
    if path.exists():
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    return SCENARIO_PRESETS["Excel Sample"].copy()


def render_sidebar_form(defaults: dict[str, object]) -> dict[str, object]:
    st.sidebar.title("Restaurant Inputs")
    preset_name = st.sidebar.selectbox("Choose a preset", list(SCENARIO_PRESETS.keys()))
    if st.sidebar.button("Load preset"):
        st.session_state["form_defaults"] = SCENARIO_PRESETS[preset_name].copy()
        st.rerun()

    current = st.session_state.get("form_defaults", defaults)

    st.sidebar.subheader("Concept")
    area_options = list(AREA_DEMAND_MAP.keys())
    current_area = str(current["area_name"])
    if current_area not in area_options:
        area_options = [current_area] + area_options

    area_name = st.sidebar.selectbox(
        "Area name",
        area_options,
        index=area_options.index(current_area),
        help="Selecting an area will auto-suggest a location demand score.",
    )
    cuisine_type = st.sidebar.text_input("Cuisine type", value=str(current["cuisine_type"]))
    target_segment = st.sidebar.selectbox(
        "Target segment",
        ["Family", "Premium", "Gen-Z", "Mixed"],
        index=["Family", "Premium", "Gen-Z", "Mixed"].index(str(current["target_segment"])),
    )
    average_spend = st.sidebar.number_input("Average spend", min_value=1.0, value=float(current["average_spend"]), step=50.0)
    suggested_location_score = AREA_DEMAND_MAP.get(area_name, int(current["location_demand_score"]))
    use_area_score = st.sidebar.checkbox(
        "Auto-fill score from area",
        value=True,
        help="Turn this off if you want to manually set the location demand score.",
    )
    location_score_default = suggested_location_score if use_area_score else int(current["location_demand_score"])
    location_demand_score = st.sidebar.slider(
        "Location demand score",
        1,
        10,
        int(location_score_default),
    )
    if use_area_score:
        st.sidebar.caption(f"Suggested score for {area_name}: {suggested_location_score}/10")

    st.sidebar.subheader("Operations")
    seating_capacity = st.sidebar.number_input("Seating capacity", min_value=1, value=int(current["seating_capacity"]))
    table_turnover_per_day = st.sidebar.number_input(
        "Table turnover per day",
        min_value=0.1,
        value=float(current["table_turnover_per_day"]),
        step=0.1,
    )
    occupancy_rate = st.sidebar.slider("Occupancy rate", min_value=0.0, max_value=1.0, value=float(current["occupancy_rate"]), step=0.01)
    operating_days_per_month = st.sidebar.number_input("Operating days per month", min_value=1, max_value=31, value=int(current["operating_days_per_month"]))

    st.sidebar.subheader("Monthly Costs")
    rent = st.sidebar.number_input("Rent", min_value=0.0, value=float(current["rent"]), step=5000.0)
    staff_salaries = st.sidebar.number_input("Staff salaries", min_value=0.0, value=float(current["staff_salaries"]), step=5000.0)
    food_and_beverage_cost = st.sidebar.number_input("Food and beverage cost", min_value=0.0, value=float(current["food_and_beverage_cost"]), step=5000.0)
    utilities = st.sidebar.number_input("Utilities", min_value=0.0, value=float(current["utilities"]), step=5000.0)
    marketing = st.sidebar.number_input("Marketing", min_value=0.0, value=float(current["marketing"]), step=5000.0)
    maintenance = st.sidebar.number_input("Maintenance", min_value=0.0, value=float(current["maintenance"]), step=5000.0)
    packaging_delivery = st.sidebar.number_input("Packaging and delivery", min_value=0.0, value=float(current["packaging_delivery"]), step=5000.0)
    other_operating_costs = st.sidebar.number_input("Other operating costs", min_value=0.0, value=float(current["other_operating_costs"]), step=5000.0)

    st.sidebar.subheader("Setup Investment")
    interior_ambience_setup = st.sidebar.number_input("Interior and ambience", min_value=0.0, value=float(current["interior_ambience_setup"]), step=10000.0)
    kitchen_equipment_setup = st.sidebar.number_input("Kitchen equipment", min_value=0.0, value=float(current["kitchen_equipment_setup"]), step=10000.0)
    furniture_fixtures = st.sidebar.number_input("Furniture and fixtures", min_value=0.0, value=float(current["furniture_fixtures"]), step=10000.0)
    licensing_compliance = st.sidebar.number_input("Licensing and compliance", min_value=0.0, value=float(current["licensing_compliance"]), step=5000.0)
    technology_setup = st.sidebar.number_input("Technology setup", min_value=0.0, value=float(current["technology_setup"]), step=5000.0)
    working_capital_reserve = st.sidebar.number_input("Working capital reserve", min_value=0.0, value=float(current["working_capital_reserve"]), step=10000.0)
    other_setup_costs = st.sidebar.number_input("Other setup costs", min_value=0.0, value=float(current["other_setup_costs"]), step=5000.0)

    st.sidebar.subheader("Demand Scores")
    food_quality_score = st.sidebar.slider("Food quality", 1, 10, int(current["food_quality_score"]))
    price_market_fit_score = st.sidebar.slider("Price-market fit", 1, 10, int(current["price_market_fit_score"]))
    ambience_design_score = st.sidebar.slider("Ambience and design", 1, 10, int(current["ambience_design_score"]))
    service_quality_score = st.sidebar.slider("Service quality", 1, 10, int(current["service_quality_score"]))
    menu_variety_score = st.sidebar.slider("Menu variety", 1, 10, int(current["menu_variety_score"]))
    online_presence_score = st.sidebar.slider("Online presence", 1, 10, int(current["online_presence_score"]))
    word_of_mouth_score = st.sidebar.slider("Word of mouth", 1, 10, int(current["word_of_mouth_score"]))
    operational_readiness_score = st.sidebar.slider("Operational readiness", 1, 10, int(current["operational_readiness_score"]))
    concept_differentiation_score = st.sidebar.slider("Concept differentiation", 1, 10, int(current["concept_differentiation_score"]))

    values = {
        "area_name": area_name,
        "cuisine_type": cuisine_type,
        "target_segment": target_segment,
        "average_spend": average_spend,
        "location_demand_score": location_demand_score,
        "seating_capacity": seating_capacity,
        "table_turnover_per_day": table_turnover_per_day,
        "occupancy_rate": occupancy_rate,
        "operating_days_per_month": operating_days_per_month,
        "rent": rent,
        "staff_salaries": staff_salaries,
        "food_and_beverage_cost": food_and_beverage_cost,
        "utilities": utilities,
        "marketing": marketing,
        "maintenance": maintenance,
        "packaging_delivery": packaging_delivery,
        "other_operating_costs": other_operating_costs,
        "interior_ambience_setup": interior_ambience_setup,
        "kitchen_equipment_setup": kitchen_equipment_setup,
        "furniture_fixtures": furniture_fixtures,
        "licensing_compliance": licensing_compliance,
        "technology_setup": technology_setup,
        "working_capital_reserve": working_capital_reserve,
        "other_setup_costs": other_setup_costs,
        "food_quality_score": food_quality_score,
        "price_market_fit_score": price_market_fit_score,
        "ambience_design_score": ambience_design_score,
        "service_quality_score": service_quality_score,
        "menu_variety_score": menu_variety_score,
        "online_presence_score": online_presence_score,
        "word_of_mouth_score": word_of_mouth_score,
        "operational_readiness_score": operational_readiness_score,
        "concept_differentiation_score": concept_differentiation_score,
    }
    st.session_state["form_defaults"] = values.copy()
    return values


def render_dashboard(result: dict[str, object]) -> None:
    summary = result["diagnostic_summary"]
    demand = result["demand_analysis"]
    profitability = result["profitability_analysis"]
    revenue = result["revenue_analysis"]
    cost_analysis = result["cost_analysis"]

    st.title("Restaurant Feasibility Dashboard")
    st.caption("Python capstone dashboard for restaurant viability, demand scoring, and strategic diagnosis.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Demand Score", demand["demand_score"])
    c2.metric("Success Probability", f"{summary['success_probability']}%")
    c3.metric("Risk Score", f"{summary['risk_score']}%")
    c4.metric("Demand Grade", demand["demand_grade"])

    left, right = st.columns([1.2, 1])

    with left:
        st.subheader("Revenue and Profitability")
        col_a, col_b = st.columns(2)
        col_a.metric("Adjusted Monthly Revenue", format_currency(revenue["adjusted_monthly_revenue"]))
        col_b.metric("Monthly Profit", format_currency(profitability["monthly_profit"]))
        col_a.metric("Annual Profit", format_currency(profitability["annual_profit_estimate"]))
        break_even = profitability["break_even_months"] if profitability["break_even_months"] is not None else "No break-even"
        col_b.metric("Break-even", break_even)
        st.info(
            f"Business Viability: {summary['viability_verdict']} | "
            f"Excel Demand Action: {demand['demand_action']}"
        )

        st.subheader("Recommendations")
        for item in result["recommendations"]:
            st.write(f"- {item}")

    with right:
        st.subheader("Demand Breakdown")
        st.bar_chart(demand["weighted_components"])

        st.subheader("Cost Health")
        cost_rows = []
        for name, details in cost_analysis["cost_breakdown"].items():
            cost_rows.append(
                {
                    "Cost Head": name.replace("_", " ").title(),
                    "Monthly Cost": format_currency(details["monthly_cost"]),
                    "Share of Revenue": f"{details['share_of_revenue'] * 100:.1f}%",
                    "Status": details["status"],
                }
            )
        st.dataframe(cost_rows, use_container_width=True, hide_index=True)

    with st.expander("Full JSON Output"):
        st.json(result)


def main() -> None:
    defaults = st.session_state.get("form_defaults", load_sample_json())
    values = render_sidebar_form(defaults)

    try:
        result = RestaurantDiagnosticModel().evaluate(RestaurantInputs(**values))
    except ValueError as exc:
        st.error(str(exc))
        return

    render_dashboard(result)


if __name__ == "__main__":
    main()
