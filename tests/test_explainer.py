"""Tests for cronscope.explainer."""

import pytest
from cronscope.parser import parse
from cronscope.explainer import explain


def test_explain_every_minute():
    expr = parse("* * * * *")
    assert explain(expr) == "every minute"


def test_explain_every_5_minutes():
    expr = parse("*/5 * * * *")
    assert explain(expr) == "every 5 minutes"


def test_explain_specific_time():
    expr = parse("30 9 * * *")
    result = explain(expr)
    assert "minute 30" in result
    assert "hour 9" in result


def test_explain_specific_dom():
    expr = parse("0 0 15 * *")
    result = explain(expr)
    assert "day-of-month 15" in result


def test_explain_specific_month():
    expr = parse("0 0 1 6 *")
    result = explain(expr)
    assert "June" in result


def test_explain_specific_weekday():
    expr = parse("0 9 * * 1")
    result = explain(expr)
    assert "Monday" in result


def test_explain_weekday_range():
    expr = parse("0 8 * * 1-5")
    result = explain(expr)
    assert "Monday" in result
    assert "Friday" in result


def test_explain_month_list():
    expr = parse("0 0 1 1,7 *")
    result = explain(expr)
    assert "January" in result
    assert "July" in result


def test_explain_step_in_range():
    expr = parse("0 8-18/2 * * *")
    result = explain(expr)
    assert "every 2 hours from 8 through 18" in result


def test_explain_every_minute_step():
    expr = parse("*/10 * * * *")
    result = explain(expr)
    assert "every 10 minutes" in result
