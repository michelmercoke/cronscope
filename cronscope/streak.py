"""Streak analyzer: find consecutive day-runs and gaps in a cron schedule."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List

from cronscope.scheduler import next_runs
from cronscope.parser import parse


@dataclass
class StreakReport:
    expression: str
    days_analyzed: int
    longest_streak: int          # consecutive days with at least one run
    longest_gap: int             # consecutive days with zero runs
    active_days: int             # days that had at least one run
    inactive_days: int           # days with no run
    streaks: List[int] = field(default_factory=list)   # lengths of every streak
    gaps: List[int] = field(default_factory=list)      # lengths of every gap


def _days_with_runs(expression: str, start: datetime, days: int) -> List[bool]:
    """Return a boolean list, one entry per day, True if ≥1 run occurred."""
    end = start + timedelta(days=days)
    runs = next_runs(parse(expression), start=start, count=days * 1500)
    active: set[int] = set()
    for r in runs:
        if r >= end:
            break
        offset = (r.date() - start.date()).days
        active.add(offset)
    return [i in active for i in range(days)]


def analyze_streaks(expression: str, start: datetime, days: int = 30) -> StreakReport:
    """Analyze consecutive active/inactive days for *expression*."""
    day_flags = _days_with_runs(expression, start, days)

    streaks: List[int] = []
    gaps: List[int] = []
    current_streak = 0
    current_gap = 0

    for active in day_flags:
        if active:
            if current_gap > 0:
                gaps.append(current_gap)
                current_gap = 0
            current_streak += 1
        else:
            if current_streak > 0:
                streaks.append(current_streak)
                current_streak = 0
            current_gap += 1

    if current_streak > 0:
        streaks.append(current_streak)
    if current_gap > 0:
        gaps.append(current_gap)

    active_days = sum(day_flags)
    return StreakReport(
        expression=expression,
        days_analyzed=days,
        longest_streak=max(streaks, default=0),
        longest_gap=max(gaps, default=0),
        active_days=active_days,
        inactive_days=days - active_days,
        streaks=streaks,
        gaps=gaps,
    )
