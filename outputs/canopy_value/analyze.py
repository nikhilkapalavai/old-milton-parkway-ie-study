"""Decision thresholds from saved traffic results; not a tree appraisal or full BCA.

Uses only the standard library. Run from any working directory. Currency for the
traffic scenarios is constant 2024 USD; present values are at a hypothetical
opening, not a dated forecast. Historical concept costs are kept separate.
"""
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRAFFIC = HERE.parent / "canopy_tradeoff"
ASSUMPTIONS = {
    "equivalent_weekdays_per_year": 250,
    "value_per_person_hour_2024_usd": 21.80,
    "occupancy_reference": 1.34,
    "occupancy_sensitivity": [1.0, 1.34, 1.41],
    "personal_time_value_sensitivity_2024_usd": 20.10,
    "years_reference": 20,
    "real_discount_rate_reference": 0.07,
    "equivalent_weekdays_sensitivity": [200, 250, 260],
    "horizons_sensitivity": [10, 20, 30],
    "real_discount_rates_sensitivity": [0.03, 0.07],
    "incremental_net_resource_cost_pv_scenarios_2024_usd": [0, 5e6, 10e6, 15e6, 20e6],
    "tree_inventory": None,
    "canopy_loss_value": None,
    "incremental_actual_four_to_six_lane_cost": None,
    "growth_forecast": None,
    "interpretation": "250 identical modeled weekdays per year and unchanged delay benefits are illustrative assumptions, not measured annual performance or a demand forecast. 1.34 is a weekday-peak occupancy reference; the modeled windows also contain off-peak hours, so 1.41 is tested separately. All vehicles are provisionally valued as passenger vehicles. No freight, safety, emissions, reliability, construction disruption or nonmodeled-hour benefits are credited here.",
}
SOURCES = {
    "USDOT_2026_BCA": {
        "url": "https://www.transportation.gov/sites/dot.gov/files/2025-12/Benefit%20Cost%20Analysis%20Guidance%202026%20Update%20(Final).pdf",
        "pages_one_based": [13, 40, 41],
        "use": "2024 USD/person-hour: personal 20.10, all purposes 21.80. Passenger occupancy: weekday peak 1.34, weekday off-peak 1.41. Real discount rate 7%. We use an opening-relative sensitivity calculation, not USDOT's full dated grant BCA procedure.",
    },
    "GDOT_concept": {
        "url": "https://www.dot.ga.gov/_layouts/GDOT.SharePoint.CustomHttpHandlers/PWDocumentDownloadHandler.ashx?DocGUID=11d2e65d-2e90-4a1a-a0a8-e75ae818d78f&Filename=0017187_CR_MAR2022.pdf",
        "pages_one_based": [13, 14],
        "local_excerpt": "../evidence_excerpt.pdf, excerpt pages 8 and 9",
        "use": "Historical concept cost estimates and alternatives; operations-and-safety B/C ratio 2.98 is reported by GDOT, not independently reproduced here.",
    },
    "iTree_requirements": {
        "url": "https://www.itreetools.org/faqs_home",
        "use": "Individual tree benefits require location, species and diameter; size/health and replacement growth affect benefits over time. No corridor inventory was located in the records reviewed.",
    },
}


def annuity(years, rate):
    return sum((1 + rate) ** -year for year in range(1, years + 1))


def source_hash(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def paired_benefit(a, b):
    """Aggregate queue vehicle-time without assuming full-corridor trips."""
    assert a["all_complete"] and b["all_complete"], "Censored runs cannot support totals"
    am, bm = a["mean"], b["mean"]
    for movement in ("main", "side"):
        assert math.isclose(am[f"{movement}_generated"], bm[f"{movement}_generated"], abs_tol=1e-5)
    hours = {
        movement: am[f"{movement}_generated"]
        * (am[f"{movement}_delay_min"] - bm[f"{movement}_delay_min"]) / 60
        for movement in ("main", "side")
    }
    # Independently check movement-level aggregation against the all-trip metric.
    all_hours = (am["all_delay_min"] - bm["all_delay_min"]) * (
        am["main_generated"] + am["side_generated"]
    ) / 60
    assert math.isclose(sum(hours.values()), all_hours, abs_tol=1e-7)
    return {
        "main_entering_model_trips": am["main_generated"],
        "synthetic_side_trips": am["side_generated"],
        "main_vehicle_hours_saved_by_six_lanes": hours["main"],
        "side_vehicle_hours_saved_by_six_lanes": hours["side"],
        "total_vehicle_hours_saved_by_six_lanes": all_hours,
    }


def main():
    r = json.loads((TRAFFIC / "results.json").read_text())
    t = json.loads((TRAFFIC / "tradeoffs.json").read_text())
    comparisons = {}
    for label in ("balanced_four_lane", "minimum_all_trip_delay_four_lane"):
        periods = {}
        for period, direction in (("AM", "west"), ("PM", "east")):
            six = next(x for x in r["summary"] if x["period"] == period and x["case"] == "base" and x["total_lanes"] == 6)
            if label == "balanced_four_lane":
                four = next(x["result"] for x in t["nominal_alternatives"] if x["period"] == period and x["plan"]["id"] == f"4L_C120_G84_{direction}")
            else:
                four = next(x for x in r["summary"] if x["period"] == period and x["case"] == "base" and x["total_lanes"] == 4)
            periods[period] = paired_benefit(four, six)
        total = sum(x["total_vehicle_hours_saved_by_six_lanes"] for x in periods.values())
        side = sum(x["side_vehicle_hours_saved_by_six_lanes"] for x in periods.values())
        annual = total * ASSUMPTIONS["equivalent_weekdays_per_year"] * ASSUMPTIONS["occupancy_reference"] * ASSUMPTIONS["value_per_person_hour_2024_usd"]
        pv = annual * annuity(ASSUMPTIONS["years_reference"], ASSUMPTIONS["real_discount_rate_reference"])
        comparisons[label] = {
            "periods": periods,
            "total_vehicle_hours_saved_per_modeled_day": total,
            "synthetic_side_street_share": side / total,
            "annual_time_value_reference_2024_usd": annual,
            "twenty_year_time_value_pv_at_opening_2024_usd": pv,
            "maximum_canopy_loss_pv_for_time_only_break_even": [
                {"incremental_net_resource_cost_pv_2024_usd": c, "canopy_loss_budget_pv_2024_usd": pv - c}
                for c in ASSUMPTIONS["incremental_net_resource_cost_pv_scenarios_2024_usd"]
            ],
        }
    ref = comparisons["balanced_four_lane"]
    sensitivities = []
    for days in ASSUMPTIONS["equivalent_weekdays_sensitivity"]:
        for occupancy in ASSUMPTIONS["occupancy_sensitivity"]:
            for value in (20.10, 21.80):
                for years in ASSUMPTIONS["horizons_sensitivity"]:
                    for rate in ASSUMPTIONS["real_discount_rates_sensitivity"]:
                        annual = ref["total_vehicle_hours_saved_per_modeled_day"] * days * occupancy * value
                        sensitivities.append(dict(days=days, occupancy=occupancy, value_per_person_hour_2024_usd=value, years=years, real_discount_rate=rate, annual_time_value_2024_usd=annual, time_value_pv_at_opening_2024_usd=annual*annuity(years,rate)))
    outside_premium = 41_800_000 - 29_196_795
    out = {
        "question": "Was the Old Milton median canopy worth losing?",
        "finding": "Undetermined by available evidence. Traffic benefits can be substantial; an actual canopy appraisal and comparable four-lane alternative cost are missing. Neither definite yes nor definite no is established.",
        "assumptions": ASSUMPTIONS,
        "sources": SOURCES,
        "input_hashes_lf": {f.name: source_hash(f) for f in (TRAFFIC / "results.json", TRAFFIC / "tradeoffs.json")},
        "comparisons": comparisons,
        "sensitivity_scenarios_not_confidence_intervals": sensitivities,
        "historical_outside_vs_inside_concept_costs": {
            "inside_total": 29_196_795,
            "outside_total": 41_800_000,
            "total_premium": outside_premium,
            "right_of_way_premium": 11_200_000 - 1_506_000,
            "additional_parcels": 63 - 18,
            "additional_construction_months": 42 - 30,
            "currency_basis": "Historical March 2021 estimates in March 2022 concept package; not converted to 2024 dollars and not subtracted from the time-value PV.",
            "illustrative_premium_per_net_tree_saved": {str(n): outside_premium / n for n in [50,100,200,400]},
            "tree_count_qualification": "Counts are hypothetical net additional surviving trees across the whole corridor, after any outside tree losses, not a measured inventory or a prediction of survival.",
            "gdot_reported_operations_safety_bcr": 2.98,
        },
        "checks": {"paired_demand_matches": True, "all_compared_runs_complete": True, "movement_and_all_trip_aggregation_match": True},
    }
    (HERE / "results.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"comparisons": comparisons, "sensitivity_count": len(sensitivities), "checks": out["checks"]}, indent=2))


if __name__ == "__main__":
    main()
