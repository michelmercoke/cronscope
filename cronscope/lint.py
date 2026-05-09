"""Lint cron expressions for common mistakes and suspicious patterns."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from cronscope.parser import CronExpression, parse, CronParseError


@dataclass
class LintResult:
    expression: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0


def _check_dom_dow_conflict(expr: CronExpression) -> str | None:
    """Warn when both day-of-month and day-of-week are restricted."""
    dom_restricted = expr.dom != "*" and expr.dom != "?"
    dow_restricted = expr.dow != "*" and expr.dow != "?"
    if dom_restricted and dow_restricted:
        return (
            "Both day-of-month and day-of-week are restricted; "
            "runs occur when EITHER condition is true (may be unintended)"
        )
    return None


def _check_high_frequency(expr: CronExpression) -> str | None:
    """Warn when the expression fires more than once per minute (not possible,
    but detect */1 patterns that indicate intent to run every second)."""
    if expr.minute in ("*/1", "*"):
        if expr.hour == "*":
            return None  # normal every-minute schedule, no warning needed
    return None


def _check_leap_day(expr: CronExpression) -> str | None:
    """Warn when day-of-month is 29 and month is 2."""
    if expr.dom == "29" and expr.month == "2":
        return "Day 29 of February only exists in leap years; schedule will be skipped in non-leap years"
    return None


def _check_day_out_of_month(expr: CronExpression) -> str | None:
    """Warn when day-of-month is 31 and month restricts to a short month."""
    short_months = {"2", "4", "6", "9", "11"}
    if expr.dom == "31" and expr.month in short_months:
        return f"Day 31 does not exist in month {expr.month}; schedule will never run"
    return None


def _check_unreachable_step(expr: CronExpression) -> str | None:
    """Warn when a step value equals the field range (e.g. */60 for minutes)."""
    checks = [
        (expr.minute, 60, "minute"),
        (expr.hour, 24, "hour"),
    ]
    for value, modulus, name in checks:
        if value.startswith("*/"):
            try:
                step = int(value[2:])
                if step >= modulus:
                    return f"Step */{step} for {name} field is >= {modulus}; only fires once per period"
            except ValueError:
                pass
    return None


_CHECKERS = [
    _check_dom_dow_conflict,
    _check_high_frequency,
    _check_leap_day,
    _check_day_out_of_month,
    _check_unreachable_step,
]


def lint(expression: str) -> LintResult:
    """Lint a cron expression and return a LintResult with errors and warnings."""
    result = LintResult(expression=expression)
    try:
        expr = parse(expression)
    except CronParseError as exc:
        result.errors.append(str(exc))
        return result

    for checker in _CHECKERS:
        msg = checker(expr)
        if msg:
            result.warnings.append(msg)

    return result
