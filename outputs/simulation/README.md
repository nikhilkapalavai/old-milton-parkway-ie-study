# Old Milton Parkway traffic simulation

**V2 archive:** The [September 11 audit](../validation/README.md) corrects the State Bridge Way location and retests the afternoon result using public count observations with explicit qualifications. This directory retains the original V2 inputs and results so the change can be reproduced; use `../validation/` for the updated analysis.

Exploratory, uncalibrated aggregate queue model. Do not present outputs as measured Google Maps travel times or a validated prediction. Main report: ../traffic_simulation_study.pdf.

Run with Python 3 (standard library only):

    python check_model.py
    python simulate.py

Optional geometry reproduction:

    python rebuild_network.py

The model uses GDOT historical forecasts (concept PDF p131), approximate OpenStreetMap spacing, and explicitly assumed signal plans. results.json contains 280 runs; network.json includes OSM paths. OSM snapshots are included under ODbL with attribution to OpenStreetMap contributors: https://www.openstreetmap.org/copyright

See simulation_report.md for results, data gaps, assumptions and limits. Default reference offsets are not the existing signal plan. A 10% or 20% reduction is a tested demand target, not a demonstrated effect of a transit or commute program. No determination of viable tree preservation has been made.
