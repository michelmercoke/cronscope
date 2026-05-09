"""Tests for cronscope.anomaly."""
from __future__ import annotations

from datetime import datetime

import pytest

from cronscope.anomaly import AnomalyReport, detect_anomalies


START = datetime(2024, 1, 1, 0, 0, 0)


def test_detect_anomalies_returns_anomaly_report():
    report = detect_anomalies("* * * * *", START, count=10)
    assert isinstance(report, AnomalyReport)


def test_every_minute_mean_gap_is_60():
    report = detect_anomalies("* * * * *", START, count=60)
    assert report.mean_gap_seconds == pytest.approx(60.0)


def test_every_minute_std_gap_is_zero():
    report = detect_anomalies("* * * * *", START, count=60)
    assert report.std_gap_seconds == pytest.approx(0.0)


def test_every_minute_no_long_gaps():
    report = detect_anomalies("* * * * *", START, count=120)
    assert report.long_gaps == []


def test_every_5_minutes_mean_gap_is_300():
    report = detect_anomalies("*/5 * * * *", START, count=60)
    assert report.mean_gap_seconds == pytest.approx(300.0)


def test_gaps_length_is_runs_minus_one():
    report = detect_anomalies("* * * * *", START, count=20)
    assert len(report.gaps) == report.total_runs - 1


def test_total_runs_matches_count():
    report = detect_anomalies("* * * * *", START, count=50)
    assert report.total_runs == 50


def test_burst_windows_detected_for_every_minute():
    # Every minute within a 10-min window should be detected as burst
    report = detect_anomalies(
        "* * * * *", START, count=60,
        burst_threshold=5, burst_window_minutes=10
    )
    assert len(report.burst_windows) > 0


def test_burst_window_fields():
    report = detect_anomalies(
        "* * * * *", START, count=30,
        burst_threshold=3, burst_window_minutes=5
    )
    for bstart, bend, cnt in report.burst_windows:
        assert isinstance(bstart, datetime)
        assert isinstance(bend, datetime)
        assert isinstance(cnt, int)
        assert cnt >= 3


def test_no_burst_when_threshold_very_high():
    report = detect_anomalies(
        "* * * * *", START, count=30,
        burst_threshold=9999, burst_window_minutes=10
    )
    assert report.burst_windows == []


def test_single_run_returns_empty_report():
    report = detect_anomalies("* * * * *", START, count=1)
    assert report.total_runs == 1
    assert report.mean_gap_seconds == 0.0
    assert report.gaps == []
    assert report.long_gaps == []
    assert report.burst_windows == []


def test_expression_stored_in_report():
    expr = "0 9 * * 1-5"
    report = detect_anomalies(expr, START, count=10)
    assert report.expression == expr
