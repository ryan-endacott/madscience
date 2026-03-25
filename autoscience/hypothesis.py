# CURRENT HYPOTHESIS: Summer x count of risk factors present (wind high + chl low + SST warm prior month)
def compute_risk(data: dict) -> float:
    summer = data.get('is_summer') or 0
    if summer < 0.5:
        return 0.0

    wind_anom = data.get('wind_speed_anom') or 0
    chl_avg3m = data.get('chlorophyll_avg3m')
    sst_anom_lag1 = data.get('sst_anom_lag1') or 0

    # Count risk factors (cleaner signal than weighted combination)
    factors = 0
    if wind_anom > 0.3:  # windier than usual
        factors += 1
    if chl_avg3m is not None and chl_avg3m < 0.85:  # low 3-month chlorophyll
        factors += 1
    if sst_anom_lag1 > 0.2:  # warm prior month
        factors += 1

    return 0.3 + 0.23 * factors  # 0.3, 0.53, 0.76, 1.0
