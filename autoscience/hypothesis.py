"""
AutoScience Hypothesis File

This is the ONLY file the agent modifies.
Write a compute_risk(data) function that takes a dict of features
and returns a float risk score (higher = more likely to strand).

CURRENT HYPOTHESIS: Baseline — seasonality only
"""


def compute_risk(data: dict) -> float:
    """
    Compute stranding risk score from environmental features.

    Args:
        data: dict with keys like 'sst', 'wind_speed', 'season_risk',
              'sst_lag1', 'wind_northerly', 'chlorophyll_anom', etc.
              Values may be None if data is missing for that month.

    Returns:
        float risk score (higher = more likely to strand)
    """
    # Baseline: just seasonality
    return data.get('season_risk', 0) or 0
