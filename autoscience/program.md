# AutoScience: Whale Stranding Hypothesis Search

## Your Mission

You are an automated research agent. Your job is to find environmental conditions that predict pilot whale mass strandings at Farewell Spit, New Zealand.

## The Data

You have monthly environmental data (2003-2024, 264 months) cached in a JSON file:
- `sst` — Sea surface temperature (°C), NOAA OISST
- `chlorophyll` — Chlorophyll-a concentration (mg/m³), MODIS satellite
- `wind_u` — Eastward wind component (m/s), ERA5
- `wind_v` — Northward wind component (m/s), ERA5
- `wind_speed` — Wind speed magnitude (m/s), ERA5
- `wind_direction` — Wind direction (degrees from north), ERA5

There were 11 pilot whale mass stranding events at Farewell Spit during 2003-2024:
- 2005-12, 2006-01, 2011-02, 2012-01, 2012-11, 2014-01, 2015-02, 2017-02, 2022-02, 2022-03, 2024-12

## What You Do Each Iteration

1. Read the experiment log (`experiments.jsonl`) to see what's been tried
2. Think about what to try next — consider:
   - Lagged variables (does wind 1, 2, or 3 months before predict strandings?)
   - Nonlinear thresholds (strandings only when SST > X)
   - Interaction effects (high chlorophyll AND warm SST)
   - Derived variables (SST anomaly, wind direction relative to coast, rate of change)
   - Seasonal decomposition (anomaly from monthly climatology)
   - Multi-month patterns (sustained conditions over 2-3 months)
3. Write a `compute_risk(data: dict) -> float` function in `hypothesis.py`
   - Input: dict with keys like `sst`, `sst_lag1`, `chlorophyll`, `wind_speed`, etc.
   - Output: a risk score (float, higher = more likely to strand)
   - The function MUST be deterministic and fast (<1 second)
4. The evaluator runs your function and reports the t-statistic

## Rules

- You can ONLY modify `hypothesis.py` — everything else is fixed
- Your function gets pre-computed features including lags (1-3 months), anomalies, and rates of change
- You CANNOT fetch new data, import heavy libraries, or do anything slow
- Each hypothesis should be DIFFERENT from previous ones — don't repeat failed ideas
- Think about WHY a variable might predict strandings, not just statistical fishing
- The bar is t > 3.0 (roughly p < 0.003 uncorrected) to be considered interesting

## What's Already Known

- Seasonality is the strongest predictor (19/20 events in Nov-Mar)
- A simple model with seasonality + SST + chlorophyll gets t=4.348
- Magnetic fields and bathymetry do NOT predict strandings (tested extensively)
- Zellar et al. (2021) found wind predicts Cape Cod strandings 1 month ahead
- Farewell Spit is a hook-shaped spit — northerly winds push water/prey into Golden Bay

## Hints for Good Hypotheses

- Northerly wind component (wind_v > 0 or wind blowing FROM north) pushes water into Golden Bay
- SST anomaly might matter more than absolute SST (warm anomaly = unusual prey movement?)
- Chlorophyll rate of change could indicate a prey bloom arriving
- Summer season + strong northerly wind + high chlorophyll = maximum trap conditions?
- Look at what makes stranding months DIFFERENT from other summer months
