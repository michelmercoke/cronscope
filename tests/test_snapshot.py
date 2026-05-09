"""Tests for cronscope.snapshot."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

from cronscope.snapshot import (
    Snapshot,
    SnapshotDiff,
    take_snapshot,
    save_snapshot,
    load_snapshot,
    compare_snapshots,
)

START = datetime(2024, 1, 15, 12, 0)


def test_take_snapshot_returns_snapshot():
    snap = take_snapshot("* * * * *", count=5, start=START)
    assert isinstance(snap, Snapshot)


def test_take_snapshot_run_count():
    snap = take_snapshot("* * * * *", count=7, start=START)
    assert len(snap.runs) == 7


def test_take_snapshot_expression_stored():
    snap = take_snapshot("0 9 * * 1", count=3, start=START)
    assert snap.expression == "0 9 * * 1"


def test_take_snapshot_label_stored():
    snap = take_snapshot("* * * * *", count=1, start=START, label="my-job")
    assert snap.label == "my-job"


def test_take_snapshot_label_defaults_none():
    snap = take_snapshot("* * * * *", count=1, start=START)
    assert snap.label is None


def test_take_snapshot_runs_are_iso_strings():
    snap = take_snapshot("* * * * *", count=3, start=START)
    for r in snap.runs:
        datetime.fromisoformat(r)  # must not raise


def test_save_and_load_snapshot_roundtrip(tmp_path):
    snap = take_snapshot("*/5 * * * *", count=4, start=START, label="test")
    p = tmp_path / "snap.json"
    save_snapshot(snap, p)
    loaded = load_snapshot(p)
    assert loaded.expression == snap.expression
    assert loaded.runs == snap.runs
    assert loaded.label == snap.label


def test_save_snapshot_creates_parent_dirs(tmp_path):
    snap = take_snapshot("* * * * *", count=2, start=START)
    p = tmp_path / "nested" / "dir" / "snap.json"
    save_snapshot(snap, p)
    assert p.exists()


def test_save_snapshot_is_valid_json(tmp_path):
    snap = take_snapshot("* * * * *", count=2, start=START)
    p = tmp_path / "snap.json"
    save_snapshot(snap, p)
    data = json.loads(p.read_text())
    assert "expression" in data
    assert "runs" in data


def test_compare_snapshots_identical():
    snap = take_snapshot("* * * * *", count=5, start=START)
    diff = compare_snapshots(snap, snap)
    assert not diff.has_changes
    assert len(diff.unchanged) == 5


def test_compare_snapshots_added():
    old = Snapshot(expression="* * * * *", taken_at="2024-01-01T00:00:00", runs=["2024-01-15T12:00:00"])
    new = Snapshot(expression="* * * * *", taken_at="2024-01-01T00:01:00", runs=["2024-01-15T12:00:00", "2024-01-15T12:01:00"])
    diff = compare_snapshots(old, new)
    assert "2024-01-15T12:01:00" in diff.added
    assert diff.has_changes


def test_compare_snapshots_removed():
    old = Snapshot(expression="* * * * *", taken_at="2024-01-01T00:00:00", runs=["2024-01-15T12:00:00", "2024-01-15T12:01:00"])
    new = Snapshot(expression="* * * * *", taken_at="2024-01-01T00:01:00", runs=["2024-01-15T12:00:00"])
    diff = compare_snapshots(old, new)
    assert "2024-01-15T12:01:00" in diff.removed


def test_snapshot_diff_has_changes_false_when_empty():
    d = SnapshotDiff()
    assert not d.has_changes
