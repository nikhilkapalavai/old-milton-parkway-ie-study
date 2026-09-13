# Was the canopy worth losing?

Decision review, September 12, 2026. This is an economic screening calculation using the completed traffic study, not a completed canopy appraisal or benefit-cost analysis.

**The available evidence does not establish that losing the canopy was worth it. It also does not establish that preserving it was the better overall decision. Widening has potentially substantial traffic benefits; the specific canopy's value and the cost of a comparable four-lane alternative remain unknown.**

My recommendation for the original, pre-clearing decision would have been to evaluate the four-lane alternative in the field before ruling it out. This is a judgment about resolving uncertainty before an irreversible choice, not proof that the trees could survive or a recommendation to stop ongoing construction. Utility requirements remain outside the decision scope, as requested.

## Small delays add up

The earlier headline of roughly 5-8 additional main-road seconds and 17 additional cross-street seconds with four lanes understates the scale if treated as the entire cost of preservation. Those seconds apply to many trips.

Using April 2 inputs and five-seed mean results, the selected six-lane design saves the following queue time compared with the 120-second-cycle four-lane candidate:

| Component | AM vehicle-hours saved | PM vehicle-hours saved | Total |
| --- | ---: | ---: | ---: |
| Main road | 31.64 | 37.14 | 68.79 |
| Synthetic cross streets | 57.72 | 86.64 | 144.37 |
| All modeled components | 89.37 | 123.79 | **213.15** |

AM covers 6-10 a.m. and PM covers 2-8 p.m., with queue drainage afterward. These are model totals, not observed daily congestion. Calculation: `entering modeled trips × difference in mean queue delay (minutes) / 60`. Main-road entries include partial-corridor trips. Cross streets are separate hypothetical queue components, with no observed route matching.

Against the four-lane plan selected for minimum total modeled delay, with a 150-second cycle, the six-lane benefit is **187.34 vehicle-hours**. That four-lane plan improves main-road delay relative to six lanes but adds about 31 seconds on cross streets. Both comparisons are retained because they distribute waiting differently.

**About 68% of the balanced comparison's time benefit comes from unmeasured cross-street demand.** For the 150-second plan, all the net six-lane advantage comes from cross streets, partly offset by a main-road disadvantage. This dependence on assumed demand is a major limitation.

## A dollar scale for time

[USDOT's 2026 guidance](https://www.transportation.gov/sites/dot.gov/files/2025-12/Benefit%20Cost%20Analysis%20Guidance%202026%20Update%20(Final).pdf#page=40) provides $21.80 per person-hour for general all-purpose travel and $20.10 for personal travel, in 2024 dollars. Passenger-vehicle occupancy references are 1.34 weekday peak and 1.41 off-peak; the real discount rate is 7% (PDF pp. 13, 40-41).

For illustration, use 1.34 occupants per modeled vehicle, 250 equivalent weekdays each year and unchanged delay benefits for 20 years. No benefits are assigned to other hours or weekends. These assumptions are not measured annual performance or a growth forecast. Because the modeled windows include off-peak hours, 1.41 occupancy is tested separately. Fleet composition is not calibrated; all vehicles are provisionally valued as passenger vehicles.

| Four-lane comparator | Illustrative annual time value | 20-year present value at hypothetical opening |
| --- | ---: | ---: |
| Minimum total modeled delay | $1.37 million | $14.49 million |
| More balanced distribution of delay | $1.56 million | $16.49 million |

Both columns use constant 2024 dollars. The second discounts annual benefits at 7%. This is travelers' economic time value, **not city-budget revenue**. The range reflects two timing choices, not a confidence interval. Holding benefits constant does not validate four-lane performance under future growth. The script also saves 108 valuation sensitivities across days, occupancy, time value, horizon and discount rate.

## The break-even decision

In common price and present-value terms, widening wins if **`T + U > E + C`**, where:

- `T` is time saved by six lanes relative to four lanes.
- `E` is incremental construction and operating resources, net of residual value, over a comparable four-lane plan.
- `C` is net canopy loss value, accounting for maintenance and the growth/survival of replacement planting.
- `U` is other net benefits, such as safety, less other losses, such as construction disruption or additional emissions.

The canopy value remains unknown; it is not assigned zero. With other net benefits temporarily omitted, the following thresholds show the canopy loss that could be offset after additional spending. **The spending amounts are hypothetical, not project estimates.**

| Additional net cost of six lanes | Canopy-loss threshold: minimum-delay four-lane comparator | Canopy-loss threshold: balanced four-lane comparator |
| --- | ---: | ---: |
| $0 million | $14.49 million | $16.49 million |
| $5 million | $9.49 million | $11.49 million |
| $10 million | $4.49 million | $6.49 million |
| $15 million | -$0.51 million | $1.49 million |
| $20 million | -$5.51 million | -$3.51 million |

Entries are opening present values in 2024 dollars. Below a positive threshold, widening has a positive balance on the included components. A negative threshold means time benefits alone fail to cover additional spending even before canopy loss. Safety and other net benefits could change either result.

At an incremental cost of $10 million, net canopy value above approximately $4.5-$6.5 million would favor preservation on the included components. At $20 million, time savings alone favor four lanes even without assigning a canopy value. Neither the actual cost difference nor canopy value has been established.

The full project budget cannot substitute for the incremental cost: bridges, sidewalks, rehabilitation and shared work must be treated consistently. This analysis is retrospective; costs already incurred require different treatment in a decision about changing the ongoing project.

## Stress-testing the four-lane alternative

I reran the retiming search across **5,280 candidate evaluations** and checked the selected plans on **800 holdout runs** using five independent arrival seeds. The grid varies synthetic side-street demand (50, 100, 300, 450 and 650 vehicles per hour per junction), main-road demand at the observed profile and at 20% higher, saturation flow (1,600 or 1,800 vehicles per hour per lane) and signal lost time (16 or 24 seconds). A four-lane plan passes only if it drains completely, stays at or below 1.0 peak v/c, keeps mean main-road delay at or below 120 seconds and side-street delay at or below 90 seconds, stays within 30 seconds of the six-lane main-road result and 15 seconds of its side-street result, and loses no more than two percentage points of the main-road exit fraction relative to six lanes.

At the observed main-road profile with 1,800 saturation and 16 seconds of lost time, the holdout comparison passes at side demand of 50 and 100 vehicles per hour per junction. At 300, the AM case fails the side-street comparison; at 450, both AM and PM fail it, adding about **31 seconds** of side-street delay while reducing main-road delay by about **7-8 seconds**. The full grid has **16 passing cases out of 80**; no case at 20% higher main-road demand passes. At side demand 450 with these saturation and lost-time settings, the selected four-lane plan has peak side v/c of about **0.85** and mean side-street delay of **1.04 minutes (62.4 seconds)**. It fails the relative side-street delay allowance, not the capacity screen. The earlier description incorrectly labeled the delay in minutes as a capacity ratio; the saved simulation values were correct.

This is a screening result, not a proof that every possible four-lane signal plan fails. Each road size's plan is selected for minimum total modeled delay among training-eligible candidates when available; otherwise the minimum-delay candidate is retained as a fallback. Another plan may distribute waiting differently. The 31-second side-street penalty and the earlier 17-second penalty use different four-lane timings at the same nominal demand. Pass/fail results need not change monotonically with side demand because the selected plans can change. The 16-of-80 count describes this scenario grid, not a real-world probability of success. The traffic test cannot justify saying the canopy was clearly worth losing, and it cannot establish that four lanes could have met GDOT's 2047 design-year need. It supports a narrower conclusion: **some modeled conditions support further investigation of a four-lane canopy-preserving alternative, but the selected four-lane plans did not pass the comparison across the full range of tested demand and operating conditions.**

The stress-test output is [stress_test.json](stress_test.json), and the reproducible script is [stress_test.py](stress_test.py). The model remains an aggregate finite-storage queue model with synthetic side demand; it is not a calibrated microsimulation or a canopy appraisal.

## The documented outside-widening option

The [GDOT concept report, PDF pp. 13-14](https://www.dot.ga.gov/_layouts/GDOT.SharePoint.CustomHttpHandlers/PWDocumentDownloadHandler.ashx?DocGUID=11d2e65d-2e90-4a1a-a0a8-e75ae818d78f&Filename=0017187_CR_MAR2022.pdf#page=14), lists inside widening at **$29,196,795** and outside widening at **$41.8 million**. The total premium is **$12,603,205**, including **$9,694,000** additional right-of-way cost. Outside widening affected 63 parcels versus 18 and took an estimated 42 months versus 30. These are historical concept estimates, not current bids or same-dollar inputs to the table above.

GDOT describes the median as reserved for expansion and the outside option as having greater adjacent-property and environmental impacts. It reports an operations-and-safety benefit-cost ratio of **2.98**. That supports the agency's economic case; its calculation and a comparison against retimed four lanes have not been independently reproduced here.

Outside widening cannot be assumed to save trees overall. If it saved 200 additional mature trees after exterior losses, its historical premium would be about **$63,016 per net tree saved**; at 100 trees, **$126,032**. These are hypothetical thresholds, not inventories or tree valuations.

## The missing canopy value

I did not locate a tree-by-tree removal inventory, measured canopy-loss area or corridor appraisal in the records reviewed. That does not establish that no such record exists. Median width alone is not canopy area.

[i-Tree guidance](https://www.itreetools.org/faqs_home) identifies the inputs for individual tree benefits and replacement comparisons, including species, size, location and health. A defensible appraisal here must consider:

- Carbon storage changes and future sequestration, air quality and stormwater.
- Heat and shade at the actual locations; home energy savings cannot automatically be credited to median trees.
- Habitat, visual character and community value, including values not readily monetized.
- Exterior tree losses under alternative designs and the years required for replacement canopy to grow.

Inventing a dollar value per tree would manufacture the missing answer. Replacement/appraisal values and annual service benefits must also be checked for double counting.

## Decision supported

**There is a credible economic case for widening, but no demonstrated canopy-specific verdict.** Small per-trip differences do not make the traffic benefit negligible. The prior study also found limited four-lane growth margin; no four-lane plan qualified in its tested 20% growth grid. A demand-reduction input was not a demonstrated transportation program.

If six lanes are required, the planning record supports inside widening's cost and footprint advantage over outside widening. The open question is whether a workable four-lane alternative would outperform widening after all costs and canopy benefits are counted. Resolving it requires field-calibrated traffic performance, comparable alternative costs and an actual canopy appraisal. My preservation-first evaluation recommendation is a stated judgment, not a claim that the model proves the trees were worth more than the lanes.

The traffic model still uses two days at one station, unresolved count-unit metadata, inferred link flows and assumed signal phases and side demand. It does not measure crashes, pedestrian operation, induced/diverted trips or canopy survival. Those omissions can change the decision in either direction.

## Reproduce

Run `python outputs/canopy_value/analyze.py`. It reads saved simulation outputs rather than rerunning traffic. [results.json](results.json) records source URLs, assumptions, hashes, both comparisons and 108 valuation scenarios. Checks verify equal offered demand, complete queue drainage and agreement between movement-level and all-trip delay totals.
