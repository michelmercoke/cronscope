"""Compute next run times for a parsed cron expression."""

from datetime import datetime, timedelta
from typing import Iterator, List

from cronscope.parser import CronExpression


def _matches_field(value: str, current: int, lo: int, hi: int) -> bool:
    if value == "*":
        return True
    for part in value.split(","):
        step = 1
        if "/" in part:
            part, step_str = part.split("/", 1)
            step = int(step_str)
        if part == "*":
            candidates = range(lo, hi + 1, step)
            if current in candidates:
                return True
        elif "-" in part:
            start, end = map(int, part.split("-", 1))
            if current in range(start, end + 1, step):
                return True
        else:
            if int(part) == current and (current - lo) % step == 0:
                return True
    return False


def _matches(expr: CronExpression, dt: datetime) -> bool:
    return (
        _matches_field(expr.minute, dt.minute, 0, 59)
        and _matches_field(expr.hour, dt.hour, 0, 23)
        and _matches_field(expr.day, dt.day, 1, 31)
        and _matches_field(expr.month, dt.month, 1, 12)
        and _matches_field(expr.weekday, dt.weekday() % 7, 0, 6)
    )


def next_runs(
    expr: CronExpression,
    after: datetime | None = None,
    count: int = 10,
    max_iterations: int = 527_040,  # ~1 year of minutes
) -> List[datetime]:
    """Return the next `count` datetimes matching the cron expression."""
    start = (after or datetime.now()).replace(second=0, microsecond=0)
    current = start + timedelta(minutes=1)
    results: List[datetime] = []
    iterations = 0
    while len(results) < count and iterations < max_iterations:
        if _matches(expr, current):
            results.append(current)
        current += timedelta(minutes=1)
        iterations += 1
    return results


def iter_runs(
    expr: CronExpression,
    after: datetime | None = None,
) -> Iterator[datetime]:
    """Yield matching datetimes indefinitely."""
    start = (after or datetime.now()).replace(second=0, microsecond=0)
    current = start + timedelta(minutes=1)
    while True:
        if _matches(expr, current):
            yield current
        current += timedelta(minutes=1)
