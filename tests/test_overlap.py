"""Tests for cronscope.overlap."""

from datetime import datetime

import pytest

from cronscope.overlap import find_overlaps, OverlapReport


START = datetime(2024, 1, 1, 0, 0, 0)


def test_returns_overlap_report():
    report = find_overlaps("* * * * *", "* * * * *", start=START, count=10)
    assert isinstance(report, OverlapReport)


def test_identical_expressions_all_overlap():
    report = find_overlaps("*/5 * * * *", "*/5 * * * *", start=START, count=10)
    assert report.overlap_count == 10
    assert report.overlap_ratio_a == 1.0
    assert report.overlap_ratio_b == 1.0


def test_no_overlap_between_disjoint_minutes():
    # even minutes vs odd minutes — no overlap
    report = find_overlaps("0 * * * *", "30 * * * *", start=START, count=24)
    assert report.overlap_count == 0


def test_partial_overlap():
    # every 10 min vs every 30 min — overlap at :00 and :30
    report = find_overlaps("*/10 * * * *", "*/30 * * * *", start=START, count=60)
    assert report.overlap_count > 0
    assert report.overlap_count < report.total_a


def test_overlap_runs_are_sorted():
    report = find_overlaps("*/5 * * * *", "*/15 * * * *", start=START, count=50)
    assert report.overlapping_runs == sorted(report.overlapping_runs)


def test_overlap_runs_are_in_both_sets():
    from cronscope.parser import parse
    from cronscope.scheduler import next_runs

    expr_a = "*/6 * * * *"
    expr_b = "*/4 * * * *"
    report = find_overlaps(expr_a, expr_b, start=START, count=60)

    runs_a = set(next_runs(parse(expr_a), start=START, count=60))
    runs_b = set(next_runs(parse(expr_b), start=START, count=60))

    for dt in report.overlapping_runs:
        assert dt in runs_a
        assert dt in runs_b


def test_overlap_ratio_between_zero_and_one():
    report = find_overlaps("*/5 * * * *", "*/15 * * * *", start=START, count=60)
    assert 0.0 <= report.overlap_ratio_a <= 1.0
    assert 0.0 <= report.overlap_ratio_b <= 1.0


def test_zero_count_gives_empty_overlap():
    report = find_overlaps("* * * * *", "* * * * *", start=START, count=0)
    assert report.overlap_count == 0
    assert report.overlap_ratio_a == 0.0
