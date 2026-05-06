"""Tests for cronscope.formatter module."""

from datetime import datetime, timedelta

import pytest

from cronscope.formatter import (
    format_datetime,
    format_relative,
    format_schedule_table,
)


NOW = datetime(2024, 6, 15, 12, 0, 0)


def test_format_datetime():
    dt = datetime(2024, 6, 15, 9, 30, 0)
    assert format_datetime(dt) == "2024-06-15 09:30:00"


def test_format_relative_seconds():
    dt = NOW + timedelta(seconds=45)
    assert format_relative(dt, now=NOW) == "in 45s"


def test_format_relative_minutes():
    dt = NOW + timedelta(minutes=7)
    assert format_relative(dt, now=NOW) == "in 7m"


def test_format_relative_hours():
    dt = NOW + timedelta(hours=3)
    assert format_relative(dt, now=NOW) == "in 3h"


def test_format_relative_hours_and_minutes():
    dt = NOW + timedelta(hours=2, minutes=30)
    assert format_relative(dt, now=NOW) == "in 2h 30m"


def test_format_relative_days():
    dt = NOW + timedelta(days=3)
    assert format_relative(dt, now=NOW) == "in 3d"


def test_format_schedule_table_contains_expression():
    runs = [NOW + timedelta(minutes=i * 5) for i in range(1, 4)]
    output = format_schedule_table("*/5 * * * *", runs, now=NOW, use_color=False)
    assert "*/5 * * * *" in output


def test_format_schedule_table_contains_timestamps():
    runs = [NOW + timedelta(minutes=5), NOW + timedelta(minutes=10)]
    output = format_schedule_table("*/5 * * * *", runs, now=NOW, use_color=False)
    assert "2024-06-15 12:05:00" in output
    assert "2024-06-15 12:10:00" in output


def test_format_schedule_table_row_count():
    runs = [NOW + timedelta(minutes=i) for i in range(1, 6)]
    output = format_schedule_table("* * * * *", runs, now=NOW, use_color=False)
    lines = [l for l in output.splitlines() if l.strip() and not l.startswith("-")]
    # header + 5 run lines
    assert len(lines) == 6


def test_format_schedule_table_no_color_no_escape_codes():
    runs = [NOW + timedelta(minutes=5)]
    output = format_schedule_table("*/5 * * * *", runs, now=NOW, use_color=False)
    assert "\033[" not in output


def test_format_schedule_table_with_color_has_escape_codes():
    runs = [NOW + timedelta(minutes=5)]
    output = format_schedule_table("*/5 * * * *", runs, now=NOW, use_color=True)
    assert "\033[" in output
