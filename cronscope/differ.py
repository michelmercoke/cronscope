"""Compare two cron expressions and summarize their scheduling differences."""

from dataclasses import dataclass
from typing import List, Tuple
from datetime import datetime

from cronscope.parser import parse, CronExpression
from cronscope.scheduler import next_runs


@dataclass
class DiffResult:
    expr_a: str
    expr_b: str
    only_in_a: List[datetime]
    only_in_b: List[datetime]
    common: List[datetime]

    @property
    def overlap_count(self) -> int:
        return len(self.common)

    @property
    def divergence_count(self) -> int:
        return len(self.only_in_a) + len(self.only_in_b)


def _runs_set(expr: CronExpression, start: datetime, count: int) -> List[datetime]:
    """Return next *count* run datetimes as a list."""
    return list(next_runs(expr, start=start, count=count))


def diff(
    expr_a: str,
    expr_b: str,
    start: datetime | None = None,
    count: int = 20,
) -> DiffResult:
    """Compare two cron expressions over the next *count* evaluation slots.

    Returns a DiffResult describing which datetimes are shared, exclusive to A,
    or exclusive to B within the sampled window.
    """
    if start is None:
        start = datetime.now().replace(second=0, microsecond=0)

    cron_a = parse(expr_a)
    cron_b = parse(expr_b)

    runs_a = _runs_set(cron_a, start, count)
    runs_b = _runs_set(cron_b, start, count)

    set_a = set(runs_a)
    set_b = set(runs_b)

    common = sorted(set_a & set_b)
    only_in_a = sorted(set_a - set_b)
    only_in_b = sorted(set_b - set_a)

    return DiffResult(
        expr_a=expr_a,
        expr_b=expr_b,
        only_in_a=only_in_a,
        only_in_b=only_in_b,
        common=common,
    )


def format_diff(result: DiffResult) -> str:
    """Render a DiffResult as a human-readable string."""
    lines = [
        f"Comparing: [{result.expr_a}]  vs  [{result.expr_b}]",
        f"  Shared runs   : {result.overlap_count}",
        f"  Only in first : {len(result.only_in_a)}",
        f"  Only in second: {len(result.only_in_b)}",
    ]
    if result.only_in_a:
        lines.append("  Exclusive to first:")
        for dt in result.only_in_a[:5]:
            lines.append(f"    - {dt.strftime('%Y-%m-%d %H:%M')}")
    if result.only_in_b:
        lines.append("  Exclusive to second:")
        for dt in result.only_in_b[:5]:
            lines.append(f"    - {dt.strftime('%Y-%m-%d %H:%M')}")
    return "\n".join(lines)
