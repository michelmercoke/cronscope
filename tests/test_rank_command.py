"""Tests for cronscope.rank_command."""

import argparse
import pytest
from cronscope.rank_command import add_rank_subparser, run_rank, _format_table
from cronscope.ranker import RankEntry


def _make_args(**kwargs):
    defaults = {
        "expressions": ["* * * * *", "0 * * * *"],
        "labels": None,
        "days": 1,
        "count": 100,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_add_rank_subparser_registers_command():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    add_rank_subparser(sub)
    args = root.parse_args(["rank", "* * * * *"])
    assert hasattr(args, "func")


def test_run_rank_returns_zero_on_success():
    args = _make_args()
    assert run_rank(args) == 0


def test_run_rank_invalid_expression_returns_zero():
    # Invalid expressions are ranked with score 0 but no error is raised
    args = _make_args(expressions=["bad_expr"])
    assert run_rank(args) == 0


def test_run_rank_mismatched_labels_returns_one():
    args = _make_args(
        expressions=["* * * * *", "0 * * * *"],
        labels=["only-one"],
    )
    assert run_rank(args) == 1


def test_format_table_contains_rank_header():
    entries = [
        RankEntry("* * * * *", "every-min", 1440.0, 0.0, 1),
        RankEntry("0 0 * * *", "daily", 1.0, 0.999, 2),
    ]
    table = _format_table(entries)
    assert "Rank" in table
    assert "Score" in table
    assert "Runs/day" in table


def test_format_table_contains_labels():
    entries = [RankEntry("0 0 * * *", "my-job", 1.0, 0.999, 1)]
    table = _format_table(entries)
    assert "my-job" in table


def test_run_rank_output_printed(capsys):
    args = _make_args(expressions=["0 0 * * *"], days=1, count=50)
    run_rank(args)
    captured = capsys.readouterr()
    assert "Rank" in captured.out
