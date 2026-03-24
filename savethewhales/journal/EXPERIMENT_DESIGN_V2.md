# Experiment Design v2: Stranding Early Warning System

## Goal
Build a prototype stranding risk score that combines known predictive factors
to estimate mass stranding probability at known hotspot sites. Validate against
historical stranding events.

## Scientific Hypothesis
Zellar et al. (2021) showed that wind/current conditions predict mass strandings
at Cape Cod with ~1 month lead time. We hypothesize that similar oceanographic
precursors predict strandings at other global hotspots (Farewell Spit, Orkney,
Tasmania, etc.).

## Architecture

```
┌─────────────────────────────────────────────────┐
│              STRANDING RISK MODEL                │
│                                                  │
│  Inputs (per site, per day):                     │
│  ┌──────────────┐  ┌──────────────┐             │
│  │ Seasonality   │  │ Tidal Phase  │             │
│  │ (historical   │  │ (spring tide │             │
│  │  month freq)  │  │  = higher)   │             │
│  └──────┬───────┘  └──────┬───────┘             │
│         │                  │                     │
│  ┌──────┴───────┐  ┌──────┴───────┐             │
│  │ Wind Speed/  │  │ Chlorophyll  │             │
│  │ Direction    │  │ (prey proxy) │             │
│  │ (onshore =   │  │ (high = prey │             │
│  │  higher)     │  │  nearshore)  │             │
│  └──────┬───────┘  └──────┬───────┘             │
│         │                  │                     │
│         └────────┬─────────┘                     │
│                  ▼                               │
│         ┌────────────────┐                       │
│         │  Risk Score    │                       │
│         │  (0-100)       │                       │
│         └────────┬───────┘                       │
│                  │                               │
│                  ▼                               │
│         ┌────────────────┐                       │
│         │  Validate vs   │                       │
│         │  Historical    │                       │
│         │  Strandings    │                       │
│         └────────────────┘                       │
└─────────────────────────────────────────────────┘
```

## Data Requirements

### Stranding Events (training/validation)
- Dates of mass stranding events at each hotspot
- Sources: NOAA (US), DOC (NZ), SMASS (Scotland), state agencies
- Need: date, location, species, group size
- Minimum: 10+ events per site for meaningful validation

### Tidal Predictions
- Height predictions at or near each hotspot
- Source: NOAA CO-OPS (US), LINZ (NZ), UKHO (UK)
- Feature: days until next spring tide, tidal range

### Wind Data
- Speed and direction, daily or 6-hourly
- Source: ERA5 reanalysis (global, 1979-present) or NOAA GFS
- Feature: sustained onshore wind speed over past 7/14/30 days

### Chlorophyll-a
- Ocean color satellite data as prey proxy
- Source: NASA MODIS/VIIRS via ERDDAP
- Feature: nearshore chlorophyll anomaly (above/below seasonal mean)

### Sea Surface Temperature (optional)
- May correlate with prey distribution
- Source: NOAA OISST via ERDDAP

## Approach

### Phase 1: Data Gathering
- Compile stranding event database from multiple sources
- Identify API endpoints for each environmental variable
- Download historical time series (2000-2025) for each hotspot

### Phase 2: Feature Engineering
For each site × day, compute:
1. `season_risk` — historical stranding frequency for this month (0-1)
2. `tidal_risk` — proximity to spring tide (0-1)
3. `wind_risk` — sustained onshore wind speed, normalized (0-1)
4. `chlorophyll_risk` — nearshore chlorophyll anomaly (0-1)
5. `combined_risk` — weighted combination

### Phase 3: Validation
- For each site with sufficient events (>10):
  - Compute daily risk scores for the entire historical period
  - Check: are risk scores higher on actual stranding days?
  - ROC analysis: can the risk score discriminate stranding vs non-stranding days?
- Leave-one-out cross-validation across sites

### Phase 4: Prototype Dashboard (if validation succeeds)
- Real-time risk computation using current conditions
- Simple web page or API showing current risk level per site
- Alert threshold for "elevated risk"

## Success Criteria
- Risk score is significantly higher on stranding days than non-stranding days (p < 0.05)
- ROC AUC > 0.7 for at least 3 hotspot sites
- Model trained on some sites generalizes to held-out sites

## Known Risks
- Small sample sizes per site (10-30 events over decades)
- Stranding databases may be incomplete (especially older events)
- Environmental data resolution may not capture local conditions
- Correlation ≠ causation — wind may be a proxy for something else
