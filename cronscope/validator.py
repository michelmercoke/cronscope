"""Validation helpers for cron expressions with human-readable error messages."""

from dataclasses import dataclass
from typing import List, Optional

from cronscope.parser import CronParseError, parse


@dataclass
class ValidationResult:
    valid: bool
    expression: str
    errors: List[str]
    warnings: List[str]

    def __bool__(self) -> bool:
        return self.valid


_FIELD_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day_of_month": (1, 31),
    "month": (1, 12),
    "day_of_week": (0, 7),
}

_SUSPICIOUS_PATTERNS = [
    ("0 0 31 2 *", "February never has 31 days"),
    ("0 0 30 2 *", "February rarely has 30 days"),
    ("0 0 31 4 *", "April never has 31 days"),
    ("0 0 31 6 *", "June never has 31 days"),
    ("0 0 31 9 *", "September never has 31 days"),
    ("0 0 31 11 *", "November never has 31 days"),
]

# Common named presets that users may want to reference
_PRESETS = {
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@monthly": "0 0 1 * *",
    "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@hourly": "0 * * * *",
}


def _check_warnings(expression: str) -> List[str]:
    warnings = []
    parts = expression.strip().split()
    if len(parts) != 5:
        return warnings

    dom, month = parts[2], parts[3]
    if dom not in ("*", "?") and month not in ("*", "?"):
        for pattern, msg in _SUSPICIOUS_PATTERNS:
            pat_parts = pattern.split()
            if parts[2] == pat_parts[2] and parts[3] == pat_parts[3]:
                warnings.append(msg)

    # Warn if both DOM and DOW are specified (non-wildcard)
    if parts[2] not in ("*", "?") and parts[4] not in ("*", "?"):
        warnings.append(
            "Both day-of-month and day-of-week are set; "
            "matches will occur when EITHER condition is true"
        )

    return warnings


def expand_preset(expression: str) -> str:
    """Expand a named cron preset (e.g. ``@daily``) to its five-field equivalent.

    Returns the original expression unchanged if it is not a recognised preset.

    >>> expand_preset("@daily")
    '0 0 * * *'
    >>> expand_preset("0 * * * *")
    '0 * * * *'
    """
    return _PRESETS.get(expression.strip(), expression)


def validate(expression: str) -> ValidationResult:
    """Validate a cron expression and return a structured result.

    Named presets such as ``@daily`` are expanded before validation so they
    are accepted as valid input.
    """
    errors: List[str] = []
    warnings: List[str] = []

    if not expression or not expression.strip():
        return ValidationResult(
            valid=False,
            expression=expression,
            errors=["Expression must not be empty"],
            warnings=[],
        )

    # Expand any named preset before parsing
    expanded = expand_preset(expression)

    try:
        parse(expanded)
    except CronParseError as exc:
        errors.append(str(exc))
        return ValidationResult(
            valid=False, expression=expression, errors=errors, warnings=[]
        )

    warnings = _check_warnings(expanded)

    return ValidationResult(
        valid=True, expression=expression, errors=[], warnings=warnings
    )
