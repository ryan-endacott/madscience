#!/usr/bin/env python3
"""
AutoScience Runner

Runs the hypothesis → evaluate loop N times, using Claude to generate
each new hypothesis based on previous experiment results.

Usage:
    python run.py                  # Run 20 iterations (default)
    python run.py --iterations 50  # Run 50 iterations
    python run.py --log            # Just show the experiment log
"""

import subprocess
import sys
import json
import argparse
from pathlib import Path


def read_log():
    """Read the experiment log."""
    try:
        with open('experiments.jsonl') as f:
            return [json.loads(line) for line in f]
    except FileNotFoundError:
        return []


def format_log_summary(entries):
    """Format experiment log for the agent to read."""
    if not entries:
        return "No experiments have been run yet."

    lines = ["Previous experiments:"]
    lines.append(f"{'#':<4} {'t-stat':>8} {'detect':>7}  description")
    lines.append("-" * 60)

    for e in entries[-20:]:  # Last 20
        sig = "***" if e['significant'] else ("*" if e.get('interesting') else "")
        lines.append(f"{e['experiment_id']:<4} {e['t_statistic']:>+8.3f} {e['detection_rate']:>6.0%}  "
                      f"{sig} {e['description'][:50]}")

    best = max(entries, key=lambda e: abs(e['t_statistic']))
    lines.append(f"\nBest so far: #{best['experiment_id']} with t={best['t_statistic']:+.4f}")
    lines.append(f"Total experiments: {len(entries)}")

    return "\n".join(lines)


def run_iteration(iteration: int):
    """Run one hypothesis → evaluate cycle."""
    print(f"\n{'#'*60}")
    print(f"  ITERATION {iteration}")
    print(f"{'#'*60}")

    # Read program and log
    program = Path('program.md').read_text()
    log_summary = format_log_summary(read_log())
    current_hyp = Path('hypothesis.py').read_text()

    # Build a concise prompt for Claude
    prompt = f"""Output ONLY Python code. No markdown, no explanations, no backticks.

TASK: Write hypothesis.py to predict whale strandings at Farewell Spit, NZ.

Available features in data dict: sst, chlorophyll, wind_speed, wind_u, wind_v, wind_northerly, wind_onshore, season_risk, is_summer, month_sin, month_cos.
Each has: _anom (anomaly), _lag1/_lag2/_lag3, _delta (rate of change), _avg2m/_avg3m variants.
Values can be None — use: val = data.get('key') or 0

Stranding months (11 events): mostly Dec-Feb. Northerly wind pushes prey into bay.

{log_summary}

Write a compute_risk(data: dict) -> float function. Try to beat the best t-statistic above.
Start with: # CURRENT HYPOTHESIS: <description>
"""

    # Call Claude via CLI
    result = subprocess.run(
        ['claude', '-p', prompt, '--output-format', 'text',
         '--allowedTools', '', '--model', 'sonnet'],
        capture_output=True, text=True, timeout=60
    )

    if result.returncode != 0:
        print(f"  Claude error: {result.stderr[:200]}")
        return False

    response = result.stdout.strip()

    # Extract the Python code from the response
    # Handle both raw code and markdown-fenced code
    if '```python' in response:
        code = response.split('```python')[1].split('```')[0].strip()
    elif '```' in response:
        code = response.split('```')[1].split('```')[0].strip()
    else:
        code = response

    # Validate it has compute_risk
    if 'def compute_risk' not in code:
        print("  ERROR: Claude didn't produce a valid hypothesis.py")
        print(f"  Response: {code[:200]}")
        return False

    # Write the new hypothesis
    Path('hypothesis.py').write_text(code)
    print(f"  New hypothesis written.")

    # Run evaluation
    eval_result = subprocess.run(
        [sys.executable, 'evaluate.py'],
        capture_output=True, text=True, timeout=30
    )
    print(eval_result.stdout)
    if eval_result.stderr:
        print(f"  Eval stderr: {eval_result.stderr[:200]}")

    return True


def main():
    parser = argparse.ArgumentParser(description='AutoScience Runner')
    parser.add_argument('--iterations', '-n', type=int, default=20,
                        help='Number of iterations to run (default: 20)')
    parser.add_argument('--log', action='store_true',
                        help='Just show the experiment log')
    args = parser.parse_args()

    if args.log:
        entries = read_log()
        print(format_log_summary(entries))
        return

    print("=" * 60)
    print("  AUTOSCIENCE RUNNER")
    print(f"  Running {args.iterations} iterations")
    print("=" * 60)

    for i in range(1, args.iterations + 1):
        try:
            success = run_iteration(i)
            if not success:
                print(f"  Iteration {i} failed, continuing...")
        except Exception as e:
            print(f"  Iteration {i} error: {e}")

    # Final summary
    print("\n" + "=" * 60)
    print("  FINAL RESULTS")
    print("=" * 60)
    entries = read_log()
    print(format_log_summary(entries))

    # Show the best hypothesis
    if entries:
        best = max(entries, key=lambda e: e['t_statistic'])
        print(f"\n  Best hypothesis (#{best['experiment_id']}, t={best['t_statistic']:+.4f}):")
        # Extract just the compute_risk function
        src = best.get('hypothesis_source', '')
        for line in src.split('\n'):
            if line.strip() and not line.startswith('"""'):
                print(f"    {line}")


if __name__ == "__main__":
    main()
