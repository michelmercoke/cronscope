"""Command-line interface for cronscope."""

import argparse
import sys
from datetime import datetime

from cronscope.formatter import format_schedule_table
from cronscope.parser import CronParseError, parse
from cronscope.scheduler import next_runs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cronscope",
        description="Visualize and validate cron expressions with next-run previews.",
    )
    parser.add_argument(
        "expression",
        help="Cron expression to evaluate (e.g. '*/5 * * * *')",
    )
    parser.add_argument(
        "-n",
        "--count",
        type=int,
        default=5,
        metavar="N",
        help="Number of upcoming runs to display (default: 5)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Only validate the expression without showing runs",
    )
    return parser


def _validate_count(count: int) -> None:
    """Raise SystemExit if the run count is not a positive integer."""
    if count < 1:
        print("Error: --count must be a positive integer (>= 1)", file=sys.stderr)
        sys.exit(1)


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        cron = parse(args.expression)
    except CronParseError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.validate:
        print(f"Valid cron expression: {args.expression}")
        return 0

    _validate_count(args.count)

    now = datetime.now().replace(second=0, microsecond=0)
    runs = next_runs(cron, count=args.count, start=now)

    output = format_schedule_table(
        expression=args.expression,
        runs=runs,
        now=now,
        use_color=not args.no_color,
    )
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
