"""Generate ASCII heatmap of cron schedule activity by hour and weekday."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict

from cronscope.scheduler import iter_runs
from cronscope.parser import CronExpression

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
SHADES = [" ", "░", "▒", "▓", "█"]


@dataclass
class HeatmapData:
    """Holds raw counts and rendered grid for a schedule heatmap."""
    counts: Dict[tuple, int] = field(default_factory=dict)  # (weekday, hour) -> count
    max_count: int = 0
    total_runs: int = 0


def _build_counts(expr: CronExpression, start: datetime, n: int) -> HeatmapData:
    data = HeatmapData()
    for dt in iter_runs(expr, start=start, count=n):
        key = (dt.weekday(), dt.hour)
        data.counts[key] = data.counts.get(key, 0) + 1
        data.total_runs += 1
    data.max_count = max(data.counts.values(), default=0)
    return data


def _shade(count: int, max_count: int) -> str:
    if max_count == 0 or count == 0:
        return SHADES[0]
    idx = max(1, round(count / max_count * (len(SHADES) - 1)))
    return SHADES[idx]


def render_heatmap(expr: CronExpression, start: datetime, n: int = 500) -> str:
    """Return a multi-line ASCII heatmap string (weekday x hour grid)."""
    data = _build_counts(expr, start, n)

    header = "     " + "".join(f"{h:2} " for h in range(24))
    lines = [header]

    for wd_idx, day_name in enumerate(DAYS):
        row = f"{day_name}  "
        for hour in range(24):
            count = data.counts.get((wd_idx, hour), 0)
            shade = _shade(count, data.max_count)
            row += f" {shade} "
        lines.append(row)

    lines.append(f"\nTotal runs sampled: {data.total_runs}  |  Peak cell: {data.max_count}")
    return "\n".join(lines)
