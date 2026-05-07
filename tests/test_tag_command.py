"""Tests for cronscope.tag_command."""

from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

import pytest

from cronscope.tag_command import run_tag, _load_registry, _save_registry, add_tag_subparser


def _make_args(expression="* * * * *", label="every minute", registry=None,
               list_tags=False, remove=False, tmp_path=None):
    if registry is None:
        registry = str(tmp_path / "tags.json") if tmp_path else "/tmp/cronscope_test_tags.json"
    return Namespace(
        expression=expression,
        label=label,
        registry=registry,
        list_tags=list_tags,
        remove=remove,
    )


def test_run_tag_saves_entry(tmp_path):
    args = _make_args(expression="0 9 * * 1-5", label="weekday morning", tmp_path=tmp_path)
    rc = run_tag(args)
    assert rc == 0
    registry = _load_registry(tmp_path / "tags.json")
    assert registry["0 9 * * 1-5"] == "weekday morning"


def test_run_tag_returns_zero_on_success(tmp_path):
    args = _make_args(tmp_path=tmp_path)
    assert run_tag(args) == 0


def test_run_tag_invalid_expression_returns_one(tmp_path):
    args = _make_args(expression="99 * * * *", tmp_path=tmp_path)
    assert run_tag(args) == 1


def test_run_tag_list_empty(tmp_path, capsys):
    args = _make_args(list_tags=True, tmp_path=tmp_path)
    rc = run_tag(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "No tagged" in out


def test_run_tag_list_shows_entries(tmp_path, capsys):
    reg = tmp_path / "tags.json"
    _save_registry(reg, {"*/5 * * * *": "every 5 minutes"})
    args = _make_args(list_tags=True, registry=str(reg), tmp_path=tmp_path)
    rc = run_tag(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "every 5 minutes" in out
    assert "*/5 * * * *" in out


def test_run_tag_remove_existing(tmp_path, capsys):
    reg = tmp_path / "tags.json"
    _save_registry(reg, {"0 0 * * *": "midnight"})
    args = _make_args(expression="0 0 * * *", registry=str(reg), remove=True, tmp_path=tmp_path)
    rc = run_tag(args)
    assert rc == 0
    assert "0 0 * * *" not in _load_registry(reg)


def test_run_tag_remove_nonexistent(tmp_path, capsys):
    args = _make_args(expression="0 0 * * *", remove=True, tmp_path=tmp_path)
    rc = run_tag(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "No tag found" in out


def test_add_tag_subparser_registers_command():
    import argparse
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_tag_subparser(sub)
    args = p.parse_args(["tag", "* * * * *", "every minute"])
    assert args.command == "tag"
    assert args.expression == "* * * * *"
    assert args.label == "every minute"
