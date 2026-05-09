"""CLI subcommand: streak — show consecutive-run streaks for a cron expression."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone

from cronscope.parser import parse, CronParseError
from cronscope.streak import analyze_streaks


def add_streak_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "streak",
        help="Analyze consecutive active/inactive days for a cron expression",
    )
    p.add_argument("expression", help="Cron expression (5 fields)")
    p.add_argument(
        "--days",
        type=int,
        default=30,
        metavar="N",
        help="Number of days to analyze (default: 30)",
    )
    p.add_argument(
        "--start",
        default=None,
        metavar="ISO",
        help="Start datetime in ISO 8601 format (default: now)",
    )


def run_streak(args: argparse.Namespace) -> int:
    try:
        parse(args.expression)
    except CronParseError as exc:
        print(f"Error: {exc}")
        return 1

    if args.start:
        try:
            start = datetime.fromisoformat(args.start).replace(tzinfo=timezone.utc)
        except ValueError:
            print(f"Error: invalid --start datetime '{args.start}'")
            return 1
    else:
        start = datetime.now(tz=timezone.utc)

    report = analyze_streaks(args.expression, start=start, days=args.days)

    print(f"Expression : {report.expression}")
    print(f"Period     : {report.days_analyzed} days from {start.date()}")
    print(f"Active days: {report.active_days}  Inactive: {report.inactive_days}")
    print(f"Longest streak : {report.longest_streak} day(s)")
    print(f"Longest gap    : {report.longest_gap} day(s)")
    if report.streaks:
        print(f"All streaks: {report.streaks}")
    if report.gaps:
        print(f"All gaps   : {report.gaps}")
    return 0
