"""Detect and report overlapping cron schedules."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Tuple

from cronscope.parser import parse
from cronscope.scheduler import next_runs


@dataclass
class OverlapReport:
    expr_a: str
    expr_b: str
    overlapping_runs: List[datetime] = field(default_factory=list)
    total_a: int = 0
    total_b: int = 0

    @property
    def overlap_count(self) -> int:
        return len(self.overlapping_runs)

    @property
    def overlap_ratio_a(self) -> float:
        if self.total_a == 0:
            return 0.0
        return self.overlap_count / self.total_a

    @property
    def overlap_ratio_b(self) -> float:
        if self.total_b == 0:
            return 0.0
        return self.overlap_count / self.total_b


def find_overlaps(
    expr_a: str,
    expr_b: str,
    start: datetime | None = None,
    count: int = 100,
) -> OverlapReport:
    """Return an OverlapReport showing runs shared by both expressions."""
    if start is None:
        start = datetime.now().replace(second=0, microsecond=0)

    cron_a = parse(expr_a)
    cron_b = parse(expr_b)

    runs_a = next_runs(cron_a, start=start, count=count)
    runs_b = next_runs(cron_b, start=start, count=count)

    set_a = set(runs_a)
    set_b = set(runs_b)
    shared = sorted(set_a & set_b)

    return OverlapReport(
        expr_a=expr_a,
        expr_b=expr_b,
        overlapping_runs=shared,
        total_a=len(runs_a),
        total_b=len(runs_b),
    )
