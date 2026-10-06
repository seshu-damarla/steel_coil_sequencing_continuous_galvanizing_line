"""Summarize a highs_results.csv file using only the Python standard library."""

from __future__ import annotations

import argparse
import csv
import statistics
from pathlib import Path


def as_bool(value: str) -> bool:
    return value.strip().lower() in {"true", "1", "yes"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file", nargs="?", default="results/highs_results.csv")
    args = parser.parse_args()

    path = Path(args.csv_file)
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    runtimes = [float(r["runtime_sec"]) for r in rows]
    gaps = [float(r["mip_gap"]) for r in rows if r["mip_gap"] not in {"", "None"}]
    optimal = sum(as_bool(r["proven_optimal"]) for r in rows)
    valid = sum(as_bool(r["valid_sequence"]) for r in rows)
    total_iterations = sum(int(r["cut_iterations"]) for r in rows)
    total_cuts = sum(int(r["sec_cuts"]) for r in rows)

    fastest = min(rows, key=lambda r: float(r["runtime_sec"]))
    slowest = max(rows, key=lambda r: float(r["runtime_sec"]))

    print(f"Instances             : {len(rows)}")
    print(f"Proven optimal        : {optimal}/{len(rows)}")
    print(f"Valid sequences       : {valid}/{len(rows)}")
    print(f"Maximum MIP gap       : {max(gaps) if gaps else 'N/A'}")
    print(f"Total runtime (s)     : {sum(runtimes):.3f}")
    print(f"Total runtime (h)     : {sum(runtimes)/3600:.3f}")
    print(f"Mean runtime (s)      : {statistics.mean(runtimes):.3f}")
    print(f"Median runtime (s)    : {statistics.median(runtimes):.3f}")
    print(f"Fastest               : {fastest['instance']} ({float(fastest['runtime_sec']):.3f} s)")
    print(f"Slowest               : {slowest['instance']} ({float(slowest['runtime_sec']):.3f} s)")
    print(f"Cut iterations total  : {total_iterations}")
    print(f"SEC cuts total        : {total_cuts}")


if __name__ == "__main__":
    main()
