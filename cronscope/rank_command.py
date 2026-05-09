"""CLI subcommand: rank multiple cron expressions by resource usage."""

from __future__ import annotations

import argparse
from typing import List

from cronscope.ranker import rank, RankEntry
from cronscope.parser import CronParseError


def add_rank_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "rank",
        help="Rank cron expressions by resource-friendliness",
    )
    p.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPR",
        help="One or more cron expressions to rank",
    )
    p.add_argument(
        "--labels",
        nargs="+",
        metavar="LABEL",
        default=None,
        help="Optional labels for each expression (same order)",
    )
    p.add_argument(
        "--days",
        type=int,
        default=7,
        metavar="N",
        help="Window of days to analyse (default: 7)",
    )
    p.add_argument(
        "--count",
        type=int,
        default=500,
        metavar="N",
        help="Max runs to sample per expression (default: 500)",
    )
    p.set_defaults(func=run_rank)


def _format_table(entries: List[RankEntry]) -> str:
    header = f"{'Rank':>4}  {'Score':>6}  {'Runs/day':>9}  {'Label'}"
    sep = "-" * len(header)
    rows = [header, sep]
    for e in entries:
        rows.append(
            f"{e.rank:>4}  {e.score:>6.3f}  {e.runs_per_day:>9.2f}  {e.label}"
        )
    return "\n".join(rows)


def run_rank(args: argparse.Namespace) -> int:
    labels = args.labels
    if labels is not None and len(labels) != len(args.expressions):
        print("Error: --labels count must match number of expressions")
        return 1

    try:
        entries = rank(
            args.expressions,
            labels=labels,
            window_days=args.days,
            count=args.count,
        )
    except (ValueError, CronParseError) as exc:
        print(f"Error: {exc}")
        return 1

    print(_format_table(entries))
    return 0
