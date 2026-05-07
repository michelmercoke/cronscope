"""Tests for cronscope.exporter."""

from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone

import pytest

from cronscope.exporter import export, export_csv, export_json, export_text

NOW = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
RUNS = [
    datetime(2024, 1, 15, 12, 5, 0, tzinfo=timezone.utc),
    datetime(2024, 1, 15, 12, 10, 0, tzinfo=timezone.utc),
    datetime(2024, 1, 15, 12, 15, 0, tzinfo=timezone.utc),
]
EXPR = "*/5 * * * *"


def test_export_json_structure():
    result = export_json(RUNS, NOW, EXPR)
    data = json.loads(result)
    assert data["expression"] == EXPR
    assert data["count"] == 3
    assert len(data["runs"]) == 3


def test_export_json_run_fields():
    result = export_json(RUNS, NOW, EXPR)
    data = json.loads(result)
    first = data["runs"][0]
    assert "index" in first
    assert "datetime" in first
    assert "relative" in first
    assert "timestamp" in first
    assert first["index"] == 1


def test_export_json_timestamp_is_int():
    result = export_json(RUNS, NOW, EXPR)
    data = json.loads(result)
    assert isinstance(data["runs"][0]["timestamp"], int)


def test_export_csv_has_header():
    result = export_csv(RUNS, NOW)
    reader = csv.DictReader(io.StringIO(result))
    assert reader.fieldnames == ["index", "datetime", "relative", "timestamp"]


def test_export_csv_row_count():
    result = export_csv(RUNS, NOW)
    reader = csv.DictReader(io.StringIO(result))
    rows = list(reader)
    assert len(rows) == 3


def test_export_text_line_count():
    result = export_text(RUNS, NOW)
    lines = result.strip().splitlines()
    assert len(lines) == 3


def test_export_text_contains_index():
    result = export_text(RUNS, NOW)
    assert "1." in result
    assert "2." in result


def test_export_dispatch_json():
    result = export(RUNS, NOW, fmt="json", expression=EXPR)
    assert result.startswith("{")


def test_export_dispatch_csv():
    result = export(RUNS, NOW, fmt="csv")
    assert "datetime" in result


def test_export_dispatch_text_default():
    result = export(RUNS, NOW)
    assert "1." in result


def test_export_empty_runs():
    result = export_json([], NOW, EXPR)
    data = json.loads(result)
    assert data["count"] == 0
    assert data["runs"] == []
