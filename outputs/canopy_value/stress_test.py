"""Stress-test signal timing and the four-lane counterfactual.

This is a screening experiment, not a calibrated traffic model. It searches the
same coarse 33-plan grid used in the traffic study, then checks selected plans
on five stochastic arrival seeds. The test varies side-street demand, main-road
demand, saturation flow, and lost time available to phases. It deliberately
keeps the candidate objective and caveats visible rather than presenting one
hand-picked timing plan as a field recommendation.
"""
from concurrent.futures import ProcessPoolExecutor
import json
import os
import statistics
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
TRAFFIC = HERE.parent / "canopy_tradeoff"
sys.path.insert(0, str(TRAFFIC))
import engine  # noqa: E402
import run_study as study  # noqa: E402

NETWORK = json.loads((HERE.parent / "validation" / "network.json").read_text())
LENGTHS = [x["length_m"] for x in NETWORK["links"]]
DESIGN = json.loads((TRAFFIC / "design.json").read_text())
SEEDS = [10, 11, 12, 13, 14]
SIDE_LEVELS = [50, 100, 300, 450, 650]
MAIN_FACTORS = [1.0, 1.2]
SATURATIONS = [1600, 1800]
LOST_TIMES = [16, 24]


def make_plan(lanes, base, lost):
    plan = dict(base)
    if lost != plan["lost"]:
        plan["lost"] = lost
        plan["green"] = min(plan["green"], plan["cycle"] - lost - DESIGN["minimum_side_green_seconds"])
        plan["id"] = plan["id"] + f"_L{lost}"
        plan["offsets"] = engine.offsets(LENGTHS, plan["pattern"], plan["cycle"], DESIGN["progression_speed_mph"])
    return plan


def candidates(lanes, lost):
    out = []
    for base in study.candidates(lanes):
        out.append(make_plan(lanes, base, lost))
    return out


def profile(period, main_factor, side):
    p = study.make_profile(period, 1, {"main_factor": main_factor, "side": side})
    return p


def run(job):
    result = engine.simulate(job["profile"], job["plan"], LENGTHS, job["seed"], job["sat"], job["speed"])
    return {k: v for k, v in job.items() if k not in ("profile", "plan")} | {"plan_id": job["plan"]["id"], "plan": job["plan"], "result": result}


def complete_result(x):
    return x["result"]["complete"] and abs(x["result"]["residual_at_end"]) < 1e-4


def training_key(x):
    # Favor total delay, then main delay, then stable plan ID.
    return (x["result"]["all_delay_min"], x["result"]["main_delay_min"], x["plan_id"])


def select_training(group):
    eligible = [x for x in group if complete_result(x) and max(x["result"]["peak_vc"].values()) <= 1 and x["result"]["side_delay_min"] <= 1.5]
    return min(eligible or group, key=training_key), len(eligible)


def aggregate(group):
    rows = [x["result"] for x in group]
    mean = {k: statistics.mean(x[k] for x in rows) for k, v in rows[0].items() if isinstance(v, (int, float))}
    return {"mean": mean, "seed_range_main_delay": [min(x["main_delay_min"] for x in rows), max(x["main_delay_min"] for x in rows)], "all_complete": all(complete_result(x) for x in group), "peak_vc": rows[0]["peak_vc"]}


def jobs_for_training():
    jobs = []
    for side in SIDE_LEVELS:
        for factor in MAIN_FACTORS:
            for sat in SATURATIONS:
                for lost in LOST_TIMES:
                    for period in DESIGN["periods"]:
                        p = profile(period, factor, side)
                        for lanes in (2, 3):
                            for plan in candidates(lanes, lost):
                                jobs.append(dict(stage="training", side=side, main_factor=factor, sat=sat, lost=lost, period=period, total_lanes=2*lanes, seed=0, speed=40, profile=p, plan=plan))
    return jobs


def main():
    train_jobs = jobs_for_training()
    print(f"training runs: {len(train_jobs)}", flush=True)
    with ProcessPoolExecutor(max_workers=min(4, os.cpu_count() or 1)) as pool:
        training = list(pool.map(run, train_jobs, chunksize=16))
    selections = []
    holdout_jobs = []
    for side in SIDE_LEVELS:
        for factor in MAIN_FACTORS:
            for sat in SATURATIONS:
                for lost in LOST_TIMES:
                    for period in DESIGN["periods"]:
                        key = lambda x: x["side"] == side and x["main_factor"] == factor and x["sat"] == sat and x["lost"] == lost and x["period"] == period
                        choices = {}
                        for lanes in (4, 6):
                            chosen, eligible = select_training([x for x in training if key(x) and x["total_lanes"] == lanes])
                            choices[lanes] = chosen
                            for seed in SEEDS:
                                holdout_jobs.append(dict(stage="holdout", side=side, main_factor=factor, sat=sat, lost=lost, period=period, total_lanes=lanes, seed=seed, speed=40, profile=profile(period, factor, side), plan=chosen["plan"]))
                        selections.append(dict(side_demand_per_junction=side, main_factor=factor, saturation=sat, lost_seconds=lost, period=period, four_lane_plan=choices[4]["plan"], six_lane_plan=choices[6]["plan"], four_training_eligible=sum(1 for x in training if key(x) and x["total_lanes"] == 4 and complete_result(x) and max(x["result"]["peak_vc"].values()) <= 1 and x["result"]["side_delay_min"] <= 1.5), six_training_eligible=sum(1 for x in training if key(x) and x["total_lanes"] == 6 and complete_result(x) and max(x["result"]["peak_vc"].values()) <= 1 and x["result"]["side_delay_min"] <= 1.5)))
    print(f"holdout runs: {len(holdout_jobs)}", flush=True)
    with ProcessPoolExecutor(max_workers=min(4, os.cpu_count() or 1)) as pool:
        holdout = list(pool.map(run, holdout_jobs, chunksize=8))
    rows = []
    for s in selections:
        key = lambda x: x["side"] == s["side_demand_per_junction"] and x["main_factor"] == s["main_factor"] and x["sat"] == s["saturation"] and x["lost"] == s["lost_seconds"] and x["period"] == s["period"]
        four = aggregate([x for x in holdout if key(x) and x["total_lanes"] == 4])
        six = aggregate([x for x in holdout if key(x) and x["total_lanes"] == 6])
        fm, sm = four["mean"], six["mean"]
        added_main = 60 * (fm["main_delay_min"] - sm["main_delay_min"])
        added_side = 60 * (fm["side_delay_min"] - sm["side_delay_min"])
        rows.append(s | {"four": four, "six": six, "added_main_seconds": added_main, "added_side_seconds": added_side, "passes_strict_comparison": four["all_complete"] and max(four["peak_vc"].values()) <= 1 and fm["main_delay_min"] <= 2 and fm["side_delay_min"] <= 1.5 and added_main <= 30 and added_side <= 15 and sm["main_exit_fraction"] - fm["main_exit_fraction"] <= .02})
    out = {
        "description": __doc__,
        "scope": "Retimed coarse-grid screening with observed April 2025 directional profiles and synthetic side demand. Not field validation or microsimulation.",
        "grid": {"side_demand_per_junction": SIDE_LEVELS, "main_factor": MAIN_FACTORS, "saturation": SATURATIONS, "lost_seconds": LOST_TIMES, "periods": list(DESIGN["periods"])},
        "training_runs": len(training), "holdout_runs": len(holdout), "cases": rows,
        "gdot_context": {"2027_no_build_dhv_total_vph": {"AM": [4060,3880,3815,3795,3630,2790], "PM": [2985,2765,2680,3095,2975,2425]}, "source_pages": "GDOT concept report PDF pp. 129-131 (printed pages 128-130)", "note": "These are GDOT total directional-hour design figures for the project corridor, included as context; the stress grid uses the observed 2025 station profile, not these aggregate forecast values."},
        "summary": {
            "strict_pass_count": sum(1 for x in rows if x["passes_strict_comparison"]),
            "case_count": len(rows),
            "four_lane_no_qualifying_training_plan": sum(1 for x in rows if x["four_training_eligible"] == 0),
            "four_lane_still_passes_at_side_450_factor_1_sat_1800_lost_16": [x for x in rows if x["side_demand_per_junction"] == 450 and x["main_factor"] == 1.0 and x["saturation"] == 1800 and x["lost_seconds"] == 16],
        },
    }
    (HERE / "stress_test.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    # Compact terminal summary for review.
    for side in SIDE_LEVELS:
        base = [x for x in rows if x["side_demand_per_junction"] == side and x["main_factor"] == 1 and x["saturation"] == 1800 and x["lost_seconds"] == 16]
        print("base side", side, [(x["period"], round(x["added_main_seconds"], 1), round(x["added_side_seconds"], 1), x["passes_strict_comparison"]) for x in base], flush=True)
    print(json.dumps(out["summary"], indent=2), flush=True)


if __name__ == "__main__":
    main()
