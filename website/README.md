# Old Milton Traffic Lab

An interactive industrial engineering study by Nikhil Kapalavai, prepared with AI assistance. Visitors can change lane configuration, signal green time, coordination, and offered demand; replay aggregate queues at seven junctions; compare alternatives; and inspect the tree, property, and cost evidence.

This is an **uncalibrated screening experiment**, not live traffic, a Google Maps traffic feed, or an official engineering recommendation. No tree-preservation count is inferred. The website carries the original study's limitations alongside the results.

## Run locally

Requires Node.js 22.13 or later and npm.

```sh
npm ci
npm run dev
```

```sh
node --experimental-strip-types lib/verify-model.mjs
npx tsc --noEmit
npm run build
```

The verification command uses Node's built-in TypeScript stripping. Node 24 is also supported.

## Model and data

- `lib/simulation.ts` directly ports the study's one-second Python fluid-queue model. Finite main-road storage and external backlog preserve offered traffic.
- `lib/simulation.worker.ts` runs scenarios away from the page's UI thread. No API keys or server-side simulation are required.
- `lib/data/network.json` contains OpenStreetMap paths, junctions, link lengths, and provenance.
- `lib/data/model-inputs.json` preserves GDOT segment forecasts and the Python model's normalized arrival factors for five reproducible seeds.
- `lib/data/verification.json` contains the 280 published Python runs used for numerical regression comparisons; it is not imported by the website.
- The website uses seed 0; the report summarizes five-seed means. Website results can differ slightly from report averages.
- The reference scenario is recalculated for the same demand forecast and advanced assumptions, with four lanes, 72 seconds of main-road green, invented offsets, and zero demand reduction.
- Inward and outward widening have identical traffic outputs when their six-lane geometry and settings match. Tree survival and real access changes are outside the model.
- Queue replay visualizes aggregate queues sampled each minute, not individual vehicle trajectories. Road geometry is approximate; it totals 3.09 km between modeled junctions and is not the construction footprint.

Original study and Python source: https://github.com/nikhilkapalavai/old-milton-parkway-ie-study

Map data © OpenStreetMap contributors, under the Open Database License: https://www.openstreetmap.org/copyright

## Validation

The browser implementation matches all 280 original Python runs within numerical tolerance for main/side/all-trip delay, peak main-road queue, remaining traffic at minute 60, and clearance time. Additional checks cover inside/outside equivalence, 20% demand scaling, invalid inputs, and vehicle conservation/storage at slider boundary combinations. These are software checks, not validation against real traffic.

The interface includes optional feature-detected WebMCP tools, `run_traffic_scenario` and `read_traffic_results`. They use the same state and calculation as the page. The available browser-control API did not provide a supported WebMCP execution context, so these optional tools were not verified through a browser registry. Normal page controls do not depend on WebMCP. Browser UI testing was not requested or performed.

## Deployment

Built with the Sites starter using React, Vinext, and the supplied Shadcn/Base UI primitives. The `.openai/hosting.json` file contains the public project identifier only. Credentials and local runtime state are excluded from Git. Reports are served from `public/reports`.
