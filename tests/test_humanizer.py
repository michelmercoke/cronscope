"""Tests for cronscope.humanizer."""

import pytest
from cronscope.parser import parse
from cronscope.humanizer import humanize


def test_every_minute():
    expr = parse("* * * * *")
    assert humanize(expr) == "every minute"


def test_every_5_minutes():
    expr = parse("*/5 * * * *")
    assert "every 5 minutes" in humanize(expr)


def test_every_15_minutes():
    expr = parse("*/15 * * * *")
    assert "every 15 minutes" in humanize(expr)


def test_specific_minute_wildcard_hour():
    expr = parse("30 * * * *")
    result = humanize(expr)
    assert "minute 30" in result


def test_specific_hour_and_minute():
    expr = parse("0 9 * * *")
    result = humanize(expr)
    assert "9:00 AM" in result
    assert "minute 0" in result


def test_midnight():
    expr = parse("0 0 * * *")
    result = humanize(expr)
    assert "12:00 AM" in result


def test_noon():
    expr = parse("0 12 * * *")
    result = humanize(expr)
    assert "12:00 PM" in result


def test_specific_dom():
    expr = parse("0 0 15 * *")
    result = humanize(expr)
    assert "day 15" in result


def test_specific_month():
    expr = parse("0 0 1 6 *")
    result = humanize(expr)
    assert "June" in result


def test_specific_dow():
    expr = parse("0 8 * * 1")
    result = humanize(expr)
    assert "Monday" in result


def test_full_expression():
    expr = parse("30 14 1 3 *")
    result = humanize(expr)
    assert "minute 30" in result
    assert "2:00 PM" in result
    assert "day 1" in result
    assert "March" in result


def test_hourly_step():
    expr = parse("0 */6 * * *")
    result = humanize(expr)
    assert "every 6 hours" in result
