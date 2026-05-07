"""CLI subcommand for detecting overlapping cron schedules."""

from __future__ import annotations

import argparse
from datetime import datetime

from cronscope.overlap import find_overlaps
from cronscope.formatter import format_datetime, format_relative
from cronscope.parser import CronParseError


def add_overlap_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "overlap",
        help="Find runs shared between two cron expressions",
    )
    p.add_argument("expr_a", help="First cron expression")
    p.add_argument("expr_b", help="Second cron expression")
    p.add_argument(
        "--count",
        type=int,
        default=100,
        metavar="N",
        help="Number of future runs to evaluate per expression (default: 100)",
    )
    p.add_argument(
        "--start",
        default=None,
        metavar="ISO",
        help="Start datetime in ISO format (default: now)",
    )


def run_overlap(args: argparse.Namespace) -> int:
    start: datetime | None = None
    if args.start:
        try:
            start = datetime.fromisoformat(args.start)
        except ValueError:
            print(f"Error: invalid --start datetime '{args.start}'")
            return 1

    try:
        report = find_overlaps(
            args.expr_a,
            args.expr_b,
            start=start,
            count=args.count,
        )
    except CronParseError as exc:
        print(f"Error: {exc}")
        return 1

    now = start or datetime.now()
    print(f"Expression A : {report.expr_a}")
    print(f"Expression B : {report.expr_b}")
    print(f"Evaluated    : {report.count} runs each" if False else
          f"Evaluated    : {report.total_a} / {report.total_b} runs")
    print(f"Overlapping  : {report.overlap_count} run(s)")
    print(f"Overlap %    : A={report.overlap_ratio_a:.1%}  B={report.overlap_ratio_b:.1%}")

    if report.overlapping_runs:
        print("\nShared run times:")
        for dt in report.overlapping_runs[:20]:
            print(f"  {format_datetime(dt)}  ({format_relative(dt, now)})")
        if report.overlap_count > 20:
            print(f"  ... and {report.overlap_count - 20} more")

    return 0
