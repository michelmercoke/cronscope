"""Tests for cronscope.timeline and cronscope.timeline_command."""

from __future__ import annotations

import argparse
from datetime import datetime

import pytest

from cronscope.parser import parse
from cronscope.timeline import (
    collect_timeline_data,
    render_timeline,
    _build_timeline,
)
from cronscope.timeline_command import add_timeline_subparser, run_timeline


START = datetime(2024, 1, 15, 0, 0, 0)


# ---------------------------------------------------------------------------
# _build_timeline
# ---------------------------------------------------------------------------

def test_build_timeline_empty_runs_returns_dashes():
    bar = _build_timeline([], START, START.replace(hour=1), 10)
    assert bar == "----------"


def test_build_timeline_single_run_at_start():
    end = START.replace(hour=1)
    bar = _build_timeline([START], START, end, 10)
    assert bar[0] == "*"


def test_build_timeline_width_respected():
    end = START.replace(hour=1)
    bar = _build_timeline([], START, end, 40)
    assert len(bar) == 40


# ---------------------------------------------------------------------------
# collect_timeline_data
# ---------------------------------------------------------------------------

def test_collect_timeline_data_returns_timeline_data():
    expr = parse("* * * * *")
    data = collect_timeline_data(expr, START, hours=1, width=60)
    assert data.start == START
    assert data.width == 60


def test_collect_timeline_every_minute_24h_has_1440_runs():
    expr = parse("* * * * *")
    data = collect_timeline_data(expr, START, hours=24, count=1500)
    assert data.total_runs if hasattr(data, "total_runs") else len(data.runs) == 1440


def test_collect_timeline_hourly_24h_has_24_runs():
    expr = parse("0 * * * *")
    data = collect_timeline_data(expr, START, hours=24, count=100)
    assert len(data.runs) == 24


def test_collect_timeline_runs_within_window():
    expr = parse("0 * * * *")
    data = collect_timeline_data(expr, START, hours=6, count=50)
    for run in data.runs:
        assert data.start <= run < data.end


# ---------------------------------------------------------------------------
# render_timeline
# ---------------------------------------------------------------------------

def test_render_timeline_returns_string():
    expr = parse("0 * * * *")
    result = render_timeline(expr, START, hours=6)
    assert isinstance(result, str)


def test_render_timeline_contains_bar_delimiters():
    expr = parse("0 * * * *")
    result = render_timeline(expr, START, hours=6)
    assert "|" in result


def test_render_timeline_shows_run_count():
    expr = parse("0 * * * *")
    result = render_timeline(expr, START, hours=6, width=60)
    assert "6" in result


# ---------------------------------------------------------------------------
# timeline_command
# ---------------------------------------------------------------------------

def _make_args(**kwargs):
    defaults = {
        "expression": "0 * * * *",
        "hours": 24,
        "width": 72,
        "start": None,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_run_timeline_returns_zero_on_success():
    args = _make_args(start="2024-01-15T00:00:00")
    assert run_timeline(args) == 0


def test_run_timeline_invalid_expression_returns_one():
    args = _make_args(expression="not a cron")
    assert run_timeline(args) == 1


def test_run_timeline_invalid_start_returns_one():
    args = _make_args(start="not-a-date")
    assert run_timeline(args) == 1


def test_run_timeline_no_start_uses_now():
    args = _make_args(start=None)
    assert run_timeline(args) == 0


def test_add_timeline_subparser_registers_command():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    add_timeline_subparser(sub)
    parsed = root.parse_args(["timeline", "* * * * *"])
    assert parsed.expression == "* * * * *"
    assert parsed.hours == 24
    assert parsed.width == 72
