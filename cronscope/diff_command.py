"""CLI sub-command handler for comparing two cron expressions."""

from __future__ import annotations

import sys
from datetime import datetime
from argparse import ArgumentParser, Namespace

from cronscope.differ import diff, format_diff
from cronscope.parser import CronParseError


def add_diff_subparser(subparsers) -> None:
    """Register the 'diff' sub-command onto an existing subparsers action."""
    p: ArgumentParser = subparsers.add_parser(
        "diff",
        help="Compare two cron expressions and show scheduling differences.",
    )
    p.add_argument("expr_a", metavar="EXPR_A", help="First cron expression (quoted).")
    p.add_argument("expr_b", metavar="EXPR_B", help="Second cron expression (quoted).")
    p.add_argument(
        "-n",
        "--count",
        type=int,
        default=20,
        metavar="N",
        help="Number of future slots to sample (default: 20).",
    )
    p.add_argument(
        "--start",
        metavar="YYYY-MM-DDTHH:MM",
        default=None,
        help="Start datetime for comparison window (ISO format, default: now).",
    )
    p.set_defaults(func=run_diff)


def run_diff(args: Namespace) -> int:
    """Execute the diff sub-command. Returns exit code."""
    start: datetime | None = None
    if args.start:
        try:
            start = datetime.fromisoformat(args.start)
        except ValueError:
            print(
                f"Error: invalid --start value '{args.start}'. "
                "Expected format: YYYY-MM-DDTHH:MM",
                file=sys.stderr,
            )
            return 1

    try:
        result = diff(
            args.expr_a,
            args.expr_b,
            start=start,
            count=args.count,
        )
    except CronParseError as exc:
        print(f"Error parsing cron expression: {exc}", file=sys.stderr)
        return 1

    print(format_diff(result))
    return 0
