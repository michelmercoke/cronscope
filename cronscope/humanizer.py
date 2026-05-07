"""Human-readable summaries of cron schedule frequency."""

from cronscope.parser import CronExpression


def _field_is_wildcard(field: str) -> bool:
    return field == "*"


def _field_is_step(field: str) -> bool:
    return "/" in field


def _field_step_value(field: str) -> int:
    """Return the step value from a */N expression."""
    return int(field.split("/")[1])


def _field_is_single(field: str) -> bool:
    return field.isdigit()


def humanize(expr: CronExpression) -> str:
    """Return a plain-English frequency description for a cron expression."""
    minute = expr.minute
    hour = expr.hour
    dom = expr.dom
    month = expr.month
    dow = expr.dow

    _DOW_NAMES = {
        "0": "Sunday", "1": "Monday", "2": "Tuesday", "3": "Wednesday",
        "4": "Thursday", "5": "Friday", "6": "Saturday",
    }

    _MONTH_NAMES = {
        "1": "January", "2": "February", "3": "March", "4": "April",
        "5": "May", "6": "June", "7": "July", "8": "August",
        "9": "September", "10": "October", "11": "November", "12": "December",
    }

    parts = []

    # Minute
    if _field_is_wildcard(minute):
        parts.append("every minute")
    elif _field_is_step(minute):
        n = _field_step_value(minute)
        parts.append(f"every {n} minutes")
    elif _field_is_single(minute):
        parts.append(f"at minute {minute}")

    # Hour
    if not _field_is_wildcard(hour):
        if _field_is_step(hour):
            n = _field_step_value(hour)
            parts.append(f"every {n} hours")
        elif _field_is_single(hour):
            h = int(hour)
            ampm = "AM" if h < 12 else "PM"
            h12 = h % 12 or 12
            parts.append(f"at {h12}:00 {ampm}")

    # Day of month
    if not _field_is_wildcard(dom) and _field_is_single(dom):
        parts.append(f"on day {dom} of the month")

    # Month
    if not _field_is_wildcard(month) and _field_is_single(month):
        name = _MONTH_NAMES.get(month, month)
        parts.append(f"in {name}")

    # Day of week
    if not _field_is_wildcard(dow) and _field_is_single(dow):
        name = _DOW_NAMES.get(dow, dow)
        parts.append(f"on {name}s")

    if not parts:
        return "every minute"

    return ", ".join(parts)
