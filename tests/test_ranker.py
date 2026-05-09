"""Tests for cronscope.ranker."""

import pytest
from cronscope.ranker import rank, _score, RankEntry


def test_score_zero_runs():
    assert _score(0) == 0.0


def test_score_one_run_per_day():
    s = _score(1)
    assert 0.99 < s <= 1.0


def test_score_max_frequency():
    # 1440 runs/day should yield score 0.0
    assert _score(1440) == 0.0


def test_score_decreases_with_frequency():
    assert _score(10) > _score(100) > _score(1000)


def test_rank_returns_list_of_rank_entries():
    entries = rank(["0 * * * *", "* * * * *"], window_days=1, count=100)
    assert all(isinstance(e, RankEntry) for e in entries)


def test_rank_assigns_sequential_ranks():
    entries = rank(["0 0 * * *", "0 * * * *", "* * * * *"], window_days=1, count=200)
    ranks = [e.rank for e in entries]
    assert sorted(ranks) == list(range(1, len(entries) + 1))


def test_rank_most_friendly_first():
    # daily is friendlier than every-minute
    entries = rank(["* * * * *", "0 0 * * *"], window_days=1, count=200)
    daily = next(e for e in entries if e.expression == "0 0 * * *")
    every_min = next(e for e in entries if e.expression == "* * * * *")
    assert daily.rank < every_min.rank


def test_rank_with_labels():
    entries = rank(["0 0 * * *"], labels=["midnight"], window_days=1, count=50)
    assert entries[0].label == "midnight"


def test_rank_default_labels_are_expressions():
    expr = "0 6 * * *"
    entries = rank([expr], window_days=1, count=50)
    assert entries[0].label == expr


def test_rank_mismatched_labels_raises():
    with pytest.raises(ValueError):
        rank(["* * * * *", "0 * * * *"], labels=["only-one"], window_days=1)


def test_rank_invalid_expression_gets_zero_score():
    entries = rank(["not_a_cron"], window_days=1, count=50)
    assert entries[0].score == 0.0
    assert entries[0].runs_per_day == 0.0


def test_rank_runs_per_day_positive_for_valid_expr():
    entries = rank(["* * * * *"], window_days=1, count=200)
    assert entries[0].runs_per_day > 0
