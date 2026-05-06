"""Formatting utilities for displaying cron schedule previews in the terminal."""

from datetime import datetime
from typing import List, Optional

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"
COLOR_CYAN = "\033[36m"
COLOR_GREEN = "\033[32m"
COLOR_YELLOW = "\033[33m"
COLOR_DIM = "\033[2m"


def format_datetime(dt: datetime) -> str:
    """Format a datetime object as a readable string."""
    return dt.strftime(TIME_FORMAT)


def format_relative(dt: datetime, now: Optional[datetime] = None) -> str:
    """Return a human-readable relative time string (e.g. 'in 5 minutes')."""
    if now is None:
        now = datetime.now()
    delta = dt - now
    total_seconds = int(delta.total_seconds())

    if total_seconds < 60:
        return f"in {total_seconds}s"
    elif total_seconds < 3600:
        minutes = total_seconds // 60
        return f"in {minutes}m"
    elif total_seconds < 86400:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        if minutes:
            return f"in {hours}h {minutes}m"
        return f"in {hours}h"
    else:
        days = total_seconds // 86400
        return f"in {days}d"


def format_schedule_table(
    expression: str,
    runs: List[datetime],
    now: Optional[datetime] = None,
    use_color: bool = True,
) -> str:
    """Render a formatted table of upcoming cron run times."""
    if now is None:
        now = datetime.now()

    def c(code: str, text: str) -> str:
        return f"{code}{text}{COLOR_RESET}" if use_color else text

    lines = []
    header = c(COLOR_BOLD, f"Upcoming runs for: ") + c(COLOR_CYAN, expression)
    lines.append(header)
    lines.append(c(COLOR_DIM, "-" * 42))

    for i, run in enumerate(runs, start=1):
        timestamp = format_datetime(run)
        relative = format_relative(run, now)
        index_str = c(COLOR_DIM, f"{i:>2}. ")
        time_str = c(COLOR_GREEN, timestamp)
        rel_str = c(COLOR_YELLOW, f"  ({relative})")
        lines.append(f"{index_str}{time_str}{rel_str}")

    return "\n".join(lines)
