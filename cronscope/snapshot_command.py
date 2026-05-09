"""CLI sub-command: snapshot — save and diff cron schedule snapshots."""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from cronscope.parser import parse, CronParseError
from cronscope.snapshot import (
    take_snapshot,
    save_snapshot,
    load_snapshot,
    compare_snapshots,
)


def add_snapshot_subparser(subparsers) -> None:  # noqa: ANN001
    p = subparsers.add_parser("snapshot", help="Save or diff cron schedule snapshots")
    sub = p.add_subparsers(dest="snapshot_cmd", required=True)

    # --- save ---
    save_p = sub.add_parser("save", help="Save a snapshot to a file")
    save_p.add_argument("expression", help="Cron expression")
    save_p.add_argument("file", help="Output JSON file path")
    save_p.add_argument("-n", "--count", type=int, default=10, metavar="N")
    save_p.add_argument("--label", default=None)
    save_p.add_argument("--start", default=None, metavar="ISO")

    # --- diff ---
    diff_p = sub.add_parser("diff", help="Diff two snapshot files")
    diff_p.add_argument("old", help="Older snapshot JSON file")
    diff_p.add_argument("new", help="Newer snapshot JSON file")

    p.set_defaults(func=run_snapshot)


def run_snapshot(args) -> int:  # noqa: ANN001
    if args.snapshot_cmd == "save":
        return _run_save(args)
    if args.snapshot_cmd == "diff":
        return _run_diff(args)
    return 1


def _run_save(args) -> int:  # noqa: ANN001
    try:
        parse(args.expression)
    except CronParseError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    start = None
    if args.start:
        try:
            start = datetime.fromisoformat(args.start)
        except ValueError:
            print(f"Error: invalid --start date '{args.start}'", file=sys.stderr)
            return 1

    snap = take_snapshot(
        args.expression,
        count=args.count,
        start=start,
        label=args.label,
    )
    save_snapshot(snap, Path(args.file))
    print(f"Snapshot saved to {args.file} ({len(snap.runs)} runs).")
    return 0


def _run_diff(args) -> int:  # noqa: ANN001
    try:
        old = load_snapshot(Path(args.old))
        new = load_snapshot(Path(args.new))
    except (FileNotFoundError, KeyError, ValueError) as exc:
        print(f"Error loading snapshot: {exc}", file=sys.stderr)
        return 1

    result = compare_snapshots(old, new)
    print(f"Unchanged : {len(result.unchanged)}")
    for ts in result.added:
        print(f"  + {ts}")
    for ts in result.removed:
        print(f"  - {ts}")
    if not result.has_changes:
        print("No changes between snapshots.")
    return 0
