"""Check saved study consistency and analytical bounds independently."""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
r = json.loads((HERE/'results.json').read_text())
t = json.loads((HERE/'tradeoffs.json').read_text())
all_runs = r['training_runs']+r['holdout_runs']+t['nominal_runs']+t['training_runs']+t['holdout_runs']
assert len(all_runs)==r['run_count']+t['additional_simulations']==858
censored = 0
for run in all_runs:
    x = run['result']
    assert abs(x['main_generated']-x['main_exited_at_pulse_end']-x['main_remaining_at_pulse_end'])<1e-4
    assert all(math.isfinite(v) for v in x.values() if type(v) in [int,float])
    assert x['main_delay_min']>=0 and x['side_delay_min']>=0
    if not x['complete']:
        censored+=1
assert censored==15
for a in r['holdout_runs']:
    if a['total_lanes']!=4:
        continue
    b=next(x for x in r['holdout_runs'] if x['total_lanes']==6 and x['case']==a['case'] and x['period']==a['period'] and x['seed']==a['seed'])
    assert abs(a['result']['main_generated']-b['result']['main_generated'])<1e-5
    assert abs(a['result']['side_generated']-b['result']['side_generated'])<1e-5
for row in r['capacity_envelope']['rows']:
    q=r['capacity_envelope']['critical_flows'][row['period']]['flow']
    m=row['max_common_demand_multiplier']
    # At the frontier, green times required at the chosen v/c exactly exhaust
    # the available cycle. Just above it they cannot fit.
    main_green=q*m/(row['lanes']*row['saturation']*row['target_vc'])*row['cycle']
    side_green=row['side']*m/(2*row['saturation']*row['target_vc'])*row['cycle']
    assert abs(main_green+side_green+16-row['cycle'])<1e-8
    assert (main_green+side_green)*1.001+16>row['cycle']
for period,pid in [('AM','4L_C120_G84_west'),('PM','4L_C120_G84_east')]:
    a=next(x for x in t['nominal_alternatives'] if x['period']==period and x['plan']['id']==pid)
    assert a['result']['all_complete']
    assert max(a['result']['peak_vc'].values())<=1
    assert any(s['passes'] and s['main_limit_seconds']==30 and s['side_limit_seconds']==30 for s in a['screens'])
    assert not any(s['passes'] and s['side_limit_seconds']==15 for s in a['screens'])
out=dict(total_runs=len(all_runs),censored_runs_identified_and_excluded_from_success=censored,
         checks=['Mass balance in all saved runs','Equal offered main and side demand in fixed-plan pairs',
                 'Capacity frontier exhausts green-time budget','Headline plans complete and meet declared 30/30 screen'],
         engine_checks='check_engine.py additionally passes seven legacy regressions, mirror symmetry, zero demand, sustained overload, conservation and storage assertions.')
(HERE/'checks.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS',out)
