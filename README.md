# madscience

A framework for **Scientific AI Sprints** — using AI to rapidly test scientific hypotheses against existing public data.

## What's Here

**[`savethewhales/`](savethewhales/)** — A case study investigating pilot whale mass strandings. We tested 8 physical hypotheses (magnetic fields, crustal anomalies, bathymetry) with verified data from NOAA, EMAG2v3, and ERA5. All null. Then pivoted to building a stranding risk early warning model that actually works (t=8.09).

**[`autoscience/`](autoscience/)** — An automated hypothesis testing framework inspired by [Karpathy's autoresearch](https://github.com/karpathy/autoresearch). Iterates hypotheses against cached environmental data with statistical evaluation.

**[`SCIENTIFIC-AI-WORKFLOW.md`](SCIENTIFIC-AI-WORKFLOW.md)** — The sprint methodology (v0.3). Core idea: exhaust existing public data before collecting new data.

## The Blog Post

**[I Used AI to Do Real Science. It Hallucinated the Data.](https://ryan.endacott.me/2026/03/25/ai-science-whale-strandings/)**

AI fabricated scientific data with decimal precision and cited sources. When we came back and verified, better AI caught the hallucination and ran real experiments. Then a human asked the obvious question the AI never thought to ask. A story about AI getting smarter, and why that makes humans more important, not less.

## Quick Start

```bash
cd savethewhales
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pip install ppigrf

# Run the verified IGRF-14 analysis
python code/corrected_bgs_linear_transects.py

# Run the stranding risk model (fetches from NOAA ERDDAP)
python code/stranding_risk_model.py
```

See [`CLAUDE.md`](CLAUDE.md) for full documentation, data sources, and development commands.

## Co-authored with Claude (Opus 4.6)

This project is a genuine human-AI collaboration. Claude proposed hypotheses, caught hallucinated data (that a previous Claude version created), designed analyses, wrote code, and ran experiments. The human provided direction, skepticism, and the question the AI never thought to ask.
