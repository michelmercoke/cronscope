"""Tests for cronscope.heatmap and cronscope.heatmap_command."""

from __future__ import annotations

import argparse
from datetime import datetime
from unittest.mock import patch

import pytest

from cronscope.parser import parse
from cronscope.heatmap import render_heatmap, _build_counts, _shade, SHADES
from cronscope.heatmap_command import run_heatmap


START = datetime(2024, 1, 1, 0, 0)


def _make_args(**kwargs):
    defaults = {"expression": "* * * * *", "start": None, "samples": 500}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_render_heatmap_returns_string():
    expr = parse("* * * * *")
    result = render_heatmap(expr, start=START, n=100)
    assert isinstance(result, str)


def test_render_heatmap_contains_all_days():
    expr = parse("* * * * *")
    result = render_heatmap(expr, start=START, n=200)
    for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
        assert day in result


def test_render_heatmap_contains_hour_header():
    expr = parse("* * * * *")
    result = render_heatmap(expr, start=START, n=50)
    assert " 0 " in result
    assert "23" in result


def test_build_counts_total_runs():
    expr = parse("* * * * *")
    data = _build_counts(expr, start=START, n=60)
    assert data.total_runs == 60


def test_build_counts_max_count_positive_for_frequent():
    expr = parse("* * * * *")
    data = _build_counts(expr, start=START, n=300)
    assert data.max_count > 0


def test_shade_zero_returns_empty():
    assert _shade(0, 10) == SHADES[0]


def test_shade_max_returns_full():
    assert _shade(10, 10) == SHADES[-1]


def test_shade_zero_max_returns_empty():
    assert _shade(0, 0) == SHADES[0]


def test_run_heatmap_success_returns_zero(capsys):
    args = _make_args(expression="0 * * * *", samples=100)
    code = run_heatmap(args)
    assert code == 0


def test_run_heatmap_invalid_expression_returns_one():
    args = _make_args(expression="bad expr here")
    code = run_heatmap(args)
    assert code == 1


def test_run_heatmap_invalid_start_returns_one():
    args = _make_args(expression="* * * * *", start="not-a-date")
    code = run_heatmap(args)
    assert code == 1


def test_run_heatmap_invalid_samples_returns_one():
    args = _make_args(expression="* * * * *", samples=0)
    code = run_heatmap(args)
    assert code == 1


def test_run_heatmap_with_iso_start(capsys):
    args = _make_args(expression="*/15 * * * *", start="2024-06-01T08:00:00", samples=50)
    code = run_heatmap(args)
    assert code == 0
    captured = capsys.readouterr()
    assert "2024-06-01" in captured.out
