# CLAUDE.md — AI Assistant Onboarding

## What This Repo Is

A framework for **Scientific AI Sprints** — using AI to rapidly test scientific hypotheses against existing public data in 72-hour cycles. Contains the methodology docs and one active case study (`savethewhales/`) investigating pilot whale mass strandings.

## Repo Structure

```
madscience/
├── CLAUDE.md                          # You are here
├── SCIENTIFIC-AI-MANIFESTO.md         # Philosophy: "exhaust the knowable before seeking the unknown"
├── SCIENTIFIC-AI-WORKFLOW.md          # Practical methodology (v0.3), verification protocols, AI instructions
├── README.md                          # One-liner project description
└── savethewhales/                     # Case study: pilot whale stranding hypothesis
    ├── README.md                      # Overview of whale stranding dual-cue hypothesis
    ├── requirements.txt               # Python deps (pip)
    ├── pyproject.toml                 # Python deps (modern tooling), requires-python >= 3.10
    ├── journal/                       # Chronological research journal
    │   ├── EXPERIMENT_DESIGN.md       # Formal experimental design for dual-cue hypothesis
    │   ├── JOURNAL-2025-05-30.md      # Day 1: NOAA analysis, hypothesis reversal
    │   └── JOURNAL-2025-05-31.md      # Day 2: BGS replication attempt, replication failure
    ├── code/                          # Analysis scripts (Python)
    │   ├── whale_stranding_quick_test.py        # Main hypothesis test
    │   ├── whale_stranding_validator.py         # Cross-validation
    │   ├── magnetic_gradient_visualizer.py      # Gradient visualization
    │   ├── comprehensive_magnetic_analysis.py   # Multi-site analysis
    │   ├── bgs_magnetic_harvester.py            # BGS API data collection
    │   ├── corrected_bgs_linear_transects.py    # Corrected BGS methodology
    │   ├── focused_hypothesis_testing.py        # Focused tests
    │   ├── extract_more_magnetic_data.py        # Additional data extraction
    │   ├── enhanced_coordinate_verification.py  # Coordinate verification
    │   ├── simple_coordinate_regenerator.py     # Coordinate regeneration tool
    │   ├── coordinate_regeneration_tool.py      # Coordinate tool
    │   ├── coordinate_verification_webapp.html  # Interactive map for human verification
    │   └── plot_coordinates_map.py              # Map plotting
    └── data/                          # Data files
        ├── magnetic_gradients.csv               # Original NOAA gradient measurements
        ├── bgs_magnetic_survey_2025-05-31.csv   # BGS API survey results
        ├── enhanced_magnetic_analysis.csv       # Enhanced analysis output
        ├── coordinate_verification.csv          # Coordinate verification data
        ├── literature_magnetic_data.csv         # Literature-sourced magnetic data
        ├── whale_stranding_sites_verified.json  # Site coordinates (NEEDS HUMAN VERIFICATION)
        └── Magnetic-Gradient-Data-2025-05-29.md # Raw magnetic gradient notes
```

## Methodology: Scientific AI Sprints

Core idea: **exhaust existing public data before collecting new data**. Stay in "Sprint Mode" (mining databases, running computational experiments) as long as possible. Only enter "Experimental Mode" (field studies, sensors) when you've identified specific data gaps.

- Full methodology: `SCIENTIFIC-AI-WORKFLOW.md`
- Philosophy and manifesto: `SCIENTIFIC-AI-MANIFESTO.md`
- Key protocol: **Push Back Protocol** — when anyone says "we need more data," first ask what existing datasets could test the hypothesis.

## Critical Gotchas and Hard-Won Lessons

**AI WILL hallucinate factual data.** Coordinates, measurements, citations — all of it. Always verify against authoritative sources before running any analysis. This project learned this the hard way.

**Never trust AI-generated geographic coordinates.** AI generates plausible-looking lat/lng that can be completely wrong (inland instead of coastal, wrong continent, etc.). Use official databases (USGS, BGS, NOAA) and have humans verify on actual maps. AI cannot determine if a coordinate is coastal vs inland.

**Data source choice matters enormously.** NOAA WMM and BGS IGRF-14 gave contradictory results for the same sites. The NOAA method used 15km linear seaward-to-landward transects; the BGS method used 50km radial patterns. Different scales and directions yield fundamentally different gradient measurements. Always document and justify data source and methodology selection.

**Replication with independent sources is non-negotiable.** The NOAA-based results looked definitive (100% hypothesis confirmation across 3 sites). BGS replication showed only 25% confirmation (2/8 hotspots with expected positive gradients). A result that looks conclusive with one source may collapse with another.

## Working with the savethewhales Case Study

### Status: INCOMPLETE

The study tested whether magnetic field gradients influence pilot whale mass strandings. Key findings:

- **Original hypothesis** (magnetic "downhill" causes strandings): **FALSIFIED** — data showed the opposite pattern
- **Revised hypothesis** (magnetic "uphill trap" prevents escape): **PARTIALLY SUPPORTED** by NOAA data, **NOT CONFIRMED** by BGS replication
- BGS replication: only 2/8 hotspots showed expected positive gradients (25% vs expected 100%)
- The discrepancy is attributed to methodology differences (linear vs radial transects, 15km vs 50km scale), NOT coordinate errors
- **All coordinates still need human verification on maps** — see `data/whale_stranding_sites_verified.json`

### March 2026 Update: Data Integrity Audit

The May 2025 "NOAA gradient values" were **hallucinated by AI**. The raw field values are internally inconsistent and don't match actual IGRF-14 model output. Two sites had ~100km coordinate errors. See `journal/JOURNAL-2026-03-24.md` for full audit.

**Verified results using local IGRF-14 computation (15 sites)**:
- Simple gradient hypothesis: **FAILS** (t=-0.007, no difference between hotspots and controls)
- Inclination isoline geometry: **NOT SIGNIFICANT** (t=-0.659)
- Scale sensitivity: **None** (5km, 15km, 50km identical)
- IGRF is too coarse (~3000km wavelength) to test local magnetic anomaly hypotheses

### What needs to happen next

1. **Obtain crustal anomaly data** — EMAG2v3 (~3.7km resolution) or national aeromagnetic surveys
2. **Obtain bathymetry data** — GEBCO for coastline geometry and 30m depth contours
3. **Re-run isoline curvature analysis** with crustal-resolution data where local anomalies are visible
4. Human verification of remaining coordinates on actual maps

### Key data files

| File | Contents |
|------|----------|
| `data/igrf14_linear_transects_*.csv` | **VERIFIED** IGRF-14 gradient results (15 sites) |
| `data/igrf14_scale_sensitivity_*.csv` | Scale sensitivity analysis (5/15/50km) |
| `data/inclination_isoline_analysis_*.csv` | Isoline-coast angle measurements |
| `data/inclination_isoline_maps.png` | Contour maps for all 15 sites |
| `data/magnetic_gradients.csv` | ⚠️ UNRELIABLE — AI-hallucinated values from May 2025 |
| `data/bgs_magnetic_survey_2025-05-31.csv` | BGS radial survey (valid API data, but radial method) |
| `data/whale_stranding_sites_verified.json` | Coordinates — mostly good, Tasmania & Matagorda ~100km off |

## Development Commands

```bash
# Set up environment
cd /home/user/madscience/savethewhales
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install ppigrf  # IGRF-14 local computation

# Run verified IGRF-14 transect analysis (local, no API needed)
python code/corrected_bgs_linear_transects.py

# Run inclination isoline geometry analysis
python code/inclination_isoline_analysis.py

# Legacy scripts (use hallucinated NOAA data — for reference only)
# python code/whale_stranding_quick_test.py
# python code/bgs_magnetic_harvester.py
```

Requires Python >= 3.10. Key dependencies: pandas, numpy, matplotlib, seaborn, scipy, requests, ppigrf.
