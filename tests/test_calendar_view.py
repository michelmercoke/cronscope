"""Tests for cronscope.calendar_view and cronscope.calendar_command."""

from __future__ import annotations

import argparse
from unittest.mock import patch

import pytest

from cronscope.parser import parse
from cronscope.calendar_view import build_calendar_view, render_calendar, CalendarView
from cronscope.calendar_command import add_calendar_subparser, run_calendar


# ---------------------------------------------------------------------------
# build_calendar_view
# ---------------------------------------------------------------------------

def test_build_calendar_view_returns_calendar_view():
    expr = parse("0 9 * * *")
    view = build_calendar_view(expr, year=2024, month=1)
    assert isinstance(view, CalendarView)


def test_build_calendar_view_daily_has_31_days():
    expr = parse("0 9 * * *")  # every day at 09:00
    view = build_calendar_view(expr, year=2024, month=1)  # January has 31 days
    assert len(view.fire_times) == 31


def test_build_calendar_view_single_time_per_day():
    expr = parse("0 9 * * *")
    view = build_calendar_view(expr, year=2024, month=1)
    for times in view.fire_times.values():
        assert times == ["09:00"]


def test_build_calendar_view_hourly_has_24_per_day():
    expr = parse("0 * * * *")
    view = build_calendar_view(expr, year=2024, month=1)
    assert view.fire_times[1] == [f"{h:02d}:00" for h in range(24)]


def test_build_calendar_view_no_runs_for_impossible_dom():
    # 31st of February never occurs
    expr = parse("0 0 31 2 *")
    view = build_calendar_view(expr, year=2024, month=2)
    assert view.fire_times == {}


def test_build_calendar_view_expression_stored():
    expr = parse("*/5 * * * *")
    view = build_calendar_view(expr, year=2024, month=3)
    assert "*/5" in view.expression


# ---------------------------------------------------------------------------
# render_calendar
# ---------------------------------------------------------------------------

def test_render_calendar_returns_string():
    expr = parse("0 12 * * *")
    view = build_calendar_view(expr, year=2024, month=6)
    result = render_calendar(view)
    assert isinstance(result, str)


def test_render_calendar_contains_month_name():
    expr = parse("0 0 * * *")
    view = build_calendar_view(expr, year=2024, month=7)
    assert "July" in render_calendar(view)


def test_render_calendar_contains_year():
    expr = parse("0 0 * * *")
    view = build_calendar_view(expr, year=2025, month=1)
    assert "2025" in render_calendar(view)


def test_render_calendar_no_runs_message():
    expr = parse("0 0 31 2 *")
    view = build_calendar_view(expr, year=2024, month=2)
    assert "no runs" in render_calendar(view)


# ---------------------------------------------------------------------------
# run_calendar (command)
# ---------------------------------------------------------------------------

def _make_args(**kwargs):
    defaults = {
        "expression": "0 9 * * *",
        "year": 2024,
        "month": 1,
        "max_per_cell": 3,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_run_calendar_returns_zero_on_success(capsys):
    assert run_calendar(_make_args()) == 0


def test_run_calendar_invalid_expression_returns_one(capsys):
    assert run_calendar(_make_args(expression="not a cron")) == 1


def test_run_calendar_invalid_month_returns_one(capsys):
    assert run_calendar(_make_args(month=13)) == 1


def test_run_calendar_output_contains_expression(capsys):
    run_calendar(_make_args(expression="0 9 * * *"))
    out = capsys.readouterr().out
    assert "0 9 * * *" in out


def test_add_calendar_subparser_registers_command():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    add_calendar_subparser(sub)
    args = root.parse_args(["calendar", "0 0 * * *", "--month", "3"])
    assert args.month == 3
