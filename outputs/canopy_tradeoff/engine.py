"""Multi-hour extension of the archived aggregate finite-storage queue model.

This is not microsimulation. Sources/turnover are inferred from link totals;
cross-street queues do not feed back onto main-road links. Reported counts
are provisionally interpreted as vehicles. See design.json and README.md.
"""
import math
import random


def offsets(lengths, pattern, cycle, speed=40):
    travel = [max(1, round(x / (speed * .44704))) for x in lengths]
    if pattern == 'west':
        return [sum(travel[i:]) % cycle for i in range(7)]
    if pattern == 'east':
        return [sum(travel[:i]) % cycle for i in range(7)]
    if pattern == 'simultaneous':
        return [0] * 7
    raise ValueError(pattern)


def peak_vc(profile, plan, sat):
    main_capacity = plan['lanes'] * sat * plan['green'] / plan['cycle']
    side_green = plan['cycle'] - plan['green'] - plan.get('lost', 16)
    side_capacity = 2 * sat * side_green / plan['cycle']
    main = max(max(x) for x in profile['eb'] + profile['wb'])
    side = max(profile['side'])
    return {'main': main / main_capacity if main_capacity else math.inf,
            'side': side / side_capacity if side_capacity else (math.inf if side else 0)}


def simulate(profile, plan, lengths, seed=0, sat=1800, speed=40, keep_series=False):
    hours = len(profile['eb'])
    assert hours and len(profile['wb']) == len(profile['side']) == hours
    assert all(len(x) == 6 for x in profile['eb'] + profile['wb'])
    assert all(v >= 0 for x in profile['eb'] + profile['wb'] for v in x)
    assert all(x >= 0 for x in profile['side'])
    assert len(lengths) == 6 and min(lengths) > 0
    cycle, green = plan['cycle'], plan['green']
    lost = plan.get('lost', 16)
    assert 0 <= green <= cycle and cycle > 0 and sat > 0 and speed > 0
    assert cycle - green - lost >= 0 or max(profile['side']) == 0
    pulse = hours * 3600
    rng = random.Random(seed)
    factors = []
    for h in range(hours):
        values = [rng.lognormvariate(-.005, .1) for _ in range(60)]
        mean = sum(values) / 60
        factors.extend(v / mean for v in values)
    travel = [max(1, round(x / (speed * .44704))) for x in lengths]
    phase_offsets = plan['offsets']
    dirs = []
    for reverse, hourly in ((False, profile['eb']), (True, profile['wb'])):
        entries, continuations = [], []
        for seq in hourly:
            seq = list(reversed(seq)) if reverse else list(seq)
            prev, nxt = [0] + seq, seq + [0]
            totals = [max(a, b) for a, b in zip(prev, nxt)]
            entries.append([max(0, b-a) / 3600 for a, b in zip(prev, nxt)])
            continuations.append([b/q if q else 0 for b, q in zip(nxt, totals)])
        spacing = list(reversed(lengths)) if reverse else lengths
        dirs.append(dict(ready=[0.]*7, moving=[0.]*7, source=[0.]*7,
                         storage=[1e9] + [x * plan['lanes'] / 7.5 for x in spacing],
                         entries=entries, continuations=continuations,
                         travel=list(reversed(travel)) if reverse else travel,
                         offsets=list(reversed(phase_offsets)) if reverse else phase_offsets,
                         events={}, generated=0., exited=0., delay=0., systemtime=0.))
    side = [0.]*7
    side_generated = side_exited = side_delay = 0.
    peak_main = peak_side = 0.
    pulse_exited = pulse_remaining = 0.
    series = []
    for t in range(pulse + 7200):
        h = min(t // 3600, hours-1)
        factor = factors[t//60] if t < pulse else 0
        for d in dirs:
            for j, a in d['events'].pop(t, []):
                d['moving'][j] -= a
                d['ready'][j] += a
            for j in range(7):
                a = d['entries'][h][j] * factor
                d['source'][j] += a
                d['generated'] += a
                room = max(0, d['storage'][j] - d['ready'][j] - d['moving'][j])
                a = min(d['source'][j], room)
                d['source'][j] -= a
                d['ready'][j] += a
            flows = []
            for j in range(7):
                cap = sat * plan['lanes'] / 3600 if (t-d['offsets'][j]) % cycle < green else 0
                f = min(d['ready'][j], cap)
                p = d['continuations'][h][j]
                if j < 6 and p > 0:
                    room = max(0, d['storage'][j+1] - d['ready'][j+1] - d['moving'][j+1])
                    f = min(f, room/p)
                flows.append(f)
            for j, f in enumerate(flows):
                p = d['continuations'][h][j]
                d['ready'][j] -= f
                d['exited'] += f*(1-p)
                if j < 6 and f*p > 0:
                    a = f*p
                    d['moving'][j+1] += a
                    d['events'].setdefault(t+d['travel'][j], []).append((j+1, a))
                assert d['ready'][j] >= -1e-7
                assert d['ready'][j]+d['moving'][j] <= d['storage'][j]+1e-6
            d['delay'] += sum(d['ready']) + sum(d['source'])
            d['systemtime'] += sum(d['ready']) + sum(d['source']) + sum(d['moving'])
        for j in range(7):
            a = profile['side'][h] / 3600 * factor
            side[j] += a
            side_generated += a
            phase = (t-phase_offsets[j]) % cycle
            cap = 2*sat/3600 if green+lost/2 <= phase < cycle-lost/2 else 0
            f = min(side[j], cap)
            side[j] -= f
            side_exited += f
        side_delay += sum(side)
        mq = sum(sum(d['ready'])+sum(d['source']) for d in dirs)
        moving = sum(sum(d['moving']) for d in dirs)
        peak_main = max(peak_main, mq)
        peak_side = max(peak_side, max(side))
        if keep_series and t % 60 == 0:
            series.append([t/60, round(mq, 3), round(sum(side), 3)])
        if t == pulse-1:
            pulse_exited = sum(d['exited'] for d in dirs)
            pulse_remaining = sum(d['generated']-d['exited'] for d in dirs)
        if t >= pulse and mq + moving + sum(side) < 1e-6:
            break
    generated = sum(d['generated'] for d in dirs)
    residual = sum(d['generated']-d['exited'] for d in dirs) + sum(side)
    for d in dirs:
        assert abs(d['generated']-d['exited']-sum(d['ready'])-sum(d['moving'])-sum(d['source'])) < 1e-4
    assert abs(side_generated-side_exited-sum(side)) < 1e-4
    assert abs(generated-pulse_exited-pulse_remaining) < 1e-4
    main_delay = sum(d['delay'] for d in dirs)
    out = dict(main_delay_min=main_delay/max(1, generated)/60,
               side_delay_min=side_delay/max(1, side_generated)/60,
               all_delay_min=(main_delay+side_delay)/max(1, generated+side_generated)/60,
               main_time_min=sum(d['systemtime'] for d in dirs)/max(1, generated)/60,
               eb_delay_min=dirs[0]['delay']/max(1, dirs[0]['generated'])/60,
               wb_delay_min=dirs[1]['delay']/max(1, dirs[1]['generated'])/60,
               main_generated=generated, side_generated=side_generated,
               main_exited_at_pulse_end=pulse_exited,
               main_remaining_at_pulse_end=pulse_remaining,
               main_exit_fraction=pulse_exited/max(1, generated),
               max_main_queue=peak_main, max_side_queue=peak_side,
               drain_minutes=(t+1-pulse)/60, residual_at_end=residual,
               complete=abs(residual)<1e-4, peak_vc=peak_vc(profile, plan, sat))
    if keep_series:
        out['queue_series'] = series
    return out
