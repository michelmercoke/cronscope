"""Tests for cronscope.streak."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from cronscope.streak import analyze_streaks, StreakReport


START = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


def test_analyze_streaks_returns_streak_report():
    report = analyze_streaks("* * * * *", start=START, days=7)
    assert isinstance(report, StreakReport)


def test_every_minute_all_days_active():
    report = analyze_streaks("* * * * *", start=START, days=7)
    assert report.active_days == 7
    assert report.inactive_days == 0


def test_every_minute_longest_streak_equals_days():
    report = analyze_streaks("* * * * *", start=START, days=7)
    assert report.longest_streak == 7


def test_every_minute_no_gaps():
    report = analyze_streaks("* * * * *", start=START, days=7)
    assert report.longest_gap == 0
    assert report.gaps == []


def test_impossible_dom_all_inactive():
    # 30th of February never exists
    report = analyze_streaks("0 0 30 2 *", start=START, days=28)
    assert report.active_days == 0
    assert report.inactive_days == 28


def test_impossible_dom_longest_streak_zero():
    report = analyze_streaks("0 0 30 2 *", start=START, days=28)
    assert report.longest_streak == 0


def test_impossible_dom_longest_gap_equals_days():
    report = analyze_streaks("0 0 30 2 *", start=START, days=28)
    assert report.longest_gap == 28


def test_expression_stored_in_report():
    expr = "0 9 * * 1"
    report = analyze_streaks(expr, start=START, days=14)
    assert report.expression == expr


def test_days_analyzed_stored():
    report = analyze_streaks("* * * * *", start=START, days=10)
    assert report.days_analyzed == 10


def test_streaks_list_nonempty_for_active_schedule():
    report = analyze_streaks("* * * * *", start=START, days=5)
    assert len(report.streaks) >= 1


def test_active_plus_inactive_equals_days():
    report = analyze_streaks("0 12 * * 1-5", start=START, days=14)
    assert report.active_days + report.inactive_days == 14


def test_daily_noon_has_active_days():
    report = analyze_streaks("0 12 * * *", start=START, days=7)
    assert report.active_days == 7
    assert report.longest_streak == 7
