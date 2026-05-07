"""Tests for cronscope.summarizer."""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from cronscope.parser import parse
from cronscope.summarizer import summarize, ScheduleSummary


START = datetime(2024, 1, 1, 0, 0, 0)
END_7D = START + timedelta(days=7)


def test_summarize_returns_schedule_summary():
    expr = parse("* * * * *")
    result = summarize(expr, START, END_7D)
    assert isinstance(result, ScheduleSummary)


def test_summarize_every_minute_total_runs():
    expr = parse("* * * * *")
    result = summarize(expr, START, END_7D)
    # 7 days * 24 hours * 60 minutes = 10080
    assert result.total_runs == 10080


def test_summarize_every_hour_total_runs():
    expr = parse("0 * * * *")
    result = summarize(expr, START, END_7D)
    assert result.total_runs == 7 * 24


def test_summarize_runs_per_day_every_hour():
    expr = parse("0 * * * *")
    result = summarize(expr, START, END_7D)
    assert result.runs_per_day == 24.0


def test_summarize_first_and_last_run_present():
    expr = parse("0 6 * * *")
    result = summarize(expr, START, END_7D)
    assert result.first_run is not None
    assert result.last_run is not None
    assert result.first_run < result.last_run


def test_summarize_no_runs_in_empty_window():
    expr = parse("0 6 * * *")
    # window of zero width
    with pytest.raises(ValueError):
        summarize(expr, START, START)


def test_summarize_expression_string_stored():
    expr = parse("*/5 * * * *")
    result = summarize(expr, START, END_7D)
    assert result.expression == "*/5 * * * *"


def test_summarize_busiest_hour_uniform_schedule():
    # Every minute: all hours equally busy
    expr = parse("* * * * *")
    result = summarize(expr, START, END_7D)
    assert result.busiest_hour_count == result.quietest_hour_count


def test_summarize_specific_hour_is_busiest():
    # Only fires at 09:00 each day
    expr = parse("0 9 * * *")
    result = summarize(expr, START, END_7D)
    assert result.busiest_hour == 9


def test_summarize_window_boundaries_stored():
    expr = parse("* * * * *")
    result = summarize(expr, START, END_7D)
    assert result.window_start == START
    assert result.window_end == END_7D
