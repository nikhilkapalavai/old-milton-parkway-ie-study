# Old Milton Parkway Traffic Simulation Study

This repository contains an industrial engineering project studying GDOT Project 0017187 on SR 120 / Old Milton Parkway in Alpharetta, Georgia. The project asks whether the removal of mature median trees was necessary for traffic improvement, and what lower-impact alternatives could reduce congestion if the widening design still required tree removal.

The work is written as an exploratory, evidence-backed student project. It uses GDOT planning documents, OpenStreetMap corridor geometry, and a custom aggregate queue simulation to compare four-lane signal operations against six-lane widening scenarios. The model is intentionally transparent and reproducible, with assumptions stated directly in the report.

**Latest traffic-only study:** The [canopy tradeoff study](outputs/canopy_tradeoff/README.md) tests longer traffic periods and alternative signal plans across 858 runs. Assuming four lanes preserve the canopy, one candidate added approximately 8 seconds of modeled morning main-road delay, 5 seconds in the afternoon, and 17 seconds on cross streets compared with selected six-lane plans. The study documents limited capacity for demand growth and tests retiming with demand-reduction targets. These are conditional simulation results, not validated road performance. The website remains on the earlier model.

**September 11 validation update:** Read the [evidence and model audit](outputs/validation/README.md) before citing results. It documents project-caused county water relocation, a corrected State Bridge Way signal location, two days of public lane counts, and 315 sensitivity runs. Count-unit processing remains unresolved; these runs are not field calibration. The earlier claim that retiming matched widening is not a supported real-world conclusion. The original simulation, PDF and website remain on the earlier V2 version.

**September 12 decision review:** [Was the canopy worth losing?](outputs/canopy_value/README.md) aggregates delay across modeled trips, values time using USDOT parameters, and calculates the canopy/cost break-even thresholds. Widening's time benefit is potentially substantial, but the missing canopy appraisal and comparable four-lane cost prevent a definitive verdict. This is an illustrative economic screen, not a full benefit-cost analysis.

## Interactive Website

Explore the traffic study in the [Old Milton Traffic Lab](https://old-milton-traffic-lab.nick98976.chatgpt.site). Adjust road design, signal timing, and peak-hour demand; replay queues; compare alternatives; and inspect the tree and cost evidence.

Website source and setup instructions are in [website/](website/). The browser model reproduces all 280 published Python runs. It uses historical forecasts and assumed operations, not live traffic. Hosted access is currently limited to the owner.

## Main Deliverables

- `outputs/canopy_value/` - decision review, aggregate delay valuation and reproducible break-even analysis

- `outputs/canopy_tradeoff/` - latest traffic-only study, competing delay objectives, capacity bounds and complete experiment outputs
- `outputs/validation/` - latest evidence audit, corrected geometry and reproducible sensitivity tests
- `outputs/traffic_simulation_study.pdf` - original V2 simulation report; read the later audit before citing
- `outputs/old_milton_study.pdf` - earlier evidence review of the GDOT concept documents
- `outputs/evidence_excerpt.pdf` - selected source pages from the GDOT documents
- `outputs/project_plan.md` - project plan, research phases, and records-request draft
- `outputs/simulation/` - reproducible model code, inputs, source snapshots, and results

## Key Finding

The available public record supports GDOT's basic reason for using the median: inward widening avoided a much larger right-of-way footprint, higher costs, and more parcel impacts. It does not prove that every removed tree was unavoidable. The traffic simulation suggests that coordinated signal timing and peak-hour demand reduction could materially improve four-lane operations in moderate cases, but they are not a complete substitute under the heaviest stress assumptions without calibrated signal timing, turning movement counts, and field validation.

## Reproduce The Simulation

From the repository root:

```powershell
python outputs/simulation/simulate.py
python outputs/simulation/check_model.py
```

The simulation outputs are already included in `outputs/simulation/results.json`. The corridor network was derived from OpenStreetMap snapshots stored as compressed `.osm.gz` files in `outputs/simulation/`.

## Data Notes

The project does not use Google live traffic data. Google Maps does not provide historical or live traffic volumes through this workspace, so the reproducible model uses GDOT published forecasts and OpenStreetMap geometry. The report names this limitation directly.

OpenStreetMap data is credited to OpenStreetMap contributors under the Open Database License: https://www.openstreetmap.org/copyright

