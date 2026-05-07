"""Tests for cronscope.differ."""

from datetime import datetime
import pytest

from cronscope.differ import diff, format_diff, DiffResult


FIXED_START = datetime(2024, 1, 15, 12, 0, 0)


def test_identical_expressions_have_no_divergence():
    result = diff("* * * * *", "* * * * *", start=FIXED_START, count=10)
    assert result.divergence_count == 0
    assert result.overlap_count == 10


def test_completely_different_expressions():
    # even hours vs odd hours — no overlap within 10 slots
    result = diff("0 */2 * * *", "0 1-23/2 * * *", start=FIXED_START, count=10)
    assert result.overlap_count == 0
    assert len(result.only_in_a) > 0
    assert len(result.only_in_b) > 0


def test_only_in_a_not_in_b():
    # every minute vs every 5 minutes — every-5 runs are a subset
    result = diff("* * * * *", "*/5 * * * *", start=FIXED_START, count=20)
    # every-5 runs should all appear in every-minute runs too
    assert len(result.only_in_b) == 0
    assert len(result.only_in_a) > 0


def test_common_runs_are_intersection():
    result = diff("*/5 * * * *", "*/10 * * * *", start=FIXED_START, count=30)
    # every-10 is a subset of every-5
    for dt in result.common:
        assert dt.minute % 5 == 0
        assert dt.minute % 10 == 0


def test_diff_result_fields():
    result = diff("0 9 * * *", "0 10 * * *", start=FIXED_START, count=5)
    assert result.expr_a == "0 9 * * *"
    assert result.expr_b == "0 10 * * *"
    assert isinstance(result.only_in_a, list)
    assert isinstance(result.only_in_b, list)
    assert isinstance(result.common, list)


def test_format_diff_contains_expressions():
    result = diff("* * * * *", "*/5 * * * *", start=FIXED_START, count=10)
    output = format_diff(result)
    assert "* * * * *" in output
    assert "*/5 * * * *" in output


def test_format_diff_contains_counts():
    result = diff("*/5 * * * *", "*/10 * * * *", start=FIXED_START, count=20)
    output = format_diff(result)
    assert "Shared runs" in output
    assert "Exclusive to first" in output or "Exclusive to second" in output or "0" in output


def test_diff_default_start_does_not_raise():
    result = diff("0 12 * * *", "0 13 * * *", count=5)
    assert isinstance(result, DiffResult)
