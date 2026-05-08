"""CLI sub-command: timeline — render an ASCII timeline for a cron expression."""

from __future__ import annotations

import argparse
from datetime import datetime

from cronscope.parser import parse, CronParseError
from cronscope.timeline import render_timeline


def add_timeline_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "timeline",
        help="Render an ASCII timeline of cron runs over a time window",
    )
    p.add_argument("expression", help="Cron expression (5 fields)")
    p.add_argument(
        "--hours",
        type=int,
        default=24,
        metavar="N",
        help="Length of the time window in hours (default: 24)",
    )
    p.add_argument(
        "--width",
        type=int,
        default=72,
        metavar="W",
        help="Width of the timeline bar in characters (default: 72)",
    )
    p.add_argument(
        "--start",
        default=None,
        metavar="ISO",
        help="Start datetime in ISO format (default: now)",
    )
    p.set_defaults(func=run_timeline)


def run_timeline(args: argparse.Namespace) -> int:
    """Execute the timeline sub-command. Returns exit code."""
    if args.start:
        try:
            start = datetime.fromisoformat(args.start)
        except ValueError:
            print(f"Error: invalid --start datetime '{args.start}'")
            return 1
    else:
        start = datetime.now().replace(second=0, microsecond=0)

    try:
        expr = parse(args.expression)
    except CronParseError as exc:
        print(f"Error: {exc}")
        return 1

    output = render_timeline(
        expr,
        start=start,
        hours=args.hours,
        width=args.width,
    )
    print(output)
    return 0
