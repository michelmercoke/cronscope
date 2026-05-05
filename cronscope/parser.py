"""Cron expression parser and validator."""

from dataclasses import dataclass
from typing import Optional

CRON_FIELDS = ["minute", "hour", "day", "month", "weekday"]
CRON_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day": (1, 31),
    "month": (1, 12),
    "weekday": (0, 6),
}
MONTH_ALIASES = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}
WEEKDAY_ALIASES = {
    "sun": 0, "mon": 1, "tue": 2, "wed": 3,
    "thu": 4, "fri": 5, "sat": 6,
}


@dataclass
class CronExpression:
    minute: str
    hour: str
    day: str
    month: str
    weekday: str
    raw: str


class CronParseError(ValueError):
    pass


def _resolve_alias(value: str, field: str) -> str:
    if field == "month":
        return str(MONTH_ALIASES.get(value.lower(), value))
    if field == "weekday":
        return str(WEEKDAY_ALIASES.get(value.lower(), value))
    return value


def _validate_field(value: str, field: str) -> None:
    lo, hi = CRON_RANGES[field]
    if value == "*":
        return
    parts = value.split(",")
    for part in parts:
        step = None
        if "/" in part:
            part, step_str = part.split("/", 1)
            if not step_str.isdigit():
                raise CronParseError(f"Invalid step in {field}: {step_str}")
            step = int(step_str)
            if step < 1:
                raise CronParseError(f"Step must be >= 1 in {field}")
        if "-" in part:
            start, end = part.split("-", 1)
            start = _resolve_alias(start, field)
            end = _resolve_alias(end, field)
            if not start.isdigit() or not end.isdigit():
                raise CronParseError(f"Invalid range in {field}: {part}")
            if not (lo <= int(start) <= hi) or not (lo <= int(end) <= hi):
                raise CronParseError(f"Range out of bounds in {field}: {part}")
        elif part != "*":
            part = _resolve_alias(part, field)
            if not part.isdigit():
                raise CronParseError(f"Invalid value in {field}: {part}")
            if not (lo <= int(part) <= hi):
                raise CronParseError(f"Value {part} out of range [{lo},{hi}] in {field}")


def parse(expression: str) -> CronExpression:
    """Parse and validate a cron expression string."""
    parts = expression.strip().split()
    if len(parts) != 5:
        raise CronParseError(
            f"Expected 5 fields, got {len(parts)}: '{expression}'"
        )
    fields = dict(zip(CRON_FIELDS, parts))
    for field, value in fields.items():
        _validate_field(value, field)
    return CronExpression(raw=expression, **fields)
