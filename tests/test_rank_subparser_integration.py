"""Integration tests for the rank subparser argument parsing."""

import argparse
import pytest
from cronscope.rank_command import add_rank_subparser


@pytest.fixture()
def parser():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers(dest="command")
    add_rank_subparser(sub)
    return root


def test_default_days_is_seven(parser):
    args = parser.parse_args(["rank", "* * * * *"])
    assert args.days == 7


def test_default_count_is_500(parser):
    args = parser.parse_args(["rank", "* * * * *"])
    assert args.count == 500


def test_custom_days(parser):
    args = parser.parse_args(["rank", "* * * * *", "--days", "14"])
    assert args.days == 14


def test_custom_count(parser):
    args = parser.parse_args(["rank", "* * * * *", "--count", "200"])
    assert args.count == 200


def test_multiple_expressions(parser):
    args = parser.parse_args(["rank", "* * * * *", "0 * * * *", "0 0 * * *"])
    assert len(args.expressions) == 3


def test_labels_stored(parser):
    args = parser.parse_args(
        ["rank", "* * * * *", "0 0 * * *", "--labels", "a", "b"]
    )
    assert args.labels == ["a", "b"]


def test_default_labels_is_none(parser):
    args = parser.parse_args(["rank", "* * * * *"])
    assert args.labels is None
