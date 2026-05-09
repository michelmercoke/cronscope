"""CLI sub-command: cronscope anomaly — detect schedule anomalies."""
from __future__ import annotations

import argparse
from datetime import datetime

from cronscope.anomaly import detect_anomalies
from cronscope.parser import CronParseError


def add_anomaly_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "anomaly",
        help="Detect gaps and bursts in a cron schedule.",
    )
    p.add_argument("expression", help="Cron expression (quoted)")
    p.add_argument(
        "-n", "--count", type=int, default=500,
        help="Number of runs to analyse (default: 500)",
    )
    p.add_argument(
        "--start", default=None,
        help="ISO-8601 start datetime (default: now)",
    )
    p.add_argument(
        "--burst-threshold", type=int, default=5, dest="burst_threshold",
        help="Min runs in window to count as burst (default: 5)",
    )
    p.add_argument(
        "--burst-window", type=int, default=10, dest="burst_window",
        help="Burst detection window in minutes (default: 10)",
    )
    p.add_argument(
        "--long-gap-multiplier", type=float, default=3.0, dest="long_gap_multiplier",
        help="Std-dev multiplier for long-gap detection (default: 3.0)",
    )
    p.set_defaults(func=run_anomaly)


def run_anomaly(args: argparse.Namespace) -> int:
    start: datetime
    if args.start:
        try:
            start = datetime.fromisoformat(args.start)
        except ValueError:
            print(f"Error: invalid --start datetime '{args.start}'")
            return 1
    else:
        start = datetime.now()

    try:
        report = detect_anomalies(
            expression=args.expression,
            start=start,
            count=args.count,
            burst_threshold=args.burst_threshold,
            burst_window_minutes=args.burst_window,
            long_gap_multiplier=args.long_gap_multiplier,
        )
    except CronParseError as exc:
        print(f"Error: {exc}")
        return 1

    print(f"Expression : {report.expression}")
    print(f"Runs       : {report.total_runs}")
    print(f"Mean gap   : {report.mean_gap_seconds:.1f}s")
    print(f"Std gap    : {report.std_gap_seconds:.1f}s")
    print(f"Long gaps  : {len(report.long_gaps)}")
    for start_dt, end_dt, secs in report.long_gaps:
        print(f"  {start_dt.isoformat()} -> {end_dt.isoformat()}  ({secs:.0f}s)")
    print(f"Burst wins : {len(report.burst_windows)}")
    for bstart, bend, cnt in report.burst_windows:
        print(f"  {bstart.isoformat()} -> {bend.isoformat()}  ({cnt} runs)")
    return 0
