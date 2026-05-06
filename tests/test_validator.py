"""Tests for cronscope.validator."""

import pytest

from cronscope.validator import validate, ValidationResult


def test_valid_wildcard_expression():
    result = validate("* * * * *")
    assert result.valid is True
    assert result.errors == []


def test_valid_specific_expression():
    result = validate("30 9 * * 1")
    assert result.valid is True
    assert result.errors == []


def test_invalid_minute_out_of_range():
    result = validate("60 * * * *")
    assert result.valid is False
    assert len(result.errors) == 1
    assert "minute" in result.errors[0].lower() or "60" in result.errors[0]


def test_invalid_hour_out_of_range():
    result = validate("0 25 * * *")
    assert result.valid is False
    assert result.errors


def test_invalid_too_few_fields():
    result = validate("* * *")
    assert result.valid is False
    assert result.errors


def test_invalid_empty_expression():
    result = validate("")
    assert result.valid is False
    assert "empty" in result.errors[0].lower()


def test_invalid_whitespace_only():
    result = validate("   ")
    assert result.valid is False


def test_valid_step_expression():
    result = validate("*/5 * * * *")
    assert result.valid is True


def test_valid_range_expression():
    result = validate("0 9-17 * * 1-5")
    assert result.valid is True


def test_warning_feb_31():
    result = validate("0 0 31 2 *")
    assert result.valid is True
    assert any("February" in w for w in result.warnings)


def test_warning_dom_and_dow_both_set():
    result = validate("0 12 15 * 3")
    assert result.valid is True
    assert any("day-of-month" in w and "day-of-week" in w for w in result.warnings)


def test_no_warning_when_only_dom_set():
    result = validate("0 12 15 * *")
    assert result.valid is True
    assert not any("day-of-week" in w for w in result.warnings)


def test_bool_truthy_for_valid():
    result = validate("* * * * *")
    assert bool(result) is True


def test_bool_falsy_for_invalid():
    result = validate("99 * * * *")
    assert bool(result) is False
