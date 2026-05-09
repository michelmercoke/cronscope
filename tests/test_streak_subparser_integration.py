"""Integration tests for the streak subparser argument parsing."""

from __future__ import annotations

import argparse
import pytest

from cronscope.streak_command import add_streak_subparser


@pytest.fixture()
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_streak_subparser(sub)
    return p


def test_default_days_is_30(parser):
    args = parser.parse_args(["streak", "* * * * *"])
    assert args.days == 30


def test_custom_days(parser):
    args = parser.parse_args(["streak", "* * * * *", "--days", "14"])
    assert args.days == 14


def test_start_flag_stored(parser):
    args = parser.parse_args(["streak", "* * * * *", "--start", "2024-06-01T00:00:00"])
    assert args.start == "2024-06-01T00:00:00"


def test_start_defaults_to_none(parser):
    args = parser.parse_args(["streak", "0 9 * * *"])
    assert args.start is None


def test_expression_stored(parser):
    args = parser.parse_args(["streak", "30 6 * * 1-5"])
    assert args.expression == "30 6 * * 1-5"


def test_command_name_is_streak(parser):
    args = parser.parse_args(["streak", "* * * * *"])
    assert args.command == "streak"
