"""CLI sub-command: summarize a cron expression over a time window."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta

from cronscope.parser import parse, CronParseError
from cronscope.summarizer import summarize


def add_summary_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "summarize",
        help="Show statistics for a cron expression over a time window.",
    )
    p.add_argument("expression", help="Cron expression (5 fields, quoted)")
    p.add_argument(
        "--days",
        type=int,
        default=7,
        metavar="N",
        help="Window size in days from --start (default: 7)",
    )
    p.add_argument(
        "--start",
        default=None,
        metavar="ISO",
        help="Window start as ISO datetime (default: now)",
    )


def run_summary(args: argparse.Namespace) -> int:
    try:
        expr = parse(args.expression)
    except CronParseError as exc:
        print(f"Error: {exc}")
        return 1

    try:
        start = datetime.fromisoformat(args.start) if args.start else datetime.now().replace(second=0, microsecond=0)
    except ValueError:
        print(f"Error: invalid --start datetime '{args.start}'")
        return 1

    days = getattr(args, "days", 7)
    if days < 1:
        print("Error: --days must be at least 1")
        return 1

    end = start + timedelta(days=days)
    s = summarize(expr, start, end)

    print(f"Expression : {s.expression}")
    print(f"Window     : {s.window_start.isoformat()} -> {s.window_end.isoformat()}")
    print(f"Total runs : {s.total_runs}")
    print(f"Per day    : {s.runs_per_day}")
    print(f"Per hour   : {s.runs_per_hour}")
    print(f"Busiest hr : {s.busiest_hour:02d}:00  ({s.busiest_hour_count} runs)")
    print(f"Quietest hr: {s.quietest_hour:02d}:00  ({s.quietest_hour_count} runs)")
    print(f"First run  : {s.first_run.isoformat() if s.first_run else 'N/A'}")
    print(f"Last run   : {s.last_run.isoformat() if s.last_run else 'N/A'}")
    return 0
