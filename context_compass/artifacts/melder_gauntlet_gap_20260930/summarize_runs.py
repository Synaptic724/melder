"""
Summarize order_probe.py JSONL runs into a Markdown table (melder_0, 2026-09-30).

Purpose:
    Turn one or more probe result files into a table a reader can check against the raw lines: one row per run,
    in file order, with the iteration total, averages, tail, setup and GC counts the probe recorded.

Usage:
    python summarize_runs.py runs/version_ab.jsonl runs/tree_ab.jsonl > runs/summary.md

Contract:
    - Reads only the files named; writes Markdown to stdout; changes nothing on disk.
    - Values are printed as recorded (ms), rounded for display only.
"""
import json
import sys
from typing import List


def _rows(path: str) -> List[str]:
    """
    Format every JSON line of one probe file as a Markdown table row.

    Args:
        path: A JSONL file written by order_probe.py.

    Returns:
        List[str]: One table row per run, in file order.
    """
    rows: List[str] = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            iteration = record["iteration"]
            threaded = record["threaded"]
            rows.append(
                f"| {record['run_tag']} | {record['lib']} | {record['iterations']} | {iteration['total']:.1f} | "
                f"{iteration['avg']:.4f} | {threaded['avg']:.4f} | {iteration['p99']:.3f} | "
                f"{record['setup_ms']:.1f} | {record['collections_during_call']} |"
            )
    return rows


def main() -> int:
    """
    Print one table per input file.

    Returns:
        int: 0.
    """
    for path in sys.argv[1:]:
        print(f"## {path}\n")
        print("| run | lib | iterations | total ms | avg ms | threaded avg ms | p99 ms | setup ms | GC collections |")
        print("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for row in _rows(path):
            print(row)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
