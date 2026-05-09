"""Tests for cronscope.retry_analyzer."""

from __future__ import annotations

from datetime import datetime

import pytest

from cronscope.retry_analyzer import RetryReport, RetryWindow, analyze_retries

START = datetime(2024, 1, 15, 12, 0, 0)


def test_analyze_retries_returns_retry_report():
    report = analyze_retries("* * * * *", start=START, count=10)
    assert isinstance(report, RetryReport)


def test_every_minute_has_60s_gaps():
    report = analyze_retries("* * * * *", start=START, count=10)
    assert report.min_gap_seconds == 60
    assert report.max_gap_seconds == 60
    assert report.avg_gap_seconds == 60.0


def test_every_5_minutes_has_300s_gaps():
    report = analyze_retries("*/5 * * * *", start=START, count=10)
    assert report.min_gap_seconds == 300
    assert report.max_gap_seconds == 300


def test_window_count_is_count_minus_one():
    report = analyze_retries("* * * * *", start=START, count=6)
    assert len(report.windows) == 5


def test_window_fields_populated():
    report = analyze_retries("*/10 * * * *", start=START, count=4)
    win = report.windows[0]
    assert isinstance(win, RetryWindow)
    assert win.gap_seconds == 600
    assert win.start < win.end


def test_safe_retries_every_minute_with_60s_retry():
    report = analyze_retries("* * * * *", start=START, count=5, retry_duration_seconds=60)
    # gap=60, retry_duration=60 → (60-60)//60 = 0
    for win in report.windows:
        assert win.safe_retries == 0


def test_safe_retries_every_hour_with_60s_retry():
    report = analyze_retries("0 * * * *", start=START, count=5, retry_duration_seconds=60)
    # gap=3600, (3600-60)//60 = 59
    for win in report.windows:
        assert win.safe_retries == 59


def test_warning_issued_for_high_frequency():
    report = analyze_retries("* * * * *", start=START, count=5, retry_duration_seconds=60)
    assert len(report.warnings) > 0
    assert "gap" in report.warnings[0].lower()


def test_no_warning_for_low_frequency():
    report = analyze_retries("0 0 * * *", start=START, count=5, retry_duration_seconds=60)
    assert report.warnings == []


def test_insufficient_runs_returns_warning():
    report = analyze_retries("* * * * *", start=START, count=1)
    assert report.min_gap_seconds == 0
    assert any("enough" in w.lower() for w in report.warnings)


def test_expression_stored_in_report():
    expr = "30 9 * * 1-5"
    report = analyze_retries(expr, start=START, count=10)
    assert report.expression == expr


def test_avg_gap_is_numeric():
    report = analyze_retries("*/15 * * * *", start=START, count=8)
    assert isinstance(report.avg_gap_seconds, float)
    assert report.avg_gap_seconds > 0
