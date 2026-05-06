"""Human-readable explanations for cron expressions."""

from cronscope.parser import CronExpression

_WEEKDAY_NAMES = [
    "Sunday", "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday"
]

_MONTH_NAMES = [
    "", "January", "February", "March", "April",
    "May", "June", "July", "August", "September",
    "October", "November", "December"
]


def _explain_field(value: str, unit: str, names: list[str] | None = None) -> str:
    """Return a human-readable description for a single cron field."""
    if value == "*":
        return f"every {unit}"

    if value.startswith("*/"):
        step = value[2:]
        return f"every {step} {unit}s"

    if "-" in value and "/" in value:
        range_part, step = value.split("/")
        start, end = range_part.split("-")
        if names:
            start = names[int(start)] if int(start) < len(names) else start
            end = names[int(end)] if int(end) < len(names) else end
        return f"every {step} {unit}s from {start} through {end}"

    if "-" in value:
        start, end = value.split("-")
        if names:
            start = names[int(start)] if int(start) < len(names) else start
            end = names[int(end)] if int(end) < len(names) else end
        return f"{unit}s {start} through {end}"

    if "," in value:
        parts = value.split(",")
        if names:
            parts = [names[int(p)] if int(p) < len(names) else p for p in parts]
        return f"{unit}s " + ", ".join(parts)

    if names and value.isdigit() and int(value) < len(names):
        return f"{unit} {names[int(value)]}"

    return f"{unit} {value}"


def explain(expr: CronExpression) -> str:
    """Return a full human-readable explanation of a CronExpression."""
    minute = _explain_field(expr.minute, "minute")
    hour = _explain_field(expr.hour, "hour")
    dom = _explain_field(expr.dom, "day-of-month")
    month = _explain_field(expr.month, "month", _MONTH_NAMES)
    dow = _explain_field(expr.dow, "weekday", _WEEKDAY_NAMES)

    parts = []

    if expr.minute == "*" and expr.hour == "*":
        parts.append("every minute")
    elif expr.minute.startswith("*/") and expr.hour == "*":
        parts.append(minute)
    else:
        parts.append(f"at {minute} past {hour}")

    if expr.dom != "*":
        parts.append(f"on {dom}")

    if expr.month != "*":
        parts.append(f"in {month}")

    if expr.dow != "*":
        parts.append(f"on {dow}")

    return ", ".join(parts)
