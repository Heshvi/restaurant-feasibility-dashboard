from __future__ import annotations

from dataclasses import asdict
from math import ceil
from typing import Any

from .schemas import RestaurantInputs


class RestaurantDiagnosticModel:
    """Rule-based diagnostic model derived from the Excel feasibility workbook."""

    DEMAND_WEIGHTS = {
        "food_quality_score": 0.15,
        "price_market_fit_score": 0.13,
        "ambience_design_score": 0.13,
        "service_quality_score": 0.12,
        "menu_variety_score": 0.09,
        "location_demand_score": 0.09,
        "online_presence_score": 0.08,
        "word_of_mouth_score": 0.07,
        "operational_readiness_score": 0.07,
        "concept_differentiation_score": 0.07,
    }

    COST_BENCHMARKS = {
        "food_and_beverage_cost": (0.25, 0.35),
        "staff_salaries": (0.20, 0.30),
        "rent": (0.08, 0.15),
        "marketing": (0.03, 0.06),
        "utilities": (0.05, 0.10),
        "maintenance": (0.01, 0.03),
        "packaging_delivery": (0.02, 0.05),
        "other_operating_costs": (0.01, 0.04),
    }

    DEMAND_ACTIONS = {
        "A+": "Launch with confidence and scale customer acquisition early.",
        "A": "Strong concept. Focus on execution discipline and customer retention.",
        "B": "Sharpen the USP and strengthen weak customer-facing levers before launch.",
        "C": "Rework the concept or operating model before committing more capital.",
        "D": "Do not launch yet. Fix the core proposition and cost structure first.",
    }

    def evaluate(self, inputs: RestaurantInputs) -> dict[str, Any]:
        inputs.validate()

        demand_score = self._calculate_demand_score(inputs)
        demand_grade = self._grade_demand(demand_score)
        revenue_multiplier = self._revenue_multiplier(demand_score)
        revenue_metrics = self._calculate_revenue(inputs, revenue_multiplier)
        cost_metrics = self._calculate_costs(inputs, revenue_metrics["adjusted_monthly_revenue"])
        profitability = self._calculate_profitability(
            revenue_metrics=revenue_metrics,
            cost_metrics=cost_metrics,
            total_initial_investment=self._total_initial_investment(inputs),
        )
        success_probability = self._calculate_success_probability(
            demand_score=demand_score,
            profit_margin=profitability["profit_margin"],
            break_even_months=profitability["break_even_months"],
            healthy_cost_ratio=cost_metrics["healthy_cost_ratio"],
            working_capital_months=profitability["working_capital_months"],
        )
        risk_score = round(100 - success_probability, 2)
        recommendations = self._generate_recommendations(
            inputs=inputs,
            demand_score=demand_score,
            demand_grade=demand_grade,
            cost_metrics=cost_metrics,
            profitability=profitability,
        )

        return {
            "restaurant_profile": {
                "area_name": inputs.area_name,
                "cuisine_type": inputs.cuisine_type,
                "target_segment": inputs.target_segment,
            },
            "inputs": asdict(inputs),
            "demand_analysis": {
                "demand_score": round(demand_score, 2),
                "demand_grade": demand_grade,
                "demand_action": self.DEMAND_ACTIONS[demand_grade],
                "weighted_components": self._demand_components(inputs),
            },
            "revenue_analysis": revenue_metrics,
            "cost_analysis": cost_metrics,
            "profitability_analysis": profitability,
            "diagnostic_summary": {
                "success_probability": success_probability,
                "risk_score": risk_score,
                "viability_verdict": profitability["viability_verdict"],
            },
            "recommendations": recommendations,
        }

    def _demand_components(self, inputs: RestaurantInputs) -> dict[str, float]:
        return {
            metric: round(getattr(inputs, metric) * weight, 3)
            for metric, weight in self.DEMAND_WEIGHTS.items()
        }

    def _calculate_demand_score(self, inputs: RestaurantInputs) -> float:
        return sum(getattr(inputs, metric) * weight for metric, weight in self.DEMAND_WEIGHTS.items())

    def _grade_demand(self, demand_score: float) -> str:
        if demand_score >= 8.5:
            return "A+"
        if demand_score >= 7.0:
            return "A"
        if demand_score >= 6.0:
            return "B"
        if demand_score >= 5.0:
            return "C"
        return "D"

    def _revenue_multiplier(self, demand_score: float) -> float:
        if demand_score >= 8.5:
            return 1.2
        if demand_score >= 7.0:
            return 1.1
        if demand_score >= 6.0:
            return 1.0
        if demand_score >= 5.0:
            return 0.85
        return 0.7

    def _calculate_revenue(self, inputs: RestaurantInputs, revenue_multiplier: float) -> dict[str, float | str]:
        customers_per_day = (
            inputs.seating_capacity
            * inputs.table_turnover_per_day
            * inputs.occupancy_rate
        )
        customers_per_month = customers_per_day * inputs.operating_days_per_month
        base_monthly_revenue = customers_per_month * inputs.average_spend
        adjusted_monthly_revenue = base_monthly_revenue * revenue_multiplier

        return {
            "customers_per_day": round(customers_per_day, 2),
            "customers_per_month": round(customers_per_month, 2),
            "base_monthly_revenue": round(base_monthly_revenue, 2),
            "revenue_multiplier": revenue_multiplier,
            "adjusted_monthly_revenue": round(adjusted_monthly_revenue, 2),
            "conservative_revenue": round(adjusted_monthly_revenue * 0.85, 2),
            "base_case_revenue": round(adjusted_monthly_revenue, 2),
            "optimistic_revenue": round(adjusted_monthly_revenue * 1.15, 2),
            "year_1_revenue": round(adjusted_monthly_revenue * 12, 2),
            "year_2_revenue": round(adjusted_monthly_revenue * 12 * 1.10, 2),
            "year_3_revenue": round(adjusted_monthly_revenue * 12 * 1.10 * 1.15, 2),
        }

    def _calculate_costs(
        self,
        inputs: RestaurantInputs,
        adjusted_monthly_revenue: float,
    ) -> dict[str, Any]:
        monthly_costs = {
            "food_and_beverage_cost": inputs.food_and_beverage_cost,
            "staff_salaries": inputs.staff_salaries,
            "rent": inputs.rent,
            "marketing": inputs.marketing,
            "utilities": inputs.utilities,
            "maintenance": inputs.maintenance,
            "packaging_delivery": inputs.packaging_delivery,
            "other_operating_costs": inputs.other_operating_costs,
        }

        benchmark_rows: dict[str, dict[str, float | str]] = {}
        healthy_count = 0
        for cost_name, amount in monthly_costs.items():
            ratio = 0.0 if adjusted_monthly_revenue <= 0 else amount / adjusted_monthly_revenue
            benchmark_min, benchmark_max = self.COST_BENCHMARKS[cost_name]
            if adjusted_monthly_revenue <= 0:
                status = "No revenue"
            elif ratio < benchmark_min:
                status = "Underinvestment"
            elif ratio > benchmark_max:
                status = "Overinvestment"
            else:
                status = "Healthy"
                healthy_count += 1

            benchmark_rows[cost_name] = {
                "monthly_cost": round(amount, 2),
                "share_of_revenue": round(ratio, 4),
                "benchmark_min": benchmark_min,
                "benchmark_max": benchmark_max,
                "status": status,
            }

        total_monthly_costs = sum(monthly_costs.values())
        healthy_ratio = healthy_count / len(monthly_costs)
        return {
            "cost_breakdown": benchmark_rows,
            "total_monthly_costs": round(total_monthly_costs, 2),
            "healthy_cost_ratio": round(healthy_ratio, 2),
        }

    def _calculate_profitability(
        self,
        revenue_metrics: dict[str, Any],
        cost_metrics: dict[str, Any],
        total_initial_investment: float,
    ) -> dict[str, Any]:
        adjusted_revenue = revenue_metrics["adjusted_monthly_revenue"]
        conservative_revenue = revenue_metrics["conservative_revenue"]
        optimistic_revenue = revenue_metrics["optimistic_revenue"]
        total_monthly_costs = cost_metrics["total_monthly_costs"]
        monthly_profit = adjusted_revenue - total_monthly_costs
        profit_margin = 0.0 if adjusted_revenue <= 0 else monthly_profit / adjusted_revenue
        annual_profit = monthly_profit * 12
        break_even_months = None if monthly_profit <= 0 else ceil(total_initial_investment / monthly_profit)
        conservative_profit = conservative_revenue - total_monthly_costs
        optimistic_profit = optimistic_revenue - total_monthly_costs
        conservative_break_even = None if conservative_profit <= 0 else ceil(total_initial_investment / conservative_profit)
        optimistic_break_even = None if optimistic_profit <= 0 else ceil(total_initial_investment / optimistic_profit)
        working_capital_months = 0.0 if total_monthly_costs <= 0 else total_initial_investment / total_monthly_costs

        if monthly_profit <= 0:
            verdict = "Not Viable"
        elif break_even_months is not None and break_even_months <= 24 and profit_margin >= 0.15:
            verdict = "Viable"
        else:
            verdict = "Marginal"

        return {
            "monthly_profit": round(monthly_profit, 2),
            "profit_margin": round(profit_margin, 4),
            "annual_profit_estimate": round(annual_profit, 2),
            "total_initial_investment": round(total_initial_investment, 2),
            "break_even_months": break_even_months,
            "conservative_break_even_months": conservative_break_even,
            "optimistic_break_even_months": optimistic_break_even,
            "working_capital_months": round(working_capital_months, 2),
            "viability_verdict": verdict,
        }

    def _calculate_success_probability(
        self,
        demand_score: float,
        profit_margin: float,
        break_even_months: int | None,
        healthy_cost_ratio: float,
        working_capital_months: float,
    ) -> float:
        demand_component = (demand_score / 10) * 0.40
        margin_component = min(max(profit_margin, 0.0), 0.25) / 0.25 * 0.25

        if break_even_months is None:
            payback_component = 0.0
        else:
            capped = min(max(break_even_months, 6), 36)
            payback_component = ((36 - capped) / 30) * 0.20

        cost_component = healthy_cost_ratio * 0.10
        capital_component = min(working_capital_months, 12) / 12 * 0.05

        probability = (demand_component + margin_component + payback_component + cost_component + capital_component) * 100
        return round(max(0.0, min(probability, 100.0)), 2)

    def _total_initial_investment(self, inputs: RestaurantInputs) -> float:
        return (
            inputs.interior_ambience_setup
            + inputs.kitchen_equipment_setup
            + inputs.furniture_fixtures
            + inputs.licensing_compliance
            + inputs.technology_setup
            + inputs.working_capital_reserve
            + inputs.other_setup_costs
        )

    def _generate_recommendations(
        self,
        inputs: RestaurantInputs,
        demand_score: float,
        demand_grade: str,
        cost_metrics: dict[str, Any],
        profitability: dict[str, Any],
    ) -> list[str]:
        recommendations: list[str] = []

        if demand_grade in {"C", "D"}:
            recommendations.append("Revisit the concept-market fit before expansion or launch.")

        if inputs.online_presence_score < 6:
            recommendations.append("Strengthen Zomato, Google, and Instagram visibility to improve digital discovery.")

        if inputs.price_market_fit_score < 6:
            recommendations.append("Refine menu pricing to match local income levels and competitor positioning.")

        if inputs.word_of_mouth_score < 6:
            recommendations.append("Design customer referral hooks and signature items that encourage repeat visits.")

        if inputs.operational_readiness_score < 7:
            recommendations.append("Improve SOPs, staffing readiness, and service speed before scaling demand.")

        if inputs.concept_differentiation_score < 7:
            recommendations.append("Sharpen the restaurant USP so the concept is easier to remember and recommend.")

        for cost_name, details in cost_metrics["cost_breakdown"].items():
            status = details["status"]
            if status == "Overinvestment":
                recommendations.append(
                    f"Reduce or renegotiate {cost_name.replace('_', ' ')} because it is above benchmark."
                )
            elif status == "Underinvestment" and cost_name in {"marketing", "maintenance", "staff_salaries"}:
                recommendations.append(
                    f"Increase {cost_name.replace('_', ' ')} toward benchmark to avoid weak execution."
                )

        if profitability["monthly_profit"] <= 0:
            recommendations.append("Current structure is loss-making; cut fixed costs or raise throughput before launch.")
        elif profitability["break_even_months"] and profitability["break_even_months"] > 24:
            recommendations.append("Payback is slow, so phase the capex rollout and protect liquidity.")

        if demand_score >= 7 and profitability["monthly_profit"] > 0:
            recommendations.append("The concept is commercially promising; pilot the outlet and validate assumptions with real customers.")

        deduped: list[str] = []
        seen = set()
        for item in recommendations:
            if item not in seen:
                deduped.append(item)
                seen.add(item)
        return deduped
