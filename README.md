# Old Milton Parkway Traffic Simulation Study

This repository contains an industrial engineering project studying GDOT Project 0017187 on SR 120 / Old Milton Parkway in Alpharetta, Georgia. The project asks whether the removal of mature median trees was necessary for traffic improvement, and what lower-impact alternatives could reduce congestion if the widening design still required tree removal.

The work is written as an exploratory, evidence-backed student project. It uses GDOT planning documents, OpenStreetMap corridor geometry, and a custom aggregate queue simulation to compare four-lane signal operations against six-lane widening scenarios. The model is intentionally transparent and reproducible, with assumptions stated directly in the report.

## Interactive Website

Explore the traffic study in the [Old Milton Traffic Lab](https://old-milton-traffic-lab.nick98976.chatgpt.site). Adjust road design, signal timing, and peak-hour demand; replay queues; compare alternatives; and inspect the tree and cost evidence.

Website source and setup instructions are in [website/](website/). The browser model reproduces all 280 published Python runs. It uses historical forecasts and assumed operations, not live traffic. Hosted access is currently limited to the owner.

## Main Deliverables

- `outputs/traffic_simulation_study.pdf` - final simulation report
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

