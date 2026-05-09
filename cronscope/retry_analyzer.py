"""Analyze cron expressions to suggest retry-safe scheduling windows."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List

from cronscope.parser import parse
from cronscope.scheduler import next_runs


@dataclass
class RetryWindow:
    """A safe window between two consecutive runs."""

    start: datetime
    end: datetime
    gap_seconds: int
    safe_retries: int  # how many retries fit assuming 60s each


@dataclass
class RetryReport:
    """Full retry analysis report for a cron expression."""

    expression: str
    min_gap_seconds: int
    max_gap_seconds: int
    avg_gap_seconds: float
    windows: List[RetryWindow] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def _gap_seconds(a: datetime, b: datetime) -> int:
    return int((b - a).total_seconds())


def analyze_retries(
    expression: str,
    start: datetime | None = None,
    count: int = 48,
    retry_duration_seconds: int = 60,
) -> RetryReport:
    """Analyze gaps between scheduled runs and compute retry safety.

    Args:
        expression: A valid cron expression string.
        start: Start datetime for analysis window (defaults to now).
        count: Number of upcoming runs to examine.
        retry_duration_seconds: Assumed duration of a single retry attempt.

    Returns:
        A RetryReport describing gap statistics and per-window retry capacity.
    """
    if start is None:
        start = datetime.now().replace(second=0, microsecond=0)

    expr = parse(expression)
    runs = next_runs(expr, start=start, count=count)

    if len(runs) < 2:
        return RetryReport(
            expression=expression,
            min_gap_seconds=0,
            max_gap_seconds=0,
            avg_gap_seconds=0.0,
            warnings=["Not enough runs to compute gaps."],
        )

    windows: list[RetryWindow] = []
    gaps: list[int] = []

    for a, b in zip(runs, runs[1:]):
        gap = _gap_seconds(a, b)
        safe = max(0, (gap - retry_duration_seconds) // retry_duration_seconds)
        windows.append(RetryWindow(start=a, end=b, gap_seconds=gap, safe_retries=safe))
        gaps.append(gap)

    warnings: list[str] = []
    min_gap = min(gaps)
    if min_gap < retry_duration_seconds * 2:
        warnings.append(
            f"Minimum gap ({min_gap}s) leaves little room for retries; "
            "consider a less frequent schedule."
        )

    return RetryReport(
        expression=expression,
        min_gap_seconds=min_gap,
        max_gap_seconds=max(gaps),
        avg_gap_seconds=sum(gaps) / len(gaps),
        windows=windows,
        warnings=warnings,
    )
