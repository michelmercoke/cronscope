"""Subcommand: tag -- annotate a cron expression with a human-readable label and save to a local registry."""

from __future__ import annotations

import json
import os
from argparse import ArgumentParser, Namespace
from pathlib import Path

DEFAULT_REGISTRY = Path.home() / ".cronscope" / "tags.json"


def _load_registry(path: Path) -> dict[str, str]:
    if path.exists():
        with path.open() as fh:
            return json.load(fh)
    return {}


def _save_registry(path: Path, data: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(data, fh, indent=2)


def add_tag_subparser(subparsers) -> None:
    """Register the 'tag' subcommand."""
    p: ArgumentParser = subparsers.add_parser(
        "tag",
        help="Annotate a cron expression with a label and store it in the local registry.",
    )
    p.add_argument("expression", help="Cron expression (5 fields, quoted).")
    p.add_argument("label", help="Human-readable label for this expression.")
    p.add_argument(
        "--registry",
        default=str(DEFAULT_REGISTRY),
        help="Path to the tags JSON registry (default: ~/.cronscope/tags.json).",
    )
    p.add_argument(
        "--list",
        action="store_true",
        dest="list_tags",
        help="List all tagged expressions and exit.",
    )
    p.add_argument(
        "--remove",
        action="store_true",
        help="Remove the tag for the given expression.",
    )
    p.set_defaults(func=run_tag)


def run_tag(args: Namespace) -> int:
    from cronscope.parser import parse, CronParseError

    registry_path = Path(args.registry)
    registry = _load_registry(registry_path)

    if args.list_tags:
        if not registry:
            print("No tagged expressions found.")
        else:
            for expr, lbl in sorted(registry.items()):
                print(f"{lbl!r:30s}  {expr}")
        return 0

    try:
        parse(args.expression)
    except CronParseError as exc:
        print(f"Invalid cron expression: {exc}")
        return 1

    if args.remove:
        if args.expression in registry:
            del registry[args.expression]
            _save_registry(registry_path, registry)
            print(f"Removed tag for '{args.expression}'.")
        else:
            print(f"No tag found for '{args.expression}'.")
        return 0

    registry[args.expression] = args.label
    _save_registry(registry_path, registry)
    print(f"Tagged '{args.expression}' as {args.label!r}.")
    return 0
