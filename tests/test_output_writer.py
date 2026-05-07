"""Tests for cronscope.output_writer."""

from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

from cronscope.output_writer import detect_format_from_path, write_output


def test_write_output_to_stdout(capsys):
    write_output("hello world")
    captured = capsys.readouterr()
    assert "hello world" in captured.out


def test_write_output_appends_newline(capsys):
    write_output("no newline")
    captured = capsys.readouterr()
    assert captured.out.endswith("\n")


def test_write_output_does_not_double_newline(capsys):
    write_output("has newline\n")
    captured = capsys.readouterr()
    assert captured.out == "has newline\n"


def test_write_output_to_file(tmp_path):
    dest = tmp_path / "out.txt"
    write_output("file content", path=str(dest))
    assert dest.read_text(encoding="utf-8") == "file content"


def test_write_output_creates_parent_dirs(tmp_path):
    dest = tmp_path / "sub" / "dir" / "out.txt"
    write_output("nested", path=str(dest))
    assert dest.exists()


def test_detect_format_json():
    assert detect_format_from_path("output.json") == "json"


def test_detect_format_csv():
    assert detect_format_from_path("output.csv") == "csv"


def test_detect_format_txt():
    assert detect_format_from_path("output.txt") == "text"


def test_detect_format_text_extension():
    assert detect_format_from_path("output.text") == "text"


def test_detect_format_unknown_returns_none():
    assert detect_format_from_path("output.xml") is None


def test_detect_format_none_path():
    assert detect_format_from_path(None) is None


def test_detect_format_no_extension():
    assert detect_format_from_path("outputfile") is None
