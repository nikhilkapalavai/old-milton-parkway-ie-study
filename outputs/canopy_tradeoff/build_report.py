"""Build the report and vector chart from saved results (chart needs reportlab)."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
r = json.loads((HERE/'results.json').read_text())
t = json.loads((HERE/'tradeoffs.json').read_text())
balanced_ids = {'AM':'4L_C120_G84_west','PM':'4L_C120_G84_east'}
balanced = {p:next(x for x in t['nominal_alternatives'] if x['period']==p and x['plan']['id']==pid)
            for p,pid in balanced_ids.items()}
six = {p:next(x for x in r['summary'] if x['period']==p and x['case']=='base' and x['total_lanes']==6)
       for p in balanced}


def seconds(value):
    return f'{60*value:.1f}'


def main():
    rows = []
    for p in ['AM','PM']:
        a,b = balanced[p]['result']['mean'], six[p]['mean']
        rows.append(f"| {p} main road | {seconds(a['main_delay_min'])} | {seconds(b['main_delay_min'])} | +{seconds(a['main_delay_min']-b['main_delay_min'])} |")
        rows.append(f"| {p} cross streets | {seconds(a['side_delay_min'])} | {seconds(b['side_delay_min'])} | +{seconds(a['side_delay_min']-b['side_delay_min'])} |")
    table = '\n'.join(rows)
    stress_rows = []
    for case in ['growth20','combined_stress','combined_stress_reduce10','combined_stress_reduce20','growth20_reduce20']:
        for p in ['AM','PM']:
            a = next(x for x in t['retimed_summary'] if x['case']==case and x['period']==p and x['total_lanes']==4)
            b = next(x for x in t['retimed_summary'] if x['case']==case and x['period']==p and x['total_lanes']==6)
            aval = (seconds(a['result']['mean']['main_delay_min'])+' / '+seconds(a['result']['mean']['side_delay_min'])) if a['result'] else 'No qualifying plan in grid'
            bval = seconds(b['result']['mean']['main_delay_min'])+' / '+seconds(b['result']['mean']['side_delay_min'])
            stress_rows.append(f"| {case} | {p} | {aval} | {bval} |")
    stress_table = '\n'.join(stress_rows)
    doc = f'''# Could four lanes preserve the canopy? A traffic-only study

Completed September 11, 2026 local time (September 12 UTC).

**Conditional finding: a four-lane alternative performed close to six lanes under the nominal assumptions, with additional delay mainly on cross streets. It had limited room for higher demand or lower discharge capacity.** This study assumes that retaining four lanes preserves the canopy. It evaluates the traffic tradeoff; it does not establish actual tree survival or a construction alternative.

The study contains **{r['run_count']+t['additional_simulations']} simulation runs**, an independent capacity calculation, and a documented comparison of competing objectives. All figures below are modeled queue delay, not measured travel time or predictions of current road performance.

## A concrete four-lane candidate

One relatively balanced candidate uses a 120-second cycle, 84 seconds of effective main-road green and 20 seconds for the simplified cross-street phase, with 16 seconds lost per cycle. Progression favors westbound traffic in the morning and eastbound traffic in the afternoon. These are hypothetical model settings, not a field signal-timing plan.

The six-lane comparator was selected from the same candidate grid by minimizing total modeled trip delay on April 1 inputs. It uses a 90-second cycle, 54 seconds of main-road green and 20 seconds of cross-street green, with the same directional progression choices. Both road sizes receive an opportunity to change their timing.

On April 2 inputs, averaging five arrival-pattern seeds:

| Modeled movement | Four lanes: seconds/trip | Six lanes: seconds/trip | Added delay with four lanes |
| --- | ---: | ---: | ---: |
{table}

![Modeled delay comparison](delay_tradeoff.svg)

The four-lane candidate gives cross streets the same 20 seconds of green less often: every 120 seconds rather than every 90. This explains why main-road performance can be close while cross-street waiting increases. Weighted mean delay across all modeled trips is {seconds(balanced['AM']['result']['mean']['all_delay_min'])} versus {seconds(six['AM']['mean']['all_delay_min'])} seconds in the morning and {seconds(balanced['PM']['result']['mean']['all_delay_min'])} versus {seconds(six['PM']['mean']['all_delay_min'])} in the afternoon.

The averages also hide directional differences. Morning eastbound delay is about {seconds(balanced['AM']['result']['mean']['eb_delay_min'])} seconds with four lanes versus {seconds(six['AM']['mean']['eb_delay_min'])} with six; morning westbound is {seconds(balanced['AM']['result']['mean']['wb_delay_min'])} versus {seconds(six['AM']['mean']['wb_delay_min'])}. The model's progression favors the busier direction, rather than making both directions equally fast.

This candidate also had similar four-lane performance on April 1: approximately 46.5 seconds of morning main-road delay and 49.3 seconds in the afternoon. Those figures are from one training seed, not a population estimate.

## What counts as close enough?

The initial research screen allowed at most 30 additional seconds of main-road delay and 15 additional seconds on cross streets, with absolute mean delays no greater than 120 and 90 seconds respectively, no loss greater than two percentage points in the main-road exit fraction, no peak hourly movement above modeled capacity, and full drainage. These thresholds were chosen for comparison; they are not official approval criteria.

No eligible four-lane candidate met that strict cross-street allowance on the second day. In an explicitly exploratory sensitivity check allowing **30 additional seconds on both main road and cross streets**, 2 morning and 6 afternoon candidates met the full screen. The candidate shown above is one of them. Whether roughly 17 extra seconds on cross streets is worth preserving canopy is a value judgment the traffic model cannot make.

The nominal all-trip-delay winner was a different four-lane plan: a 150-second cycle and 112 seconds of main-road green. It slightly outperformed the selected six-lane plan on main-road delay while adding about 31 seconds on cross streets. Presenting only main-road delay would conceal that cost. The shorter-cycle candidate above illustrates another balance.

## Where the four-lane alternative becomes fragile

The study held the originally selected plans fixed while testing growth and operating uncertainty. It then performed a separate retiming search for changed conditions, so failure of a fixed plan would not automatically be called failure of every four-lane option.

Under nominal saturation flow of 1,800 per lane per hour and synthetic cross-street demand of 450 per junction per hour, the two-phase green-time budget allows at most about **11% AM or 13% PM common growth** before the largest observed-pattern peak would exceed capacity, even after continuous green reallocation within a 150-second cycle. These are optimistic bounds within the stated cycle limit, not dated forecasts or measured road capacities.

The relationship is based on the standard capacity equation in [FHWA's archived Signal Timing Manual, Chapter 3](https://ops.fhwa.dot.gov/publications/fhwahop08024/chapter3.htm):

`capacity = number of lanes × saturation flow per lane × effective green / cycle`

For the simplified two-phase model, a necessary condition is:

`critical main demand / (main lanes × saturation) + side demand / (2 × saturation) <= 1 - lost time / cycle`

The independently derived common-growth bound divides the right side by the sum of the two demand ratios. It ignores storage interference, additional turning phases and pedestrian timing, so satisfying it cannot establish feasibility. Exceeding it means the modeled critical peak hour would accumulate a queue; a later lower-demand hour can still clear that queue.

The strongest modeled AM flow occurs at 7 a.m., in the westbound North Point–Cotton Creek link: approximately 2,450 per hour. The PM critical flow is approximately 2,389 eastbound at 3 p.m. between Park Bridge and Parkview. These are inferred link flows using historical spatial ratios; neither location was independently counted in this study. They illustrate why the busiest total-count hour and the limiting directional flow need not be the same.

At a 0.90 volume/capacity target, the nominal AM four-lane green-time budget already has essentially no growth margin. At the lower saturation assumption of 1,600 and cross-street demand of 650, avoiding peak-hour oversaturation requires roughly a 10% AM or 8% PM main-demand reduction in the continuous calculation; keeping 10% capacity headroom requires roughly 22% AM or 20% PM. These are conditional target calculations, not evidence that such reductions can be achieved.

## Can retiming plus demand reduction help?

The retiming extension selected a plan using April 1 inputs separately for each changed-condition case, then applied that plan to April 2. The table gives mean **main-road / cross-street seconds of queue delay per trip**. A missing four-lane entry means none of the tested plans met the training capacity and side-delay criteria; it is not a proof that all possible signal designs fail.

| Scenario ID | Period | Four lanes, retimed | Six lanes, retimed |
| --- | --- | ---: | ---: |
{stress_table}

Scenario definitions:

- `growth20`: both main-road and synthetic side demand increased 20%.
- `combined_stress`: saturation lowered to 1,600 and side demand raised to 650 per junction per hour.
- `combined_stress_reduce10/20`: that same stress case with 10% or 20% fewer main-road arrivals throughout the modeled windows; side demand remains 650.
- `growth20_reduce20`: after 20% growth, reduce main-road arrivals by 20%, leaving them at 96% of the original level; side demand remains 20% higher.

**A 20% reduction combined with retiming produced qualifying four-lane plans in the tested combined-stress case.** Simply reducing main demand while retaining the original long main-road green did not solve cross-street overload. The signal plan has to respond to the changed balance of demand.

The reduction is an input target, not a demonstrated transportation program. Removed trips are not reassigned to other hours or routes, so this is not a simulation of staggered schedules that preserves daily trip totals. Vehicle-trip consolidation, trip avoidance or time shifting would need their own behavioral and network analysis before being credited with this effect.

## How the experiment was run

The [design file](design.json) was saved before the initial runs. Morning profiles cover 6–10 a.m.; afternoon profiles cover 2–8 p.m. Hourly direction totals come from the four explicitly named lanes in [GDOT's April 2025 report](https://gdottrafficdata.drakewell.com/tfdaysreport.asp?node=GDOT_PORTABLES&cosit=0000121_0312&reportdate=2025-04-01&enddate=2025-04-30&dir=%2D3). Queues carry across hour boundaries, followed by up to two hours of drainage.

The grid contains 33 plans for each road size: 90/120/150-second cycles, selected main-green fractions subject to at least 20 seconds of side green, and eastbound/westbound/simultaneous offsets. The initial 132 training runs use April 1, seed 0; 260 runs use April 2 and seeds 10–14 with frozen selected plans across 13 conditions. The exploratory extension adds 90 alternative-plan runs, 306 case-specific training runs and 70 second-day runs. The added search includes all 9 nominal training-eligible four-lane plans per period.

The balanced candidate in the first table was selected for presentation after examining the exploratory second-day tradeoff results. Its reported second-day performance is therefore not an untouched final test. It is also not field validation: no observed delays or queue lengths were available. Calibration requires comparison with measured system performance, as discussed in [FHWA's 2019 calibration guidance](https://ops.fhwa.dot.gov/publications/fhwahop18036/chapter5.htm).

## Limits that matter to the result

- Only two complete observation days at one station are available. The station's `volumeisaxles` metadata remains unresolved; the runs provisionally treat each displayed report unit as a vehicle. Classified data are populated, but processing has not been independently confirmed.
- Observed flow need not equal unmet traffic demand. A count can miss vehicles held upstream or choosing other routes. Other links inherit the historical forecast's spatial ratios, with a separate +15% stress test on unobserved links.
- Signal phases, side-street volumes, saturation rates and existing queues are assumed. Both periods start with empty networks. Longer runs prevent hourly queue resets, but do not establish the real starting queue.
- Side streets are modeled as separate two-lane approaches at every junction. Their queues cannot block the main road. Turning movements are approximated by net changes in link flow, not observed turning matrices; inferred continuation ratios change by hour, without individual trip routes.
- Delays are per entering modeled trip, including partial-corridor trips, not full-length commute times. Five seeds describe synthetic arrival variation only; their narrow ranges are not uncertainty intervals for the road.
- Fifteen fixed-plan stress runs still contained vehicles at the drain cutoff. Their total-delay statistics are incomplete lower bounds and were excluded from successful comparisons. No such censored run supports the headline candidate.
- The model has no measure of canopy area, tree survival, pedestrian performance, emissions, crashes or program cost. This study's scope is the conditional traffic tradeoff.

## Reproduce and inspect

```powershell
python outputs/canopy_tradeoff/check_engine.py
python outputs/canopy_tradeoff/run_study.py
python outputs/canopy_tradeoff/extend_tradeoffs.py
python outputs/canopy_tradeoff/check_results.py
python outputs/canopy_tradeoff/build_report.py
```

Simulation and checks use the Python standard library. Report/chart generation additionally uses ReportLab. The vector figure is [delay_tradeoff.svg](delay_tradeoff.svg). Full outputs are [results.json](results.json) and [tradeoffs.json](tradeoffs.json); the earlier evidence audit is [here](../validation/README.md). The original website remains on its earlier model and does not yet implement this study.

Checks cover seven one-hour legacy regressions, directional mirror symmetry, zero demand, sustained overload, vehicle conservation, finite storage, identical offered demand for paired road-size comparisons, capacity-bound algebra and consistent report extraction. See [checks.json](checks.json).

**Decision supported by this study:** retain the four-lane option as a candidate for field evaluation, with explicit tolerance for additional cross-street delay and a plan for peak demand. The model does not justify declaring canopy removal necessary, or declaring the four-lane alternative proven on the actual corridor.
'''
    (HERE/'README.md').write_text(doc,encoding='utf-8')
    chart()
    print('Created README.md and delay_tradeoff.svg')


def chart():
    from reportlab.graphics.shapes import Drawing, String, Rect
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics import renderSVG
    from reportlab.lib.colors import HexColor
    drawing = Drawing(820,430)
    ink, green, blue = HexColor('#19332f'), HexColor('#287862'), HexColor('#4568a9')
    drawing.add(Rect(0,0,820,430,fillColor=HexColor('#fafbf7'),strokeColor=None))
    drawing.add(String(38,393,'Four lanes can come close, with a cost to side streets',fontName='Helvetica-Bold',fontSize=19,fillColor=ink))
    drawing.add(String(38,367,'Average modeled queue delay • April 2 inputs • five arrival-pattern seeds',fontSize=11,fillColor=ink))
    values = [[],[]]
    for period,metric in [('AM','main_delay_min'),('PM','main_delay_min'),('AM','side_delay_min'),('PM','side_delay_min')]:
        values[0].append(60*balanced[period]['result']['mean'][metric])
        values[1].append(60*six[period]['mean'][metric])
    bar = VerticalBarChart()
    bar.x,bar.y,bar.width,bar.height = 70,100,690,215
    bar.data = values
    bar.categoryAxis.categoryNames = ['AM main road','PM main road','AM cross streets','PM cross streets']
    bar.categoryAxis.labels.fontSize = 11
    bar.valueAxis.valueMin,bar.valueAxis.valueMax,bar.valueAxis.valueStep = 0,60,15
    bar.valueAxis.labels.fontSize = 10
    bar.valueAxis.visibleGrid = True
    bar.valueAxis.gridStrokeColor = HexColor('#dce4e0')
    bar.bars[0].fillColor,bar.bars[1].fillColor = green,blue
    bar.bars.strokeColor = None
    bar.barLabelFormat = '%.1f'
    bar.barLabels.fontSize = 10
    bar.barLabels.nudge = 6
    drawing.add(bar)
    drawing.add(String(70,331,'Seconds per modeled trip',fontSize=11,fillColor=ink))
    drawing.add(Rect(510,329,10,10,fillColor=green,strokeColor=None))
    drawing.add(String(525,329,'Four lanes',fontSize=11,fillColor=ink))
    drawing.add(Rect(625,329,10,10,fillColor=blue,strokeColor=None))
    drawing.add(String(640,329,'Six lanes',fontSize=11,fillColor=ink))
    drawing.add(String(38,50,'Assumes four lanes preserve the canopy. Counts provisionally treated as vehicles.',fontSize=10,fillColor=ink))
    drawing.add(String(38,31,'Exploratory model comparison; not measured road performance. Sources and full assumptions: README.md.',fontSize=10,fillColor=ink))
    renderSVG.drawToFile(drawing,str(HERE/'delay_tradeoff.svg'))


if __name__=='__main__':
    main()
