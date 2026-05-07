"""CLI subcommand: heatmap — render an ASCII activity heatmap for a cron expression."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

from cronscope.parser import parse, CronParseError
from cronscope.heatmap import render_heatmap


def add_heatmap_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "heatmap",
        help="Render an ASCII heatmap of schedule activity by weekday and hour.",
    )
    p.add_argument("expression", help="Cron expression (5 fields, quoted).")
    p.add_argument(
        "--start",
        default=None,
        metavar="ISO",
        help="Start datetime in ISO 8601 format (default: now).",
    )
    p.add_argument(
        "--samples",
        type=int,
        default=500,
        metavar="N",
        help="Number of upcoming runs to sample (default: 500).",
    )


def run_heatmap(args: argparse.Namespace) -> int:
    """Execute the heatmap subcommand. Returns exit code."""
    try:
        expr = parse(args.expression)
    except CronParseError as exc:
        print(f"Error: invalid cron expression — {exc}", file=sys.stderr)
        return 1

    if args.start:
        try:
            start = datetime.fromisoformat(args.start)
        except ValueError:
            print(f"Error: invalid --start datetime '{args.start}'", file=sys.stderr)
            return 1
    else:
        start = datetime.now().replace(second=0, microsecond=0)

    if args.samples < 1:
        print("Error: --samples must be at least 1.", file=sys.stderr)
        return 1

    print(f"Heatmap for: {args.expression}")
    print(f"Sampled {args.samples} runs from {start.isoformat()}\n")
    print(render_heatmap(expr, start=start, n=args.samples))
    return 0
