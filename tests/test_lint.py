"""Tests for cronscope.lint."""

import pytest
from cronscope.lint import lint, LintResult


def test_lint_returns_lint_result():
    result = lint("* * * * *")
    assert isinstance(result, LintResult)


def test_valid_expression_has_no_errors():
    result = lint("0 9 * * 1-5")
    assert result.errors == []


def test_invalid_expression_reports_error():
    result = lint("99 * * * *")
    assert not result.ok
    assert len(result.errors) == 1


def test_ok_is_true_for_valid_expression():
    result = lint("*/5 * * * *")
    assert result.ok is True


def test_ok_is_false_for_invalid_expression():
    result = lint("bad expression")
    assert result.ok is False


def test_dom_and_dow_conflict_warning():
    result = lint("0 12 15 * 1")
    assert any("day-of-month" in w and "day-of-week" in w for w in result.warnings)


def test_no_dom_dow_warning_when_only_dom_set():
    result = lint("0 12 15 * *")
    assert not any("day-of-month" in w and "day-of-week" in w for w in result.warnings)


def test_no_dom_dow_warning_when_only_dow_set():
    result = lint("0 12 * * 1")
    assert not any("day-of-month" in w and "day-of-week" in w for w in result.warnings)


def test_leap_day_warning():
    result = lint("0 0 29 2 *")
    assert any("leap" in w.lower() for w in result.warnings)


def test_no_leap_day_warning_for_other_months():
    result = lint("0 0 29 3 *")
    assert not any("leap" in w.lower() for w in result.warnings)


def test_day_31_in_short_month_warning():
    result = lint("0 0 31 4 *")
    assert any("31" in w and "never" in w.lower() for w in result.warnings)


def test_day_31_in_long_month_no_warning():
    result = lint("0 0 31 1 *")
    assert not any("31" in w and "never" in w.lower() for w in result.warnings)


def test_step_equals_modulus_warning_minute():
    result = lint("*/60 * * * *")
    assert any("minute" in w.lower() for w in result.warnings)


def test_step_equals_modulus_warning_hour():
    result = lint("0 */24 * * *")
    assert any("hour" in w.lower() for w in result.warnings)


def test_normal_step_no_warning():
    result = lint("*/15 * * * *")
    assert not any("step" in w.lower() or ">=" in w for w in result.warnings)


def test_expression_stored_in_result():
    expr = "30 8 * * 1-5"
    result = lint(expr)
    assert result.expression == expr
