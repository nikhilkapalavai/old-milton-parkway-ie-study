# Old Milton Parkway: evidence and model audit

Audit date: September 11, 2026. Research notes, not an admissions essay.

The evidence supports road-project-caused relocation of Fulton County water facilities. It does **not** establish that an independent utility project required all the median trees to be cleared regardless of widening. The traffic retest still finds potential benefits from hypothetical signal changes, but does not establish that four lanes could replace widening or preserve the trees.

## 1. What caused the utility relocation?

| Record | Relevant finding | What it establishes |
| --- | --- | --- |
| [GDOT–Fulton County agreement, Exhibit A, PDF p. 3](https://fulton.legistar.com/View.ashx?M=F&ID=14952539&GUID=06CED4A8-1853-44D1-8CBE-DD286C5FDDC1#page=3) | The recital first identifies widening and then says utility adjustments are necessary “due to the construction of this project.” | Direct documentary support for road-project-caused adjustments to county water facilities. The posted exhibit has blank signatures; it is not presented here as an executed copy. |
| [Fulton County action 25-0887, approved November 19, 2025](https://fulton.legistar.com/LegislationDetail.aspx?FullText=1&GUID=9AD617BF-CCB2-4DA1-B116-BC28465F4227&ID=7744982) | The background attributes water-line conflicts and valve adjustments to the bridge/road work and changes in roadway elevation. It approves approximately 3,188 feet of water-line relocation, estimated at $1,768,280. | Confirms approval and the specific physical cause. Inclusion in the county capital budget describes funding; it does not establish an independently necessary replacement project. |
| [Earlier Fulton County action 25-0612, approved August 20, 2025](https://fulton.legistar.com/LegislationDetail.aspx?FullText=1&GUID=AD7197B5-9036-4AE5-A566-A3C7254F9A03&ID=7515806) | The earlier MOU action also attributes relocation to roadway and bridge construction impacts. | Corroborates the stated project dependency. |
| [GDOT concept package, PDF pp. 42–43](https://www.dot.ga.gov/_layouts/GDOT.SharePoint.CustomHttpHandlers/PWDocumentDownloadHandler.ashx?DocGUID=11d2e65d-2e90-4a1a-a0a8-e75ae818d78f&Filename=0017187_CR_MAR2022.pdf#page=42) | The utility report, dated November 2020 and revised April 2021, lists no known utility capital projects in the area and recommends no separate utility funding phase. It anticipates including Fulton County facilities in the road contract. | Supports the project-related interpretation at that planning date. This preliminary inventory explicitly cannot substitute for later utility engineering. It cannot rule out subsequent work by every owner. |
| [GDOT construction notice, April 13, 2026](https://content.civicplus.com/api/assets/8b883552-d5a2-44ee-971d-b2e7fc85f77a?scope=all) | Clearing provides access to utilities, including gas, communications and power, before widening begins. | Establishes the construction sequence. It does not by itself demonstrate that those utilities would need relocation without the road project. |

**Conclusion:** The original question remains worth investigating. The supported causal chain for county water is road/bridge construction → utility conflicts → relocation. The public records reviewed do not support the proposed claim that independent utility work made the trees' loss inevitable.

This is narrower than saying “no widening, no relocation, no clearing” for the entire corridor. The agreement does not isolate the extra lanes from every other component of the road project; owner-specific gas/power/communications plans, independent bridge needs, drainage requirements and tree locations remain unresolved. No tree-by-tree preservation determination has been made. A construction prerequisite is not automatically an independent reason for the project.

## 2. What the traffic data actually contain

[GDOT TADA station 121-0312](https://gdottrafficdata.drakewell.com/tfdaysreport.asp?node=GDOT_PORTABLES&cosit=0000121_0312&reportdate=2025-04-01&enddate=2025-04-30&dir=%2D3) is at approximately 34.06397125, −84.25179971, between Cotton Creek/Brookside and Vista Forest/Brookside. The raw station record is in [station.json](station.json). This corresponds to the model's second link.

The April report contains two complete days, April 1 and April 2, not a month of observations. Their displayed daily totals are 55,248 and 55,217. April 3 contains an incomplete midnight zero, and the remaining dates have missing entries. Those entries were excluded. The audit uses all four named lanes and checks all 48 hourly sums against the all-direction table.

| Reported hour, local time | April 1 | April 2 | Two-day mean | Westbound share from named lanes |
| --- | ---: | ---: | ---: | ---: |
| 3–4 p.m., both days' afternoon peak | 3,977 | 3,728 | 3,852.5 | 46.62% |
| 5–6 p.m. | 3,525 | 3,487 | 3,506 | 48.00% |

The historical 2027 PM input for this link was 2,765. The mean reported 3 p.m. value is numerically 39.33% higher, but these are different years and sampling/design-hour definitions. This comparison does not establish a forecast error.

**Unit qualification:** station metadata contains `volumeisaxles=1`. The public report offers vehicle-class filters, but that alone does not settle its axle-to-vehicle processing. All new runs provisionally interpret one reported volume unit as one modeled vehicle. These are sensitivity tests using public observations, not calibrated predictions of current traffic. Do not present the displayed volumes as verified vehicle demand until their processing is established. [GDOT's traffic monitoring guide](https://www.dot.ga.gov/DriveSmart/Data/Documents/Guides/2025_Georgia_Traffic_Monitoring_Program.pdf) distinguishes axle adjustment for volume-only counts from classification counts.

A subsequent [F2 classification check](classification_check.json) returned daily totals of 46,378 and 46,391 and 3 p.m. totals of 3,370 and 3,099. Thus the classification data are populated, which supports a vehicle-count interpretation; the meaning of the conflicting metadata flag is still unconfirmed. No speculative axle conversion was applied.

**Direction qualification:** aggregate headings in the portal say Northbound/Southbound, while lane names explicitly say Eastbound/Westbound. This audit sums the two explicitly named westbound lanes, rather than interpreting the aggregate headings. Station orientation still needs field or agency confirmation. Applying this one station's ratio to all six links remains an assumption.

The complete transcription, dates, exclusions and source URL are in [counts.json](counts.json).

## 3. Geometry correction

The previous OSM matching method used shared nodes with each named cross street. At State Bridge Way it matched a nearby connection instead of the identified signal. The audit anchors the corridor to [GDOT's signal inventory](https://sigopsmetrics.dot.ga.gov/signal-info), including signal 7273 at 34.05786, −84.23279. The concept package also lists State Bridge Way among the signalized intersections (PDF p. 9). The selected inventory rows are saved in [signals.json](signals.json).

Six inventory coordinates are mapped to a connected OSM carriageway; Kimball Bridge uses an OSM signal anchor. Corrected link lengths are 833.6, 748.6, 424.7, 491.2, 350.3 and 272.2 meters. The largest changes are the two links adjoining State Bridge Way: previously 193.4 and 420.7 meters, now 350.3 and 272.2 meters. Total represented spacing changes from approximately 3.092 to 3.121 km.

This remains approximate geometry. One carriageway's spacing is mirrored for both directions, and the inventory records have 2018 as-of and 2022 modification dates. The inventory supplies locations, not current signal timing. Source labels or conflicting descriptions must be reconciled by location and date; a label alone is not evidence of a new or removed signal.

## 4. Rerun design and results

The audit runs 9 profiles × 7 scenarios × 5 arrival-pattern seeds = **315 simulations**. Controls isolate the geometry change, volume change and directional-share change. Separate tests use each observed day, the 5 p.m. hour, lower saturation flow and higher cross-street demand.

For a reported-volume profile, all six historical PM link volumes are multiplied by `station anchor / 2765`. This matches the second link to the selected report value while preserving the old forecast's spatial pattern. The other five links have not been observed or calibrated by this procedure. The simulation uses the same one-hour arrival pulse and up-to-two-hour drain as V2, from an initially empty network.

Numbers below are five-seed mean main-road queue delay in minutes per entering modeled trip, including delay after the arrival pulse. They are not measured waits, full-corridor travel times, maximum road capacity, or a prediction of GDOT's future signal plan.

| Input profile | Four lanes, coordinated, 84-second green | Six lanes, coordinated, 72-second green | Six lanes, coordinated, 84-second green |
| --- | ---: | ---: | ---: |
| Original V2 PM forecast and geometry, 60% westbound | 0.635 | 0.837 | 0.536 |
| Same forecast, corrected geometry | 0.644 | 0.811 | 0.548 |
| April peak volume anchor, old 60% westbound assumption | 1.259 | 0.911 | 0.621 |
| April peak volume and reported lane-direction ratio | 1.119 | 1.272 | 0.854 |
| April 1 peak and lane-direction ratio | 1.175 | 1.316 | 0.872 |
| April 2 peak and lane-direction ratio | 1.069 | 1.229 | 0.835 |
| Mean 5 p.m. volume and lane-direction ratio | 0.976 | 1.141 | 0.791 |
| April mean peak, saturation lowered from 1,800 to 1,600 per lane per hour | 1.684 | 1.397 | 0.902 |

The same-green comparison at the April mean peak is 1.119 versus 0.854 minutes: about 0.265 minute (16 seconds), or 31%, more modeled delay with four lanes. Under lower assumed saturation, that gap grows to about 47 seconds. The assumptions matter more than the small geometry correction.

**The earlier result does not simply disappear.** With different green allocations, four lanes still outperform the six-lane 72-second scenario in the profile using the reported directional split. Reporting only the volume change and keeping 60% westbound would miss that result. This is why neither “retiming matched widening” nor “the observed counts proved retiming failed” is an adequate conclusion.

In the mean-peak profile, four-lane reference offsets produce 3.634 minutes of main-road delay, coordination alone 2.669, and coordination plus more green 1.119. These are comparisons against invented reference offsets, not measured existing operations. They cannot establish the benefit of retiming the real corridor today.

At minute 60, the equal-green four- and six-lane cases have released about 4,449 and 4,467 modeled main-road trips, with about 288 and 270 still in the system. They ultimately process equal offered demand once the network drains. That near-equality in this finite pulse is **not** a demonstration of equal maximum traffic capacity. It also cannot justify the essay wording “moved as much traffic as six lanes would have.”

The green change has costs. With assumed cross-street arrivals raised from 450 to 650 per junction per hour, cross-street delay rises from about 0.656 minutes under 72-second main green to 3.343 under 84 seconds. Four-lane coordination-only then has lower average delay across all modeled trips (1.683 minutes) than four lanes with the longer main green (2.208). Cross-street queues are modeled separately and do not block main-road traffic, a structural limitation that can understate network interaction.

## 5. What the essay can and cannot claim

- Retire the broad claim that four lanes approached or matched widening as a real-world finding. The original claim did not define a metric, comparison signal plan or acceptable gap.
- Do not claim the utility records reveal an independent constraint that made clearing inevitable. The strongest record points to road-project-caused water relocation.
- The “one-third of the widening benefit after twenty years” sentence remains unverified. This audit retests the disputed afternoon case; it does not validate that separate long-term ratio or a new 2047 forecast.
- The defensible completed work is a transparent screening model followed by a source audit, correction of a signal location, recovery of two days of public lane counts, and sensitivity tests that qualify the early conclusion.
- The traffic model does not monetize canopy or represent root zones, utility access, drainage, bridge work, pedestrian clearance, turning movements or actual signal phases. It cannot decide whether particular trees were necessary casualties of the chosen design.

No new essay has been drafted or submitted as part of this audit.

## Reproduction and checks

From the repository root, with Python 3:

```powershell
python outputs/validation/rebuild_network.py
python outputs/validation/retest.py
python outputs/simulation/check_model.py
```

[retest_results.json](retest_results.json) contains every run, profile, metric, seed and input hash. [retest_summary.csv](retest_summary.csv) contains the scenario means. The tests reproduced all 35 archived V2 PM runs within 1e-7 for the compared metrics, checked all 48 hourly lane sums and both daily totals, and passed flow conservation, finite storage and complete drainage for every new run. Arrival seeds represent timing variation; they are not confidence intervals for real traffic.

The original `outputs/simulation/` results and PDFs remain V2 historical artifacts. The website also remains on that earlier version; this audit does not claim to have updated the deployed model. Use this directory for the corrected geometry and current qualification of the findings.
