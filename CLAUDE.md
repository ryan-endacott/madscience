# CLAUDE.md — AI Assistant Onboarding

## What This Repo Is

A framework for **Scientific AI Sprints** — using AI to rapidly test scientific hypotheses against existing public data in 72-hour cycles. Contains the methodology docs, one active case study (`savethewhales/`), and an automated hypothesis testing framework (`autoscience/`).

## Repo Structure

```
madscience/
├── CLAUDE.md                          # You are here
├── SCIENTIFIC-AI-MANIFESTO.md         # Philosophy: "exhaust the knowable before seeking the unknown"
├── SCIENTIFIC-AI-WORKFLOW.md          # Practical methodology (v0.3), verification protocols
├── README.md                          # One-liner project description
├── autoscience/                       # Automated hypothesis testing (Karpathy autoresearch-inspired)
│   ├── program.md                     # Research directives and available features
│   ├── prepare.py                     # Data loading, 74 features (lags, anomalies, deltas)
│   ├── hypothesis.py                  # The ONE file modified each iteration
│   ├── evaluate.py                    # Runs hypothesis, computes t-stat, logs results
│   ├── run.py                         # Loop orchestrator (WIP)
│   └── experiments.jsonl              # Append-only log of all experiments
└── savethewhales/                     # Case study: pilot whale stranding investigation
    ├── README.md                      # Overview
    ├── CASE-STUDY.md                  # Full methodology case study writeup
    ├── requirements.txt               # Python deps
    ├── pyproject.toml                 # Modern Python config
    ├── journal/                       # Chronological research journal
    │   ├── JOURNAL-2025-05-30.md      # Day 1: NOAA analysis, hypothesis reversal
    │   ├── JOURNAL-2025-05-31.md      # Day 2: BGS replication, replication failure
    │   ├── JOURNAL-2026-03-24.md      # Day 3: Data audit, IGRF-14 null results
    │   ├── JOURNAL-2026-03-25.md      # Day 4: EMAG2v3, ETOPO, risk model, autoscience
    │   ├── LITERATURE-REVIEW-2026-03.md # Literature review (Kirschvink, Zellar, etc.)
    │   ├── EXPERIMENT_DESIGN.md       # Original dual-cue hypothesis design
    │   └── EXPERIMENT_DESIGN_V2.md    # Early warning system design
    ├── code/                          # Analysis scripts
    │   ├── corrected_bgs_linear_transects.py  # IGRF-14 local computation (15 sites)
    │   ├── inclination_isoline_analysis.py    # 2D isoline geometry analysis
    │   ├── crustal_anomaly_analysis.py        # EMAG2v3 crustal anomaly analysis
    │   ├── bathymetry_analysis.py             # ETOPO1 bathymetry analysis
    │   ├── stranding_risk_model.py            # Risk model prototype (t=4.35)
    │   └── (legacy scripts from May 2025 — use hallucinated data, for reference only)
    └── data/
        ├── stranding_events.csv               # 33 events across 10 sites
        ├── igrf14_linear_transects_*.csv       # VERIFIED IGRF-14 results
        ├── crustal_anomaly_*.csv/json          # EMAG2v3 results
        ├── stranding_risk_*.csv/png            # Risk model output
        ├── inclination_isoline_*.csv/json/png  # Isoline geometry results
        ├── magnetic_gradients.csv              # ⚠️ UNRELIABLE — hallucinated May 2025
        └── external/                          # Large files (gitignored)
            ├── autoscience_cache.json          # Cached SST/chl/wind (264 months)
            ├── EMAG2_V3.zip                   # EMAG2v3 raw data (1.1GB)
            └── era5_wind_monthly.nc           # ERA5 wind data
```

## Critical Gotchas and Hard-Won Lessons

**AI WILL hallucinate factual data.** The May 2025 "NOAA gradient values" were fabricated. Raw field values were internally inconsistent and didn't match any real model output. Two sites had ~100km coordinate errors. Always verify against authoritative sources.

**Compute locally when possible.** Using `ppigrf` to compute IGRF-14 locally eliminates the possibility of data fabrication. Same principle applies to any published mathematical model.

**Replication with independent sources is non-negotiable.** The original NOAA results looked definitive (100% confirmation). They collapsed completely with verified data.

**Null results are results.** This project tested 8 magnetic/bathymetric hypotheses — all null. That definitively rules out an entire class of explanations and has scientific value.

## Whale Stranding Study — Current Status

### Magnetic Hypothesis: DEAD

Tested at two resolutions with verified data. All null:
- IGRF-14 core field (t=-0.007, 15 sites)
- EMAG2v3 crustal anomalies (t=0.075, 15 sites)
- Inclination isoline geometry (t=-0.659)
- Bathymetry / coastal geometry (t=-1.340)

### Risk Early Warning Model: WORKING

A prototype at `code/stranding_risk_model.py` significantly predicts stranding months at Farewell Spit (t=4.35, 91% detection). Uses seasonality + SST + chlorophyll from ERDDAP.

### AutoScience: 15 Experiments Run

Best model (t=8.09): Summer × SST anomaly × chlorophyll anomaly. But the t-statistic is mostly driven by seasonality. Within summer months, only **wind speed anomaly** (t=2.19) significantly distinguishes stranding months from non-stranding months.

**Surprising finding**: Low chlorophyll (not high) correlates with strandings. Hypothesis: low offshore productivity concentrates prey nearshore.

### What Needs to Happen Next

1. Add tidal predictions to the risk model
2. Extend to Cape Cod, Tasmania, Orkney (need event dates for those sites)
3. Move to daily resolution (monthly is too coarse for operational use)
4. Test whether the wind anomaly → stranding link holds at other sites
5. Continue autoscience experiments (read `autoscience/experiments.jsonl`)

## Development Commands

```bash
# Set up environment
cd savethewhales
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install ppigrf netCDF4 rasterio openpyxl cdsapi

# Run verified IGRF-14 transect analysis
python code/corrected_bgs_linear_transects.py

# Run crustal anomaly analysis (requires EMAG2v3 in data/external/)
python code/crustal_anomaly_analysis.py

# Run risk model (fetches data from ERDDAP)
python code/stranding_risk_model.py

# Run autoscience
cd ../autoscience
python prepare.py          # Show available features
python evaluate.py         # Evaluate current hypothesis
python evaluate.py log     # Show experiment leaderboard

# ERA5 wind data (requires ~/.cdsapirc — see Copernicus CDS)
# Already cached in data/external/autoscience_cache.json
```

## Data Sources

| Source | Resolution | Auth | Status |
|--------|-----------|------|--------|
| IGRF-14 (ppigrf) | ~3000km | None (local) | Cached |
| EMAG2v3 (NOAA) | ~3.7km | None | Downloaded (1.1GB) |
| ETOPO1 (ERDDAP) | ~1.8km | None | Fetched per-site |
| SST OISST (ERDDAP) | 25km, daily | None | Cached (264 months) |
| Chlorophyll MODIS (ERDDAP) | 4km, monthly | None | Cached (233 months) |
| ERA5 wind (CDS) | 25km, hourly | Free registration | Cached (264 months) |
