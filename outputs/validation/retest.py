"""Reproduce the September 2026 audit without altering the archived V2 study.

Python standard library only. This is a one-station sensitivity test, not a
calibrated traffic forecast. Run rebuild_network.py in this folder first.
"""
import csv
import hashlib
import importlib.util
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODEL = HERE.parent / 'simulation'
spec = importlib.util.spec_from_file_location('queue_model', MODEL / 'simulate.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
counts = json.loads((HERE / 'counts.json').read_text())
network = json.loads((HERE / 'network.json').read_text())
old_lengths = list(m.LENGTHS)
new_lengths = [link['length_m'] for link in network['links']]

def volume(hour, days=(0, 1)):
    return statistics.mean(counts['all_lanes'][hour][d] for d in days)

def share(hour, days=(0, 1)):
    west = sum(counts['lanes'][lane][hour][d]
               for lane in ('Westbound Slow', 'Westbound Fast') for d in days)
    total = sum(counts['all_lanes'][hour][d] for d in days)
    return west / total

# Independent cross-checks of transcribed totals and lane aggregation.
for d, expected in enumerate(counts['daily_all_lane_totals']):
    assert sum(row[d] for row in counts['all_lanes']) == expected
    for h in range(24):
        assert sum(lane[h][d] for lane in counts['lanes'].values()) == counts['all_lanes'][h][d]
    assert max(range(12, 24), key=lambda h: counts['all_lanes'][h][d]) == 15

# Each tuple: id, station-volume anchor, westbound share, sat, side, geometry.
# Reported data only replace a single station anchor and a directional ratio.
# All six link volumes retain the old forecast's relative spatial pattern.
profiles = [
    ('v2_forecast_original_geometry', 2765, .60, 1800, 450, 'v2'),
    ('forecast_corrected_geometry', 2765, .60, 1800, 450, 'corrected'),
    ('apr_peak_volume_only', volume(15), .60, 1800, 450, 'corrected'),
    ('apr_peak_volume_and_direction', volume(15), share(15), 1800, 450, 'corrected'),
    ('apr_1_peak_volume_and_direction', volume(15, (0,)), share(15, (0,)), 1800, 450, 'corrected'),
    ('apr_2_peak_volume_and_direction', volume(15, (1,)), share(15, (1,)), 1800, 450, 'corrected'),
    ('apr_17h_volume_and_direction', volume(17), share(17), 1800, 450, 'corrected'),
    ('apr_peak_lower_saturation', volume(15), share(15), 1600, 450, 'corrected'),
    ('apr_peak_higher_side_demand', volume(15), share(15), 1800, 650, 'corrected'),
]
metrics = ['main_delay_min', 'side_delay_min', 'all_delay_min',
           'main_generated', 'main_exited_at_60min', 'main_remaining_at_60min',
           'cleared_by_min', 'residual_at_end']
runs, summary, profile_data = [], [], []
for profile, anchor, west_share, sat, side, geometry in profiles:
    m.LENGTHS = old_lengths if geometry == 'v2' else new_lengths
    factor = anchor / m.VOLUMES['2027 PM'][1]
    m.VOLUMES[profile] = [v * factor for v in m.VOLUMES['2027 PM']]
    assert abs(m.VOLUMES[profile][1] - anchor) < 1e-8
    profile_data.append(dict(id=profile, station_anchor=anchor, factor=factor,
                             share_westbound=west_share, saturation=sat,
                             side_rate=side, geometry=geometry,
                             segment_volumes=m.VOLUMES[profile]))
    for scenario in m.SCENARIOS:
        group = []
        for seed in range(5):
            run = m.simulate(scenario, profile, seed, west_share, sat, side)
            run.pop('queue_series', None)
            assert abs(run['main_exited_at_60min'] + run['main_remaining_at_60min'] - run['main_generated']) < 1e-5
            assert run['residual_at_end'] < 1e-5, 'Delay would be censored by incomplete drainage'
            run['profile'] = profile
            runs.append(run)
            group.append(run)
        summary.append(dict(profile=profile, scenario=scenario['name'],
                            mean={k: statistics.mean(x[k] for x in group) for k in metrics},
                            seed_min_main_delay=min(x['main_delay_min'] for x in group),
                            seed_max_main_delay=max(x['main_delay_min'] for x in group)))
    print('Completed', profile, flush=True)

# Ensure the control reproduces the published V2 PM runs exactly.
archived = json.loads((MODEL / 'results.json').read_text())['runs']
for run in runs:
    if run['profile'] != 'v2_forecast_original_geometry':
        continue
    prior = next(x for x in archived if x['period'] == '2027 PM'
                 and x['scenario'] == run['scenario'] and x['seed'] == run['seed'])
    for key in metrics:
        assert abs(run[key] - prior[key]) < 1e-7, (key, run[key], prior[key])

files = [HERE / 'counts.json', HERE / 'network.json', HERE / 'retest.py',
         MODEL / 'simulate.py', MODEL / 'network.json', MODEL / 'results.json']
result = dict(
    audit_date='2026-09-11', run_count=len(runs), seeds=list(range(5)),
    interpretation='One-station-anchored sensitivity analysis, not field calibration. Reported units provisionally treated as vehicles; see counts.json.',
    source_sha256={str(p.relative_to(HERE.parent)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
    profiles=profile_data, summary=summary, runs=runs,
    checks='48 hourly all-lane sums and two daily totals matched. V2 PM control reproduced. All runs passed conservation, finite storage, and complete-drain checks.')
(HERE / 'retest_results.json').write_text(json.dumps(result, indent=2) + '\n')
with (HERE / 'retest_summary.csv').open('w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['profile', 'scenario'] + metrics)
    writer.writeheader()
    writer.writerows(dict(profile=x['profile'], scenario=x['scenario'], **x['mean']) for x in summary)
print(result['checks'], flush=True)
for x in summary:
    if x['scenario'] in (m.SCENARIOS[2]['name'], m.SCENARIOS[5]['name'], m.SCENARIOS[6]['name']):
        print(x['profile'], x['scenario'], round(x['mean']['main_delay_min'], 4))
