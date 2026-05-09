"""Monthly calendar view showing cron fire times for a given month."""

from __future__ import annotations

import calendar
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List

from cronscope.scheduler import iter_runs
from cronscope.parser import CronExpression


@dataclass
class CalendarView:
    year: int
    month: int
    expression: str
    # day -> list of HH:MM strings
    fire_times: Dict[int, List[str]] = field(default_factory=dict)


def _month_bounds(year: int, month: int):
    """Return (start, end) datetimes covering the full month (UTC)."""
    _, last_day = calendar.monthrange(year, month)
    start = datetime(year, month, 1, 0, 0, tzinfo=timezone.utc)
    end = datetime(year, month, last_day, 23, 59, tzinfo=timezone.utc)
    return start, end


def build_calendar_view(
    expr: CronExpression,
    year: int,
    month: int,
    max_runs: int = 5000,
) -> CalendarView:
    """Collect all fire times within *month* and group them by day."""
    start, end = _month_bounds(year, month)
    view = CalendarView(year=year, month=month, expression=str(expr))

    for run in iter_runs(expr, start=start, count=max_runs):
        if run > end:
            break
        day = run.day
        hhmm = run.strftime("%H:%M")
        view.fire_times.setdefault(day, []).append(hhmm)

    return view


def render_calendar(view: CalendarView, max_times_per_cell: int = 3) -> str:
    """Render a text calendar grid annotated with fire counts / times."""
    lines: List[str] = []
    month_name = calendar.month_name[view.month]
    header = f"  {month_name} {view.year}  |  {view.expression}"
    lines.append(header)
    lines.append("-" * max(len(header), 55))
    lines.append(" Mo  Tu  We  Th  Fr  Sa  Su")

    cal = calendar.monthcalendar(view.year, view.month)
    for week in cal:
        day_cells = []
        for day in week:
            if day == 0:
                day_cells.append("    ")
            else:
                count = len(view.fire_times.get(day, []))
                day_cells.append(f"{day:2d}({'*' if count else ' '}{min(count, 99):1d})" if count else f"{day:2d}   ")
        lines.append(" ".join(day_cells))

    # Detail block
    lines.append("")
    lines.append("Fire times by day:")
    for day in sorted(view.fire_times):
        times = view.fire_times[day]
        shown = ", ".join(times[:max_times_per_cell])
        extra = f" (+{len(times) - max_times_per_cell} more)" if len(times) > max_times_per_cell else ""
        lines.append(f"  {day:2d}: {shown}{extra}")

    if not view.fire_times:
        lines.append("  (no runs scheduled)")

    return "\n".join(lines)
