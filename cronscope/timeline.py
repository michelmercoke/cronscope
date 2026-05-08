"""Timeline rendering: display cron runs as an ASCII timeline chart."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

from cronscope.scheduler import next_runs
from cronscope.parser import CronExpression


@dataclass
class TimelineData:
    start: datetime
    end: datetime
    runs: List[datetime]
    width: int


def _build_timeline(runs: List[datetime], start: datetime, end: datetime, width: int) -> str:
    """Return a single-line ASCII bar with markers for each run."""
    bar = ["-"] * width
    total_seconds = (end - start).total_seconds()
    if total_seconds <= 0:
        return "".join(bar)

    for run in runs:
        offset = (run - start).total_seconds()
        pos = int(offset / total_seconds * (width - 1))
        pos = max(0, min(width - 1, pos))
        bar[pos] = "*"

    return "".join(bar)


def render_timeline(
    expr: CronExpression,
    start: datetime,
    hours: int = 24,
    width: int = 72,
    count: int = 500,
) -> str:
    """Render a textual timeline of cron runs over a window of *hours* hours.

    Returns a multi-line string suitable for terminal output.
    """
    end = start + timedelta(hours=hours)
    all_runs = next_runs(expr, start, count)
    window_runs = [r for r in all_runs if start <= r < end]

    bar = _build_timeline(window_runs, start, end, width)

    lines = [
        f"Timeline: {start.strftime('%Y-%m-%d %H:%M')} → {end.strftime('%Y-%m-%d %H:%M')} ({hours}h window)",
        f"Runs shown : {len(window_runs)}",
        f"|{bar}|",
        f" {start.strftime('%H:%M'):^{width//2}}{end.strftime('%H:%M'):>{width//2}} ",
    ]
    return "\n".join(lines)


def collect_timeline_data(
    expr: CronExpression,
    start: datetime,
    hours: int = 24,
    width: int = 72,
    count: int = 500,
) -> TimelineData:
    """Return structured timeline data (useful for testing)."""
    end = start + timedelta(hours=hours)
    all_runs = next_runs(expr, start, count)
    window_runs = [r for r in all_runs if start <= r < end]
    return TimelineData(start=start, end=end, runs=window_runs, width=width)
