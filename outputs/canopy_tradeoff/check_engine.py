"""Regression, symmetry, conservation and sustained-capacity checks."""
import importlib.util
import json
from pathlib import Path
import engine

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('legacy', HERE.parent/'simulation'/'simulate.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
m.LENGTHS = [x['length_m'] for x in json.loads((HERE.parent/'validation'/'network.json').read_text())['links']]

# The extension must reproduce prior one-hour behavior before new experiments.
for sc in m.SCENARIOS:
    profile = dict(eb=[[v*.4*(1-sc['reduction']) for v in m.VOLUMES['2027 PM']]],
                   wb=[[v*.6*(1-sc['reduction']) for v in m.VOLUMES['2027 PM']]], side=[450])
    plan = dict(lanes=sc['lanes'], cycle=120, green=sc['green'],
                offsets=engine.offsets(m.LENGTHS, 'west', 120) if sc['coordinated'] else [0,35,80,15,65,100,45])
    new = engine.simulate(profile, plan, m.LENGTHS)
    old = m.simulate(sc, '2027 PM')
    for key in ['main_delay_min','side_delay_min','all_delay_min','main_time_min','main_generated']:
        assert abs(new[key]-old[key]) < 1e-7, (sc['name'], key, new[key], old[key])

lengths = [300, 400, 500, 600, 700, 800]
plan = dict(lanes=2, cycle=120, green=72, offsets=engine.offsets(lengths, 'west', 120))
p = dict(eb=[[500]*6, [800]*6], wb=[[900]*6, [1100]*6], side=[300, 400])
a = engine.simulate(p, plan, lengths, seed=7)
reversed_lengths = list(reversed(lengths))
mirror = dict(eb=[list(reversed(x)) for x in p['wb']], wb=[list(reversed(x)) for x in p['eb']], side=p['side'])
b = engine.simulate(mirror, dict(plan, offsets=list(reversed(plan['offsets']))), reversed_lengths, seed=7)
assert abs(a['main_delay_min']-b['main_delay_min']) < 1e-8
assert abs(a['eb_delay_min']-b['wb_delay_min']) < 1e-8
zero = dict(eb=[[0]*6], wb=[[0]*6], side=[0])
z = engine.simulate(zero, plan, lengths)
assert z['main_generated'] == z['main_delay_min'] == z['residual_at_end'] == 0

# In one direction a two-lane, 50%-green approach serves 1800/h at sat=1800.
# At 2400/h sustained for 3 hours the remaining count cannot disappear.
high = dict(eb=[[2400]*6]*3, wb=[[0]*6]*3, side=[0]*3)
hot = engine.simulate(high, dict(plan, green=60, offsets=[0]*7), lengths)
assert hot['main_remaining_at_pulse_end'] >= 1800-1e-4
assert hot['complete'] and hot['drain_minutes'] > 30
assert engine.peak_vc(high, dict(plan, green=60), 1800)['main'] > 1
print('PASS: seven legacy scenario regressions, mirrored-direction symmetry, zero demand, sustained overload, conservation and finite storage.')
