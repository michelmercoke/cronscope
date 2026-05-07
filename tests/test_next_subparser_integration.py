"""Integration tests: 'next' subparser wired into a full ArgumentParser."""

from __future__ import annotations

import argparse

import pytest

from cronscope.next_command import add_next_subparser, run_next


@pytest.fixture()
def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="cronscope")
    sub = root.add_subparsers(dest="command")
    add_next_subparser(sub)
    return root


def test_default_count_is_ten(parser):
    args = parser.parse_args(["next", "* * * * *"])
    assert args.count == 10


def test_custom_count(parser):
    args = parser.parse_args(["next", "* * * * *", "-n", "3"])
    assert args.count == 3


def test_long_count_flag(parser):
    args = parser.parse_args(["next", "* * * * *", "--count", "7"])
    assert args.count == 7


def test_start_flag_stored(parser):
    args = parser.parse_args(["next", "0 0 * * *", "--start", "2024-06-01T12:00:00"])
    assert args.start == "2024-06-01T12:00:00"


def test_no_humanize_flag(parser):
    args = parser.parse_args(["next", "* * * * *", "--no-humanize"])
    assert args.no_humanize is True


def test_no_humanize_defaults_false(parser):
    args = parser.parse_args(["next", "* * * * *"])
    assert args.no_humanize is False


def test_func_set_to_run_next(parser):
    args = parser.parse_args(["next", "* * * * *"])
    assert args.func is run_next


def test_full_run_via_parsed_args(parser, capsys):
    args = parser.parse_args(
        ["next", "0 8 * * 1", "-n", "3", "--start", "2024-01-01T00:00:00"]
    )
    rc = args.func(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "2024" in out
