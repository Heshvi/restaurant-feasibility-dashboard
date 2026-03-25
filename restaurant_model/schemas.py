from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RestaurantInputs:
    area_name: str
    cuisine_type: str
    target_segment: str
    average_spend: float
    location_demand_score: float
    seating_capacity: int
    table_turnover_per_day: float
    occupancy_rate: float
    operating_days_per_month: int
    rent: float
    staff_salaries: float
    food_and_beverage_cost: float
    utilities: float
    marketing: float
    maintenance: float
    packaging_delivery: float
    other_operating_costs: float
    interior_ambience_setup: float
    kitchen_equipment_setup: float
    furniture_fixtures: float
    licensing_compliance: float
    technology_setup: float
    working_capital_reserve: float
    other_setup_costs: float
    food_quality_score: float
    price_market_fit_score: float
    ambience_design_score: float
    service_quality_score: float
    menu_variety_score: float
    online_presence_score: float
    word_of_mouth_score: float
    operational_readiness_score: float
    concept_differentiation_score: float

    def validate(self) -> None:
        bounded_scores = {
            "location_demand_score": self.location_demand_score,
            "food_quality_score": self.food_quality_score,
            "price_market_fit_score": self.price_market_fit_score,
            "ambience_design_score": self.ambience_design_score,
            "service_quality_score": self.service_quality_score,
            "menu_variety_score": self.menu_variety_score,
            "online_presence_score": self.online_presence_score,
            "word_of_mouth_score": self.word_of_mouth_score,
            "operational_readiness_score": self.operational_readiness_score,
            "concept_differentiation_score": self.concept_differentiation_score,
        }
        for name, value in bounded_scores.items():
            if not 1 <= value <= 10:
                raise ValueError(f"{name} must be between 1 and 10. Got {value}.")

        if not 0 <= self.occupancy_rate <= 1:
            raise ValueError("occupancy_rate must be between 0 and 1.")

        positive_fields = {
            "average_spend": self.average_spend,
            "seating_capacity": self.seating_capacity,
            "table_turnover_per_day": self.table_turnover_per_day,
            "operating_days_per_month": self.operating_days_per_month,
        }
        for name, value in positive_fields.items():
            if value <= 0:
                raise ValueError(f"{name} must be greater than 0. Got {value}.")
