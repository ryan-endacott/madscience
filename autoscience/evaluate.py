#!/usr/bin/env python3
"""
AutoScience Evaluator

Runs the hypothesis function from hypothesis.py against cached data,
computes the t-statistic, and logs the result.
"""

import json
import math
import sys
import time
import traceback
import importlib
from datetime import datetime
from pathlib import Path

from prepare import load_cache, compute_features


LOG_FILE = "experiments.jsonl"


def welch_t(a, b):
    """Welch's t-test. Returns (t_stat, mean_a, mean_b, sd_a, sd_b)."""
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return 0, 0, 0, 0, 0
    ma, mb = sum(a)/na, sum(b)/nb
    va = sum((x-ma)**2 for x in a) / (na - 1)
    vb = sum((x-mb)**2 for x in b) / (nb - 1)
    se = math.sqrt(va/na + vb/nb) if (va + vb) > 0 else 1e-10
    return (ma - mb) / se, ma, mb, math.sqrt(va), math.sqrt(vb)


def run_evaluation():
    """Run the current hypothesis and evaluate it."""
    # Load data
    cache = load_cache()
    records = compute_features(cache)

    # Import hypothesis (force reimport)
    if 'hypothesis' in sys.modules:
        del sys.modules['hypothesis']
    import hypothesis

    # Read the hypothesis source for logging
    hyp_source = Path('hypothesis.py').read_text()

    # Extract the docstring or first comment as description
    description = ""
    for line in hyp_source.split('\n'):
        if line.strip().startswith('#') or line.strip().startswith('"""'):
            if 'CURRENT HYPOTHESIS:' in line:
                description = line.split('CURRENT HYPOTHESIS:')[1].strip()
                break

    # Run hypothesis function on each month
    start = time.time()
    results = []
    errors = 0

    for record in records:
        try:
            risk = hypothesis.compute_risk(record)
            if risk is None or not isinstance(risk, (int, float)):
                risk = 0.0
            results.append({
                'key': record['key'],
                'risk': float(risk),
                'had_stranding': record['had_stranding'],
            })
        except Exception as e:
            errors += 1
            if errors <= 3:
                print(f"  Error on {record['key']}: {e}")

    elapsed = time.time() - start

    if errors > 3:
        print(f"  ... and {errors - 3} more errors")

    # Compute t-statistic
    stranding_scores = [r['risk'] for r in results if r['had_stranding']]
    non_stranding_scores = [r['risk'] for r in results if not r['had_stranding']]

    t_stat, s_mean, n_mean, s_sd, n_sd = welch_t(stranding_scores, non_stranding_scores)

    # Above-median detection rate
    if results:
        median_risk = sorted(r['risk'] for r in results)[len(results) // 2]
        above_median = sum(1 for s in stranding_scores if s > median_risk)
        detection_rate = above_median / len(stranding_scores) if stranding_scores else 0
    else:
        median_risk = 0
        detection_rate = 0

    # Determine result
    significant = abs(t_stat) > 3.0
    interesting = abs(t_stat) > 2.0

    # Count previous experiments
    n_prev = 0
    try:
        with open(LOG_FILE) as f:
            n_prev = sum(1 for _ in f)
    except FileNotFoundError:
        pass

    # Log result
    entry = {
        'experiment_id': n_prev + 1,
        'timestamp': datetime.now().isoformat(),
        'description': description,
        'hypothesis_source': hyp_source,
        't_statistic': round(t_stat, 4),
        'stranding_mean': round(s_mean, 4),
        'non_stranding_mean': round(n_mean, 4),
        'stranding_sd': round(s_sd, 4),
        'non_stranding_sd': round(n_sd, 4),
        'n_stranding': len(stranding_scores),
        'n_non_stranding': len(non_stranding_scores),
        'detection_rate': round(detection_rate, 3),
        'errors': errors,
        'elapsed_seconds': round(elapsed, 3),
        'significant': significant,
        'interesting': interesting,
    }

    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(entry) + '\n')

    # Print report
    print(f"\n{'='*60}")
    print(f"  EXPERIMENT #{entry['experiment_id']}: {description or '(no description)'}")
    print(f"{'='*60}")
    print(f"  t-statistic:    {t_stat:+.4f}  {'*** SIGNIFICANT ***' if significant else ('* interesting *' if interesting else '')}")
    print(f"  Stranding months:     mean={s_mean:.4f} (SD={s_sd:.4f}, n={len(stranding_scores)})")
    print(f"  Non-stranding months: mean={n_mean:.4f} (SD={n_sd:.4f}, n={len(non_stranding_scores)})")
    print(f"  Detection rate: {detection_rate:.0%} of stranding months above median")
    print(f"  Errors: {errors}, Time: {elapsed:.3f}s")
    print(f"{'='*60}\n")

    return entry


def show_log():
    """Print experiment log summary."""
    try:
        with open(LOG_FILE) as f:
            entries = [json.loads(line) for line in f]
    except FileNotFoundError:
        print("No experiments yet.")
        return

    print(f"\n{'='*70}")
    print(f"  EXPERIMENT LOG ({len(entries)} experiments)")
    print(f"{'='*70}")
    print(f"  {'#':<4} {'t-stat':>8} {'detect':>7} {'sig':>5}  {'description'}")
    print(f"  {'-'*65}")

    best_t = 0
    for e in entries:
        sig = "***" if e['significant'] else ("*" if e['interesting'] else "")
        print(f"  {e['experiment_id']:<4} {e['t_statistic']:>+8.3f} {e['detection_rate']:>6.0%} {sig:>5}  {e['description'][:45]}")
        if abs(e['t_statistic']) > abs(best_t):
            best_t = e['t_statistic']

    print(f"\n  Best t-statistic: {best_t:+.4f}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'log':
        show_log()
    else:
        run_evaluation()
