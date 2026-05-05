"""Tests for cronscope.scheduler."""

from datetime import datetime

import pytest
from cronscope.parser import parse
from cronscope.scheduler import next_runs, iter_runs


BASE = datetime(2024, 1, 15, 12, 0, 0)  # Monday 12:00


def test_next_runs_returns_correct_count():
    expr = parse("* * * * *")
    runs = next_runs(expr, after=BASE, count=5)
    assert len(runs) == 5


def test_next_runs_every_minute():
    expr = parse("* * * * *")
    runs = next_runs(expr, after=BASE, count=3)
    assert runs[0] == datetime(2024, 1, 15, 12, 1)
    assert runs[1] == datetime(2024, 1, 15, 12, 2)
    assert runs[2] == datetime(2024, 1, 15, 12, 3)


def test_next_runs_every_5_minutes():
    expr = parse("*/5 * * * *")
    runs = next_runs(expr, after=BASE, count=3)
    assert runs[0].minute % 5 == 0
    assert all(r.minute % 5 == 0 for r in runs)


def test_next_runs_specific_hour():
    expr = parse("0 9 * * *")
    runs = next_runs(expr, after=BASE, count=3)
    assert all(r.hour == 9 and r.minute == 0 for r in runs)


def test_next_runs_weekday_filter():
    # BASE is Monday (weekday index 1 in cron 0=Sun)
    expr = parse("0 0 * * 3")  # Wednesdays
    runs = next_runs(expr, after=BASE, count=2)
    # Wednesday is weekday() == 2 in Python, cron 3
    assert all(r.weekday() == 2 for r in runs)


def test_iter_runs_yields_correct_values():
    expr = parse("0 * * * *")
    gen = iter_runs(expr, after=BASE)
    first = next(gen)
    assert first.minute == 0
    second = next(gen)
    assert second.minute == 0
    assert second > first


def test_next_runs_no_match_within_limit():
    # Feb 30 never exists — should return empty list within max_iterations
    expr = parse("0 0 30 2 *")
    runs = next_runs(expr, after=BASE, count=1, max_iterations=100)
    assert runs == []
