"""Explore alternative balances and case-specific retiming after the fixed-plan study.

This extension is explicitly exploratory. Nominal alternative plans must first
pass the April 1 training screen. In changed-condition cases each road size is
allowed to retime on April 1 inputs before testing April 2. No observed delays
are available, so the second day is not field validation.
"""
import json
import statistics
from pathlib import Path
import engine
import run_study as study

HERE = Path(__file__).resolve().parent


def aggregate(runs):
    group = [x['result'] for x in runs]
    keys = [k for k,v in group[0].items() if type(v) in [int,float]]
    return dict(mean={k:statistics.mean(x[k] for x in group) for k in keys},
                all_complete=all(x['complete'] for x in group), peak_vc=group[0]['peak_vc'],
                main_seed_range=[min(x['main_delay_min'] for x in group),max(x['main_delay_min'] for x in group)])


def main():
    base = json.loads((HERE/'results.json').read_text())
    plans = {x['id']:x for x in base['candidate_plans']}
    eligible = [x for x in base['training_runs'] if x['total_lanes']==4 and x['result']['complete']
                and max(x['result']['peak_vc'].values())<=1 and x['result']['side_delay_min']<=1.5]
    jobs = [dict(stage='nominal_alternatives', period=x['period'], total_lanes=4,
                 profile=study.make_profile(x['period'],1,{}),plan=plans[x['plan_id']],seed=seed)
            for x in eligible for seed in study.DESIGN['holdout_seeds']]
    nominal_runs = study.run_batch(jobs,'Alternative plans')
    nominal = []
    for x in eligible:
        period, plan_id = x['period'], x['plan_id']
        a = aggregate([r for r in nominal_runs if r['period']==period and r['plan_id']==plan_id])
        b = next(r for r in base['summary'] if r['case']=='base' and r['period']==period and r['total_lanes']==6)
        main_gap = 60*(a['mean']['main_delay_min']-b['mean']['main_delay_min'])
        side_gap = 60*(a['mean']['side_delay_min']-b['mean']['side_delay_min'])
        absolute_ok = a['all_complete'] and a['mean']['main_delay_min']<=2 and a['mean']['side_delay_min']<=1.5 and max(a['peak_vc'].values())<=1 and b['mean']['main_exit_fraction']-a['mean']['main_exit_fraction']<=.02
        nominal.append(dict(period=period,plan=plans[plan_id],result=a,added_main_seconds=main_gap,added_side_seconds=side_gap,
                            screens=[dict(main_limit_seconds=m,side_limit_seconds=s,
                                          passes=absolute_ok and main_gap<=m and side_gap<=s)
                                     for m in [15,30,60] for s in [15,30,60]]))
    cases = [x for x in study.CASES if x['id'] in ['growth20','combined_stress','combined_stress_reduce10','combined_stress_reduce20','growth20_reduce20']]
    jobs, capacity_checks = [], []
    for case in cases:
        for period in study.DESIGN['periods']:
            profile = study.make_profile(period,0,case)
            for lanes in [2,3]:
                for plan in study.candidates(lanes):
                    vc = engine.peak_vc(profile,plan,case.get('sat',1800))
                    capacity_checks.append(dict(case=case['id'],period=period,total_lanes=2*lanes,plan_id=plan['id'],peak_vc=vc))
                    if max(vc.values())<=1:
                        jobs.append(dict(stage='retimed_training',case=case['id'],period=period,total_lanes=2*lanes,
                                         profile=profile,plan=plan,seed=0,sat=case.get('sat',1800),speed=case.get('speed',40)))
    training = study.run_batch(jobs,'Retiming training')
    choices, jobs = [], []
    for case in cases:
        for period in study.DESIGN['periods']:
            for lanes in [4,6]:
                group = [x for x in training if x['case']==case['id'] and x['period']==period and x['total_lanes']==lanes
                         and x['result']['complete'] and x['result']['side_delay_min']<=1.5]
                if not group:
                    choices.append(dict(case=case['id'],period=period,total_lanes=lanes,eligible_count=0,plan=None))
                    continue
                best = min(group,key=lambda x:(x['result']['all_delay_min'],x['plan_id']))
                plan = plans[best['plan_id']]
                choices.append(dict(case=case['id'],period=period,total_lanes=lanes,eligible_count=len(group),plan=plan))
                for seed in study.DESIGN['holdout_seeds']:
                    jobs.append(dict(stage='retimed_holdout',case=case['id'],period=period,total_lanes=lanes,
                                     profile=study.make_profile(period,1,case),plan=plan,seed=seed,
                                     sat=case.get('sat',1800),speed=case.get('speed',40)))
    holdout = study.run_batch(jobs,'Retimed holdout')
    summary = []
    for choice in choices:
        group = [x for x in holdout if x['case']==choice['case'] and x['period']==choice['period'] and x['total_lanes']==choice['total_lanes']]
        summary.append(choice | {'result':aggregate(group) if group else None})
    result = dict(exploratory=True,description=__doc__,additional_simulations=len(nominal_runs)+len(training)+len(holdout),
                  nominal_alternatives=nominal,retimed_summary=summary,capacity_checks=capacity_checks,
                  nominal_runs=nominal_runs,training_runs=training,holdout_runs=holdout)
    (HERE/'tradeoffs.json').write_text(json.dumps(result,indent=2)+'\n')
    for period in ['AM','PM']:
        print('Nominal feasible balances',period,flush=True)
        for x in nominal:
            if x['period']==period and any(s['passes'] and s['main_limit_seconds']==30 and s['side_limit_seconds']==30 for s in x['screens']):
                print(x['plan']['id'],'main gap',round(x['added_main_seconds'],2),'side gap',round(x['added_side_seconds'],2),flush=True)
    for x in summary:
        print(x['case'],x['period'],x['total_lanes'],x['plan']['id'] if x['plan'] else 'NO QUALIFYING GRID PLAN',
              {k:round(v,3) for k,v in x['result']['mean'].items() if k in ['main_delay_min','side_delay_min','all_delay_min']} if x['result'] else '',flush=True)
    print('Additional simulations',result['additional_simulations'],flush=True)


if __name__=='__main__':
    main()
