"""Behavioral checks, independent from the report's preferred result."""
import simulate as m

# Zero demand must yield no vehicles or delay.
m.VOLUMES['test_zero']=[0]*6
x=m.simulate(m.SCENARIOS[0],period='test_zero',side_rate=0)
assert x['main_generated']==0 and x['main_delay_min']==0 and x['residual_at_end']==0

# Low demand with uninterrupted main green should not acquire signal queues.
m.VOLUMES['test_light']=[100]*6
s=dict(m.SCENARIOS[0],green=120)
x=m.simulate(s,period='test_light',side_rate=0)
assert x['main_delay_min']<.01 and x['residual_at_end']<1e-6

# Demand intervention must reduce offered demand, not delete queued vehicles.
a=m.simulate(m.SCENARIOS[2]);b=m.simulate(m.SCENARIOS[4])
assert abs(b['main_generated']/a['main_generated']-.8)<1e-8

# Trees are not a traffic parameter. Same six-lane operations must give equal
# results for inside/outside alignment labels, without asserting feasibility.
a=m.simulate(m.SCENARIOS[5]);b=m.simulate(dict(m.SCENARIOS[5],name='Outside widening'))
for key in ['main_delay_min','main_exited_at_60min','max_main_queue_vehicles']:
 assert a[key]==b[key]

# Conservation and storage assertions execute inside every simulation run.
print('Passed: zero demand, continuous green, demand scaling, alignment equivalence, flow conservation, finite storage.')
