"""Summarize statistics about a cron schedule over a time window."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

from cronscope.scheduler import iter_runs
from cronscope.parser import CronExpression


@dataclass
class ScheduleSummary:
    expression: str
    window_start: datetime
    window_end: datetime
    total_runs: int
    runs_per_day: float
    runs_per_hour: float
    busiest_hour: int          # 0-23
    busiest_hour_count: int
    quietest_hour: int         # 0-23
    quietest_hour_count: int
    first_run: datetime | None
    last_run: datetime | None


def _hour_histogram(runs: List[datetime]) -> dict[int, int]:
    hist: dict[int, int] = {h: 0 for h in range(24)}
    for dt in runs:
        hist[dt.hour] += 1
    return hist


def summarize(
    expr: CronExpression,
    start: datetime,
    end: datetime,
) -> ScheduleSummary:
    """Compute a statistical summary of *expr* between *start* and *end*."""
    if end <= start:
        raise ValueError("end must be after start")

    runs: List[datetime] = []
    for dt in iter_runs(expr, start):
        if dt >= end:
            break
        runs.append(dt)

    total = len(runs)
    window_seconds = (end - start).total_seconds()
    window_hours = window_seconds / 3600
    window_days = window_seconds / 86400

    runs_per_hour = total / window_hours if window_hours else 0.0
    runs_per_day = total / window_days if window_days else 0.0

    hist = _hour_histogram(runs)
    busiest_hour = max(hist, key=lambda h: hist[h])
    quietest_hour = min(hist, key=lambda h: hist[h])

    return ScheduleSummary(
        expression=f"{expr.minute} {expr.hour} {expr.dom} {expr.month} {expr.dow}",
        window_start=start,
        window_end=end,
        total_runs=total,
        runs_per_day=round(runs_per_day, 2),
        runs_per_hour=round(runs_per_hour, 4),
        busiest_hour=busiest_hour,
        busiest_hour_count=hist[busiest_hour],
        quietest_hour=quietest_hour,
        quietest_hour_count=hist[quietest_hour],
        first_run=runs[0] if runs else None,
        last_run=runs[-1] if runs else None,
    )
