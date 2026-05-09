"""Tests for cronscope.streak_command."""

from __future__ import annotations

import argparse
from unittest.mock import patch

import pytest

from cronscope.streak_command import add_streak_subparser, run_streak


def _make_args(**kwargs):
    defaults = {
        "expression": "* * * * *",
        "days": 7,
        "start": None,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_add_streak_subparser_registers_command():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")
    add_streak_subparser(sub)
    args = parser.parse_args(["streak", "* * * * *"])
    assert args.expression == "* * * * *"


def test_run_streak_returns_zero_on_success():
    args = _make_args()
    assert run_streak(args) == 0


def test_run_streak_invalid_expression_returns_one():
    args = _make_args(expression="not a cron")
    assert run_streak(args) == 1


def test_run_streak_invalid_start_returns_one():
    args = _make_args(start="not-a-date")
    assert run_streak(args) == 1


def test_run_streak_valid_iso_start_returns_zero():
    args = _make_args(start="2024-03-01T00:00:00")
    assert run_streak(args) == 0


def test_run_streak_prints_expression(capsys):
    args = _make_args(expression="0 9 * * *")
    run_streak(args)
    captured = capsys.readouterr()
    assert "0 9 * * *" in captured.out


def test_run_streak_prints_longest_streak(capsys):
    args = _make_args(expression="* * * * *", days=3)
    run_streak(args)
    captured = capsys.readouterr()
    assert "Longest streak" in captured.out


def test_run_streak_default_days_is_30():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")
    add_streak_subparser(sub)
    args = parser.parse_args(["streak", "* * * * *"])
    assert args.days == 30
