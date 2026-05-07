"""Tests for cronscope.overlap_command."""

from __future__ import annotations

import argparse
from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest

from cronscope.overlap_command import add_overlap_subparser, run_overlap
from cronscope.overlap import OverlapReport


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "expr_a": "*/5 * * * *",
        "expr_b": "*/15 * * * *",
        "count": 100,
        "start": None,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_add_overlap_subparser_registers_command():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")
    add_overlap_subparser(sub)
    args = parser.parse_args(["overlap", "*/5 * * * *", "* * * * *"])
    assert args.expr_a == "*/5 * * * *"
    assert args.expr_b == "* * * * *"


def test_run_overlap_returns_zero_on_success(capsys):
    args = _make_args()
    result = run_overlap(args)
    assert result == 0


def test_run_overlap_invalid_start_returns_one(capsys):
    args = _make_args(start="not-a-date")
    result = run_overlap(args)
    assert result == 1
    captured = capsys.readouterr()
    assert "invalid" in captured.out.lower()


def test_run_overlap_invalid_expr_returns_one(capsys):
    args = _make_args(expr_a="invalid")
    result = run_overlap(args)
    assert result == 1
    captured = capsys.readouterr()
    assert "error" in captured.out.lower()


def test_run_overlap_output_contains_expressions(capsys):
    args = _make_args(expr_a="*/5 * * * *", expr_b="*/10 * * * *")
    run_overlap(args)
    captured = capsys.readouterr()
    assert "*/5 * * * *" in captured.out
    assert "*/10 * * * *" in captured.out


def test_run_overlap_with_iso_start(capsys):
    args = _make_args(start="2024-06-01T00:00:00", count=20)
    result = run_overlap(args)
    assert result == 0


def test_run_overlap_shows_overlap_count(capsys):
    args = _make_args(expr_a="*/5 * * * *", expr_b="*/5 * * * *", count=10)
    run_overlap(args)
    captured = capsys.readouterr()
    assert "10" in captured.out
