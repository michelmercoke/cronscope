"""Rank and score cron expressions by various criteria."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from cronscope.parser import parse, CronParseError
from cronscope.scheduler import next_runs
from cronscope.summarizer import summarize


@dataclass
class RankEntry:
    expression: str
    label: str
    runs_per_day: float
    score: float
    rank: int


def _score(runs_per_day: float) -> float:
    """Higher frequency = lower score (less resource-friendly)."""
    if runs_per_day <= 0:
        return 0.0
    # Normalize: 1 run/day = 1.0, 1440 runs/day = 0.0
    return max(0.0, 1.0 - (runs_per_day / 1440.0))


def rank(
    expressions: List[str],
    labels: List[str] | None = None,
    window_days: int = 7,
    count: int = 500,
) -> List[RankEntry]:
    """Rank a list of cron expressions by resource-friendliness.

    Returns entries sorted from most friendly (highest score) to least.
    """
    if labels is None:
        labels = [expr for expr in expressions]

    if len(labels) != len(expressions):
        raise ValueError("labels length must match expressions length")

    entries: List[RankEntry] = []
    for expr, label in zip(expressions, labels):
        try:
            parsed = parse(expr)
        except CronParseError:
            entries.append(RankEntry(expr, label, 0.0, 0.0, 0))
            continue

        summary = summarize(parsed, days=window_days, count=count)
        rpd = summary.runs_per_day
        score = _score(rpd)
        entries.append(RankEntry(expr, label, rpd, score, 0))

    entries.sort(key=lambda e: e.score, reverse=True)
    for i, entry in enumerate(entries, start=1):
        entry.rank = i

    return entries
