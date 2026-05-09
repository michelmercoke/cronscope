"""CLI sub-command: cronscope calendar — show a monthly calendar view."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone

from cronscope.parser import parse, CronParseError
from cronscope.calendar_view import build_calendar_view, render_calendar


def add_calendar_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "calendar",
        help="Display a monthly calendar annotated with cron fire times.",
    )
    p.add_argument("expression", help="Cron expression (5 fields)")
    p.add_argument(
        "--year",
        type=int,
        default=None,
        help="Year (default: current year)",
    )
    p.add_argument(
        "--month",
        type=int,
        default=None,
        choices=range(1, 13),
        metavar="MONTH",
        help="Month 1-12 (default: current month)",
    )
    p.add_argument(
        "--max-per-cell",
        type=int,
        default=3,
        dest="max_per_cell",
        help="Max fire times shown per day in the detail block (default: 3)",
    )
    p.set_defaults(func=run_calendar)


def run_calendar(args: argparse.Namespace) -> int:
    now = datetime.now(tz=timezone.utc)
    year = args.year if args.year is not None else now.year
    month = args.month if args.month is not None else now.month

    try:
        expr = parse(args.expression)
    except CronParseError as exc:
        print(f"Error: invalid cron expression — {exc}")
        return 1

    if not (1 <= month <= 12):
        print(f"Error: month must be between 1 and 12, got {month}")
        return 1

    view = build_calendar_view(expr, year=year, month=month)
    print(render_calendar(view, max_times_per_cell=args.max_per_cell))
    return 0
