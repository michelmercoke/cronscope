"""Tests for cronscope.diff_command."""

import argparse
from types import SimpleNamespace
from unittest.mock import patch
import pytest

from cronscope.diff_command import add_diff_subparser, run_diff


def _make_args(**kwargs):
    defaults = {
        "expr_a": "* * * * *",
        "expr_b": "*/5 * * * *",
        "count": 10,
        "start": None,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_run_diff_returns_zero_on_success():
    args = _make_args()
    assert run_diff(args) == 0


def test_run_diff_invalid_start_returns_one():
    args = _make_args(start="not-a-date")
    assert run_diff(args) == 1


def test_run_diff_invalid_expr_returns_one():
    args = _make_args(expr_a="99 99 99 99 99")
    assert run_diff(args) == 1


def test_run_diff_valid_start_iso():
    args = _make_args(start="2024-06-01T08:00")
    assert run_diff(args) == 0


def test_run_diff_prints_output(capsys):
    args = _make_args()
    run_diff(args)
    captured = capsys.readouterr()
    assert "Comparing" in captured.out


def test_add_diff_subparser_registers_command():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    add_diff_subparser(subparsers)
    ns = parser.parse_args(["diff", "* * * * *", "*/5 * * * *"])
    assert ns.expr_a == "* * * * *"
    assert ns.expr_b == "*/5 * * * *"
    assert ns.count == 20


def test_add_diff_subparser_custom_count():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    add_diff_subparser(subparsers)
    ns = parser.parse_args(["diff", "* * * * *", "*/2 * * * *", "-n", "5"])
    assert ns.count == 5
