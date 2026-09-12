MAP-BASED QUEUE SIMULATION / RESEARCH VERSION 2

**Historical V2 report.** Read the [September 11 evidence and model audit](../validation/README.md) before citing these results. The original inputs and numbers below are preserved for reproducibility; the later audit corrects signal geometry and qualifies the afternoon comparison.

What if the median trees had stayed?

Completed: 280 scenario runs using mapped corridor spacing and GDOT historical demand forecasts. Seven alternatives were tested across eight demand/operations profiles, with five arrival-pattern seeds each. Vehicle conservation, finite storage, zero demand, continuous green, and demand-scaling checks passed.

Finding: Keeping four lanes can perform much better with signal coordination under moderate assumed demand. Under higher directional demand, retiming alone is insufficient. Peak-demand reduction can help, but a 20% reduction does not solve the most demanding combined test.

This does not establish that widening or tree removal was unnecessary. The model is a screening experiment. Current signal timings, observed turning counts, travel-time observations, and tree-survival constraints have not been obtained. Historical forecast turning diagrams exist but are not digitized into this model. The reference timing plan is invented and could be worse than existing operations.

Counterfactual | What this simulation can answer

Keep trees and retain four lanes | Operational effects under assumed signal plans and demand. No determination of bridge/tree engineering feasibility.

Keep median trees by widening outside | Same traffic result as inside widening if lane geometry and operations are identical. This model does not establish that identity or net tree survival.

Trees removed, road widened | Signals and peak-demand management can still reduce delay; tree cutting itself is not a traffic-control measure.

No Google Maps traffic colors or live travel times were scraped or used as vehicle counts. Geometry comes from OpenStreetMap; demand comes from the approved GDOT concept package. Google access was not required to run this experiment.

Prepared with AI assistance. This is a reproducible extension of the earlier desk study, not a calibrated engineering forecast or a claim of fieldwork.

OLD MILTON PARKWAY | SIMULATION STUDY | 7 SEPTEMBER 2026

1. Real map data, with explicit assumptions

Junctions west to east | Distance to next junction

1. North Point Parkway | 838 m

2. Cotton Creek Drive | 736 m

3. Vista Forest Drive | 412 m

4. Park Bridge Parkway | 491 m

5. Parkview Lane | 193 m

6. State Bridge Way | 421 m

7. Kimball Bridge Road | End

Mapped signal-to-signal spacing totals 3.092 km (about 1.92 miles). This differs from GDOT total project limits, which may include tie-ins. Distances use shortest undirected trunk-road paths between shared intersection nodes; they approximate spacing, not a surveyed lane network. Current map geometry may reflect construction changes. [M1-M2]

GDOT PDF p131 provides 2027 no-build AM segment volumes of 4,060; 3,880; 3,815; 3,795; 3,630; and 2,790 vehicles/hour. These are interpreted as two-way design-hour totals; a directional split must be assumed. PM and 2047 AM volumes were also transcribed. [G1]

Default assumptions: 60% westbound, 40 mph progression speed, 1,800 vehicles/hour/lane saturation flow, a 120-second cycle, and 450 vehicles/hour of synthetic cross-street demand per junction. These are not measured local operations. FHWA supports saturation-flow screening in this general range, not these site-specific settings. [F1]

OLD MILTON PARKWAY | SIMULATION STUDY | 7 SEPTEMBER 2026

2. What the moderate-demand experiment shows

All rows use the same 2027 AM no-build demand unless a reduction is stated. Values are mean stopped/queue delay per entering trip, including waiting after the demand pulse ends. They are not full-length corridor travel times or predicted current waits.

Scenario | Main road delay (min) | Cross-street delay (min) | All modeled trips (min)

4 lanes: reference offsets | 5.21 | 0.61 | 3.20

4 lanes: coordination only | 3.46 | 0.61 | 2.22

4 lanes: coordination + split | 0.84 | 0.79 | 0.82

4 lanes: signals + 10% fewer cars | 0.75 | 0.79 | 0.77

4 lanes: signals + 20% fewer cars | 0.71 | 0.79 | 0.75

6 lanes: coordination | 1.00 | 0.61 | 0.83

6 lanes: coordination + split | 0.65 | 0.79 | 0.71

Reference and coordination-only cases use 72 seconds of main-road effective green. The split-change cases use 84 seconds, reducing cross-street green from 32 to 20 seconds; 16 seconds per cycle are reserved as lost/clearance time. These are hypothetical two-phase plans, not implementable signal instructions.

Coordination-only improves the four-lane reference in this model. Reallocating green produces a further improvement at the cost of longer cross-street waits. Six lanes under the same 84-second plan perform better than four lanes, avoiding an unfair comparison of different signal plans.

An unchanged six-lane configuration receives identical output whether labeled inward or outward widening because the model has no tree parameter. In the real outside design, turns, driveways, and construction effects could differ; identical traffic performance cannot simply be assumed.

The model intentionally uses equal no-build demand for the widening comparison to isolate supply. GDOT forecast different build demand (e.g., 4,355 versus 4,060 AM vehicles/hour in the first segment). This experiment does not reproduce that demand reassignment or induced travel. [G1]

Arrival-seed variation covers minute-to-minute timing only. Five seeds are not a confidence interval for the real road, and structural uncertainty is much larger. Full outputs, including the individual runs and remaining traffic at minute 60, are saved in results.json.

OLD MILTON PARKWAY | SIMULATION STUDY | 7 SEPTEMBER 2026

3. Where the tree-preserving option struggles

Input case | 4 lanes + signals | 4 lanes + signals + 20% fewer cars | 6 lanes + coordination

2027 AM / default | 0.84 | 0.71 | 1.00

2027 PM / default | 0.64 | 0.58 | 0.84

2027 AM / 50:50 direction | 1.02 | 0.89 | 1.25

2027 AM / 70:30 direction | 3.22 | 0.58 | 0.79

2027 AM / lower discharge | 2.40 | 0.75 | 1.05

2027 AM / busier cross streets | 0.84 | 0.71 | 1.00

2047 AM / default | 2.07 | 0.75 | 1.04

2047 AM / combined stress | 8.86 | 3.11 | 2.74

All values above are modeled main-road queue delay in minutes. The last case combines 2047 forecast demand, a 70% dominant direction, saturation flow of 1,600 vehicles/hour/lane, and 650 cross-street vehicles/hour at each junction.

With busier cross streets, the 84-second main-road green produces about 3.34 minutes of cross-street delay, versus 0.66 with 72 seconds. Under combined stress, these become about 7.32 versus 0.67 minutes. A main-road-only optimization would hide this harm.

Capacity check: Two lanes x 1,800 x (84/120) = 2,520 vehicles/hour in one direction. Against 4,060 x 60% = 2,436, there is little margin. At a 70% split, demand is 2,842, requiring roughly 11% reduction just to match average capacity. This is a lower bound; it ignores burstiness and downstream constraints. [F2; model inputs]

Under combined stress, two lanes x 1,600 x 0.70 = 2,240 versus 4,490 x 70% = 3,143. About 29% reduction would be needed merely to balance that approach; more operating margin may be necessary. Giving still more green would worsen already-overloaded cross streets.

Interpretation: A coordinated four-lane option is a candidate for engineering validation under moderate demand, not a robust substitute for widening across all tested conditions.

OLD MILTON PARKWAY | SIMULATION STUDY | 7 SEPTEMBER 2026

4. The alternative worth pursuing

First: assess existing coordination before changing anything. Obtain controller timing plans and movement counts. Model both directions, turn lanes, pedestrian crossings, and adjacent intersections. Optimize total person delay and maximum queues, subject to side-street and pedestrian constraints. Existing operations may already be coordinated. [F2-F3]

Second: test a peak-demand package. Employer staggered shifts, fewer solo car commutes, carpools/vanpools, and a useful transit connection could reduce offered traffic. On the highest 2027 AM segment, 10% and 20% correspond to about 406 and 812 fewer vehicles in that hour, in both directions combined. These are targets, not demonstrated program effects.

Moving trips to another hour requires a multi-hour check so congestion is not merely shifted. Replacing car trips with transit requires passenger capacity and service that people will use; this study does not assume that a particular route can absorb the target. Measure participation and corridor counts before claiming success.

Third: identify localized bottlenecks. Evaluate whether protecting turn-lane storage, changing access, or using small external widening at selected intersections can remove a bottleneck while retaining tree clusters. No localized geometry change has been simulated here because its plan dimensions and turning counts are missing. This is the next design candidate, not a proven result.

If the selected road/bridge design truly requires tree removal: combine any necessary capacity work with validated coordination and peak-demand management. Use final grading/drainage and arborist records to separate unavoidable removals from potential retention. Replanting and canopy restoration address the environmental loss; they do not substitute for a traffic intervention.

What would settle the original question? A four-lane or selective-widening alternative must both pass a calibrated operations test and preserve viable trees under its actual construction footprint. The current model addresses only an initial portion of the operations question.

No contacts were messaged. The existing records-request draft can be extended to request AM/PM turning counts, 15-minute profiles, signal splits/offsets/phasing, observed queues, travel-time samples, and a native model of the final design.

OLD MILTON PARKWAY | SIMULATION STUDY | 7 SEPTEMBER 2026

5. Method, validation, and reproducibility

The model is a one-second aggregate queue simulation with two directions, seven signal nodes, and six finite-storage links per direction. Link travel time derives from OSM length and assumed speed. Storage uses 7.5 meters per queued vehicle per lane. Flow is fractional and conservation-based; it is not individual vehicle-following or lane-changing simulation.

A one-hour arrival pulse begins with an empty network, followed by up to two hours of clearing. Minute-wise lognormal variation has about 10% variability and is normalized to preserve the hourly totals. Mainline entries and exits use the minimum net flows needed to match consecutive segment volumes. This does not identify actual origin-destination patterns or intermediate turnover.

Local entry flow joins an aggregate main-road queue, and exits split proportionally after service. Cross-street traffic is a separate synthetic queue with two aggregate discharge lanes. There are no explicit turning conflicts, turn pockets, bus stops, pedestrian phases, adaptive detectors, spillback on cross streets, incidents, or neighboring-network rerouting. Those omissions can materially change the results.

Finite mainline storage blocks upstream transfers. External source backlog is retained and included in delay rather than silently discarding unmet demand. Waiting is accumulated through clearance and divided by generated trips; driving time is excluded from the headline delay. Conservation and storage assertions run in every experiment. All 280 runs cleared by the horizon.

Checks passed: zero demand yields zero delay; low demand with continuous green yields essentially no queue; the 20% case offers exactly 80% of mainline demand; relabeling identical geometry does not alter flow; generated traffic equals exited plus remaining traffic. These validate implementation behavior, not calibration to Alpharetta.

Run: python check_model.py, then python simulate.py from the simulation folder. Standard Python 3 is sufficient. network.json contains the map paths and input provenance; results.json stores all runs. rebuild_network.py and compressed OSM snapshots reproduce the distance extraction without network access.

Before a policy conclusion: replace assumed inputs, calibrate against observed queues/travel times from several comparable weekdays, validate on held-out observations, model the final turn geometry, and test longer demand periods and adverse conditions. A nice animation would not replace these steps. [F3]

OLD MILTON PARKWAY | SIMULATION STUDY | 7 SEPTEMBER 2026

6. Sources and input audit

G1. GDOT approved concept report, March 21, 2022; PDF p131 (demand), p129 (capacity), p14 (alternatives). Source

M1. OpenStreetMap API corridor snapshot, downloaded September 7, 2026. Source

M2. OpenStreetMap API eastern corridor snapshot, same date. Source

M3. Map data copyright OpenStreetMap contributors; Open Database License. Source

F1. FHWA Traffic Signal Timing Manual, Chapter 3: saturation flow and observations. Source

F2. FHWA Traffic Signal Timing Manual, Chapter 6: coordination and competing users. Source

F3. FHWA Traffic Analysis Toolbox, Volume III: simulation application guidance. Source

G2. GDOT traffic data portal / TADA. Located but no new station count used. Source

GM. Google Routes API traffic-aware routing documentation. No Google traffic observations used. Source

Historical forecast turning diagrams are included in GDOT attachment 7 (PDF pp57-126). They were located and spot-checked, but not fully digitized/reconciled here. Some diagram footers use 2029 while the summary table uses 2027; reconcile the versions before calibration. A discovered GDOT ArcGIS service described inclement-weather counters and was not used. Overpass requests failed; the OSM map API supplied geometry.

Input category | Evidence status

Road spacing and named intersections | Derived from downloaded OSM data; approximate geometry.

Segment traffic demand | Historical GDOT forecasts; not September 2026 measurements.

Direction split, signals, saturation, speed, cross traffic | Assumptions tested partly through sensitivity; no site calibration.

Tree locations, root survival, environmental impact | Not modeled; no verified tree-preservation count.

The full study package is AI-assisted. Reproduce and understand it before using it in an application. A truthful project description is: built an exploratory corridor queue model using public map geometry and agency traffic forecasts; tested signal and demand-management scenarios while documenting uncertainty.
