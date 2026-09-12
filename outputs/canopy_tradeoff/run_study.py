"""Reproduce the traffic-only study: Python 3, standard library, no network.

Four worker processes evaluate independent runs. Run check_engine.py first.
"""
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import statistics
import engine

HERE = Path(__file__).resolve().parent
DESIGN = json.loads((HERE/'design.json').read_text())
COUNTS = json.loads((HERE.parent/'validation'/'counts.json').read_text())
NETWORK = json.loads((HERE.parent/'validation'/'network.json').read_text())
LENGTHS = [x['length_m'] for x in NETWORK['links']]
FORECASTS = json.loads((HERE.parent/'simulation'/'results.json').read_text())['volumes']

CASES = [
    dict(id='base'),
    dict(id='growth10', main_factor=1.10, side_factor=1.10),
    dict(id='growth20', main_factor=1.20, side_factor=1.20),
    dict(id='growth30', main_factor=1.30, side_factor=1.30),
    dict(id='lower_saturation', sat=1600),
    dict(id='higher_side_demand', side=650),
    dict(id='combined_stress', sat=1600, side=650),
    dict(id='slower_travel', speed=35),
    dict(id='unobserved_links_plus15', shape_factor=1.15),
    dict(id='combined_stress_reduce10', sat=1600, side=650, main_factor=.90),
    dict(id='combined_stress_reduce20', sat=1600, side=650, main_factor=.80),
    dict(id='growth20_reduce10', main_factor=1.20*.90, side_factor=1.20),
    dict(id='growth20_reduce20', main_factor=1.20*.80, side_factor=1.20),
]


def make_profile(period, day, case):
    ratios = [v/FORECASTS['2027 '+period][1] for v in FORECASTS['2027 '+period]]
    ratios = [v*(case.get('shape_factor', 1) if j != 1 else 1) for j,v in enumerate(ratios)]
    hourly = {'eb': [], 'wb': [], 'side': []}
    for h in DESIGN['periods'][period]:
        for key, prefix in [('eb', 'Eastbound'), ('wb', 'Westbound')]:
            observed = sum(COUNTS['lanes'][prefix+' '+lane][h][day] for lane in ['Slow', 'Fast'])
            hourly[key].append([observed*v*case.get('main_factor', 1) for v in ratios])
        hourly['side'].append(case.get('side', 450)*case.get('side_factor', 1))
    return hourly


def candidates(lanes):
    plans = []
    for cycle in DESIGN['cycles_seconds']:
        for fraction in DESIGN['main_green_fractions']:
            green = round(cycle*fraction)
            if cycle-green-DESIGN['lost_seconds'] < DESIGN['minimum_side_green_seconds']:
                continue
            for pattern in DESIGN['offset_patterns']:
                plans.append(dict(id=f'{lanes*2}L_C{cycle}_G{green}_{pattern}', lanes=lanes,
                                  cycle=cycle, green=green, lost=DESIGN['lost_seconds'], pattern=pattern,
                                  offsets=engine.offsets(LENGTHS, pattern, cycle, DESIGN['progression_speed_mph'])))
    return plans


def run_job(job):
    profile, plan = job['profile'], job['plan']
    result = engine.simulate(profile, plan, LENGTHS, job['seed'],
                             job.get('sat', 1800), job.get('speed', 40))
    return {k:v for k,v in job.items() if k not in ['profile', 'plan']} | {'plan_id':plan['id'], 'result':result}


def run_batch(jobs, stage):
    outputs = []
    with ProcessPoolExecutor(max_workers=min(4, os.cpu_count() or 1)) as pool:
        for i, result in enumerate(pool.map(run_job, jobs), 1):
            outputs.append(result)
            if i % 24 == 0 or i == len(jobs):
                print(stage, i, '/', len(jobs), flush=True)
    return outputs


def capacity_envelope():
    criticals = {}
    for period in DESIGN['periods']:
        values = []
        for day in [0, 1]:
            profile = make_profile(period, day, {})
            for direction in ['eb', 'wb']:
                for i, volumes in enumerate(profile[direction]):
                    for j, q in enumerate(volumes):
                        values.append(dict(flow=q, day=COUNTS['dates'][day], hour=DESIGN['periods'][period][i],
                                           direction=direction, link=j, link_from=NETWORK['links'][j]['from'],
                                           link_to=NETWORK['links'][j]['to']))
        criticals[period] = max(values, key=lambda x:x['flow'])
    rows = []
    for period, critical in criticals.items():
        q = critical['flow']
        for lanes in [2, 3]:
            for cycle in DESIGN['cycles_seconds']:
                for sat in [1600, 1800, 2000]:
                    for side in [450, 650]:
                        for target in [1., .9]:
                            available = target*(1-DESIGN['lost_seconds']/cycle)
                            main_y, side_y = q/(lanes*sat), side/(2*sat)
                            rows.append(dict(period=period, lanes=lanes, cycle=cycle, saturation=sat,
                                             side=side, target_vc=target,
                                             max_common_demand_multiplier=available/(main_y+side_y),
                                             max_main_only_multiplier=max(0, (available-side_y)/main_y)))
    return dict(critical_flows=criticals, rows=rows)


def main():
    plans = {p['id']:p for lanes in [2,3] for p in candidates(lanes)}
    jobs = [dict(stage='training', period=period, total_lanes=lanes*2, seed=0,
                 profile=make_profile(period, 0, {}), plan=plan)
            for period in DESIGN['periods'] for lanes in [2,3] for plan in candidates(lanes)]
    training = run_batch(jobs, 'Training')
    selected = []
    for period in DESIGN['periods']:
        for total_lanes in [4,6]:
            group = [x for x in training if x['period']==period and x['total_lanes']==total_lanes]
            eligible = [x for x in group if x['result']['complete']
                        and x['result']['side_delay_min'] <= 1.5
                        and max(x['result']['peak_vc'].values()) <= 1]
            best = min(eligible or group, key=lambda x:(x['result']['all_delay_min'],x['plan_id']))
            selected.append(dict(period=period, total_lanes=total_lanes, plan=plans[best['plan_id']],
                                 training_eligible=bool(eligible), eligible_count=len(eligible),
                                 candidate_count=len(group), training_result=best['result']))
            print('Selected', period, total_lanes, best['plan_id'], 'eligible',len(eligible), flush=True)
    profiles = {}
    jobs = []
    for case in CASES:
        for period in DESIGN['periods']:
            profile = make_profile(period, 1, case)
            profiles[case['id']+'_'+period] = profile
            for choice in selected:
                if choice['period'] != period:
                    continue
                for seed in DESIGN['holdout_seeds']:
                    jobs.append(dict(stage='holdout', case=case['id'], period=period,
                                     total_lanes=choice['total_lanes'], seed=seed, profile=profile,
                                     plan=choice['plan'], sat=case.get('sat',1800), speed=case.get('speed',40)))
    holdout = run_batch(jobs, 'Holdout')
    summary = []
    for case in CASES:
        for period in DESIGN['periods']:
            for lanes in [4,6]:
                group = [x['result'] for x in holdout if x['case']==case['id']
                         and x['period']==period and x['total_lanes']==lanes]
                numeric = [k for k,v in group[0].items() if type(v) in [int,float]]
                summary.append(dict(case=case['id'], period=period, total_lanes=lanes,
                                    mean={k:statistics.mean(x[k] for x in group) for k in numeric},
                                    peak_vc=group[0]['peak_vc'], all_complete=all(x['complete'] for x in group),
                                    seed_range_main_delay=[min(x['main_delay_min'] for x in group),max(x['main_delay_min'] for x in group)]))
    comparisons = []
    screen = DESIGN['comparison_screen']
    for case in CASES:
        for period in DESIGN['periods']:
            a = next(x for x in summary if x['case']==case['id'] and x['period']==period and x['total_lanes']==4)
            b = next(x for x in summary if x['case']==case['id'] and x['period']==period and x['total_lanes']==6)
            assert abs(a['mean']['main_generated']-b['mean']['main_generated']) < 1e-5
            added_main = 60*(a['mean']['main_delay_min']-b['mean']['main_delay_min'])
            added_side = 60*(a['mean']['side_delay_min']-b['mean']['side_delay_min'])
            checks = dict(main_absolute=a['mean']['main_delay_min']*60 <= screen['maximum_four_lane_main_delay_seconds'],
                          side_absolute=a['mean']['side_delay_min']*60 <= screen['maximum_four_lane_side_delay_seconds'],
                          added_side=added_side <= screen['maximum_added_side_delay_seconds'],
                          exit_fraction=b['mean']['main_exit_fraction']-a['mean']['main_exit_fraction'] <= screen['maximum_exit_fraction_loss'],
                          hourly_capacity=max(a['peak_vc'].values()) <= screen['maximum_peak_hourly_volume_capacity_ratio'],
                          full_drainage=a['all_complete'] and b['all_complete'])
            passes = {str(limit):all(checks.values()) and added_main <= limit
                      for limit in screen['alternate_added_main_delay_limits_seconds']}
            comparisons.append(dict(case=case['id'],period=period,added_main_seconds=added_main,
                                    added_side_seconds=added_side, checks=checks, passes_by_main_limit=passes,
                                    all_delay_change_seconds=60*(a['mean']['all_delay_min']-b['mean']['all_delay_min'])))
    files = [HERE/'design.json', HERE/'engine.py', HERE/'run_study.py',
             HERE.parent/'validation'/'counts.json', HERE.parent/'validation'/'network.json']
    result = dict(study=DESIGN['study'],run_count=len(training)+len(holdout),
                  source_sha256_lf={str(p.relative_to(HERE.parent)):hashlib.sha256(p.read_text().encode()).hexdigest() for p in files},
                  design=DESIGN, cases=CASES, candidate_plans=list(plans.values()), selected=selected,
                  holdout_inputs=profiles, summary=summary, comparisons=comparisons,
                  capacity_envelope=capacity_envelope(), training_runs=training, holdout_runs=holdout)
    (HERE/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    for row in comparisons:
        print(row['case'],row['period'],round(row['added_main_seconds'],1),
              'added main seconds; pass30:',row['passes_by_main_limit']['30'], flush=True)
    print('Saved',result['run_count'],'runs',flush=True)


if __name__ == '__main__':
    main()
