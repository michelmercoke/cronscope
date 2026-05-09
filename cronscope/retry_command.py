"""CLI subcommand: retry — analyze retry-safe windows for a cron expression."""

from __future__ import annotations

import argparse
from datetime import datetime

from cronscope.parser import CronParseError
from cronscope.retry_analyzer import analyze_retries


def add_retry_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the 'retry' subcommand."""
    p = subparsers.add_parser(
        "retry",
        help="Analyze retry-safe scheduling windows for a cron expression.",
    )
    p.add_argument("expression", help="Cron expression to analyze.")
    p.add_argument(
        "-n",
        "--count",
        type=int,
        default=48,
        metavar="N",
        help="Number of upcoming runs to examine (default: 48).",
    )
    p.add_argument(
        "--retry-duration",
        type=int,
        default=60,
        metavar="SECONDS",
        dest="retry_duration",
        help="Assumed duration of one retry attempt in seconds (default: 60).",
    )
    p.add_argument(
        "--start",
        default=None,
        metavar="ISO",
        help="Start datetime in ISO format (default: now).",
    )
    p.set_defaults(func=run_retry)


def run_retry(args: argparse.Namespace) -> int:
    """Execute the retry analysis subcommand.

    Returns:
        0 on success, 1 on error.
    """
    start: datetime | None = None
    if args.start:
        try:
            start = datetime.fromisoformat(args.start)
        except ValueError:
            print(f"Error: invalid --start datetime '{args.start}'.")
            return 1

    try:
        report = analyze_retries(
            expression=args.expression,
            start=start,
            count=args.count,
            retry_duration_seconds=args.retry_duration,
        )
    except CronParseError as exc:
        print(f"Error: {exc}")
        return 1

    print(f"Expression : {report.expression}")
    print(f"Runs examined : {len(report.windows) + 1}")
    print(f"Min gap    : {report.min_gap_seconds}s")
    print(f"Max gap    : {report.max_gap_seconds}s")
    print(f"Avg gap    : {report.avg_gap_seconds:.0f}s")

    if report.warnings:
        print()
        for w in report.warnings:
            print(f"  ⚠  {w}")

    print()
    print(f"{'Window Start':<22} {'Window End':<22} {'Gap (s)':>8} {'Safe Retries':>13}")
    print("-" * 68)
    for win in report.windows[:10]:
        print(
            f"{win.start.strftime('%Y-%m-%d %H:%M'):<22}"
            f" {win.end.strftime('%Y-%m-%d %H:%M'):<22}"
            f" {win.gap_seconds:>8}"
            f" {win.safe_retries:>13}"
        )
    if len(report.windows) > 10:
        print(f"  … {len(report.windows) - 10} more windows not shown.")

    return 0
