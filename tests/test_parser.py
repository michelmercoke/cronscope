"""Tests for cronscope.parser."""

import pytest
from cronscope.parser import CronExpression, CronParseError, parse


def test_parse_all_wildcards():
    expr = parse("* * * * *")
    assert isinstance(expr, CronExpression)
    assert expr.minute == "*"
    assert expr.raw == "* * * * *"


def test_parse_specific_values():
    expr = parse("30 9 1 6 1")
    assert expr.minute == "30"
    assert expr.hour == "9"
    assert expr.day == "1"
    assert expr.month == "6"
    assert expr.weekday == "1"


def test_parse_ranges():
    expr = parse("0-30 8-18 * * 1-5")
    assert expr.minute == "0-30"
    assert expr.weekday == "1-5"


def test_parse_step():
    expr = parse("*/5 * * * *")
    assert expr.minute == "*/5"


def test_parse_list():
    expr = parse("0,15,30,45 * * * *")
    assert expr.minute == "0,15,30,45"


def test_parse_month_alias():
    expr = parse("0 0 1 jan *")
    assert expr.month == "jan"


def test_invalid_field_count_raises():
    with pytest.raises(CronParseError, match="Expected 5 fields"):
        parse("* * * *")


def test_invalid_minute_range_raises():
    with pytest.raises(CronParseError):
        parse("60 * * * *")


def test_invalid_hour_raises():
    with pytest.raises(CronParseError):
        parse("0 24 * * *")


def test_invalid_step_raises():
    with pytest.raises(CronParseError):
        parse("*/0 * * * *")


def test_invalid_non_numeric_raises():
    with pytest.raises(CronParseError):
        parse("abc * * * *")
