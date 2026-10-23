"""Summarize PresentMon 1.x CSVs; keep raw samples beside a benchmark report.

Use only active-game captures at matching resolution/settings and locations.
These present intervals include scheduling and capture-environment effects;
they do not attribute a hitch to a particular shader or GPU operation.
"""
import argparse
import csv
import json
import math
from pathlib import Path
import statistics


def summarize(path):
    with path.open(newline='', encoding='utf-8-sig') as source:
        rows = list(csv.DictReader(source))
    values = [float(row['msBetweenPresents']) for row in rows]
    if not values or any(not math.isfinite(v) or v <= 0 for v in values):
        raise ValueError(f'Invalid frame intervals: {path}')
    ordered = sorted(values)
    percentile = lambda p: ordered[min(len(ordered)-1, math.ceil(len(ordered)*p)-1)]
    return {
        'file': path.name, 'frames': len(values), 'seconds': sum(values)/1000,
        'average_fps': 1000/statistics.mean(values),
        'median_ms': statistics.median(values), 'p95_ms': percentile(.95),
        'p99_ms': percentile(.99), 'worst_ms': max(values),
        'frames_over_33ms': sum(v > 1000/30 for v in values),
        'frames_over_50ms': sum(v > 50 for v in values),
        'present_api_median_ms': statistics.median(float(r['msInPresentAPI']) for r in rows),
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('captures', nargs='+', type=Path)
    args = parser.parse_args()
    print(json.dumps([summarize(path) for path in args.captures], indent=2))
