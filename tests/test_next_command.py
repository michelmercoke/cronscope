"""Tests for cronscope.next_command."""

from __future__ import annotations

import argparse
from datetime import datetime
from unittest.mock import patch

import pytest

from cronscope.next_command import add_next_subparser, run_next


def _make_args(
    expression: str = "* * * * *",
    count: int = 5,
    start: str | None = None,
    no_humanize: bool = False,
) -> argparse.Namespace:
    return argparse.Namespace(
        expression=expression,
        count=count,
        start=start,
        no_humanize=no_humanize,
    )


def test_add_next_subparser_registers_command():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    add_next_subparser(sub)
    args = root.parse_args(["next", "* * * * *"])
    assert args.func is run_next
    assert args.expression == "* * * * *"


def test_run_next_returns_zero_on_success(capsys):
    args = _make_args(expression="* * * * *", count=3)
    result = run_next(args)
    assert result == 0


def test_run_next_invalid_expression_returns_one(capsys):
    args = _make_args(expression="not a cron")
    result = run_next(args)
    assert result == 1
    captured = capsys.readouterr()
    assert "Error" in captured.out


def test_run_next_invalid_start_returns_one(capsys):
    args = _make_args(start="not-a-date")
    result = run_next(args)
    assert result == 1
    captured = capsys.readouterr()
    assert "Error" in captured.out


def test_run_next_valid_start_iso(capsys):
    args = _make_args(expression="0 9 * * *", count=2, start="2024-01-01T00:00:00")
    result = run_next(args)
    assert result == 0
    captured = capsys.readouterr()
    assert "2024" in captured.out


def test_run_next_no_humanize_skips_description(capsys):
    args = _make_args(expression="*/5 * * * *", count=2, no_humanize=True)
    result = run_next(args)
    assert result == 0
    captured = capsys.readouterr()
    assert "Schedule" not in captured.out


def test_run_next_humanize_shows_description(capsys):
    args = _make_args(expression="*/5 * * * *", count=2, no_humanize=False)
    result = run_next(args)
    assert result == 0
    captured = capsys.readouterr()
    assert "Schedule" in captured.out


def test_run_next_count_clamps_to_one(capsys):
    args = _make_args(expression="* * * * *", count=0)
    result = run_next(args)
    assert result == 0
