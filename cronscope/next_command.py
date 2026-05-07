"""CLI subcommand: show the next N runs for a cron expression."""

from __future__ import annotations

import argparse
from datetime import datetime

from cronscope.parser import parse, CronParseError
from cronscope.scheduler import next_runs
from cronscope.formatter import format_schedule_table
from cronscope.humanizer import humanize


def add_next_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'next' subcommand."""
    p = subparsers.add_parser(
        "next",
        help="Show the next N scheduled run times for a cron expression.",
    )
    p.add_argument("expression", help="Cron expression (quoted), e.g. '*/5 * * * *'")
    p.add_argument(
        "-n",
        "--count",
        type=int,
        default=10,
        metavar="N",
        help="Number of upcoming runs to display (default: 10).",
    )
    p.add_argument(
        "--start",
        default=None,
        metavar="ISO",
        help="Start datetime in ISO 8601 format (default: now).",
    )
    p.add_argument(
        "--no-humanize",
        action="store_true",
        help="Skip the human-readable description header.",
    )
    p.set_defaults(func=run_next)


def run_next(args: argparse.Namespace) -> int:
    """Execute the 'next' subcommand. Returns an exit code."""
    # Parse start datetime
    if args.start:
        try:
            start_dt = datetime.fromisoformat(args.start)
        except ValueError:
            print(f"Error: invalid --start datetime '{args.start}'.")
            return 1
    else:
        start_dt = datetime.now().replace(second=0, microsecond=0)

    # Parse cron expression
    try:
        expr = parse(args.expression)
    except CronParseError as exc:
        print(f"Error: {exc}")
        return 1

    count = max(1, args.count)
    runs = next_runs(expr, start=start_dt, count=count)

    if not getattr(args, "no_humanize", False):
        description = humanize(expr)
        print(f"Schedule : {description}")
        print(f"Expression: {args.expression}")
        print()

    print(format_schedule_table(runs, now=start_dt))
    return 0
