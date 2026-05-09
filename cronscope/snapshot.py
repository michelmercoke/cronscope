"""Snapshot: save and compare cron schedule runs at a point in time."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from cronscope.scheduler import next_runs
from cronscope.parser import parse


@dataclass
class Snapshot:
    expression: str
    taken_at: str  # ISO-8601
    runs: List[str]  # ISO-8601 datetimes
    label: Optional[str] = None


@dataclass
class SnapshotDiff:
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    unchanged: List[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed)


def take_snapshot(
    expression: str,
    count: int = 10,
    start: Optional[datetime] = None,
    label: Optional[str] = None,
) -> Snapshot:
    """Generate a snapshot of the next *count* runs for *expression*."""
    expr = parse(expression)
    start = start or datetime.now().replace(second=0, microsecond=0)
    runs = next_runs(expr, count=count, start=start)
    return Snapshot(
        expression=expression,
        taken_at=datetime.now().isoformat(timespec="seconds"),
        runs=[r.isoformat(timespec="seconds") for r in runs],
        label=label,
    )


def save_snapshot(snapshot: Snapshot, path: Path) -> None:
    """Persist a snapshot to a JSON file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "expression": snapshot.expression,
        "taken_at": snapshot.taken_at,
        "runs": snapshot.runs,
        "label": snapshot.label,
    }
    path.write_text(json.dumps(data, indent=2))


def load_snapshot(path: Path) -> Snapshot:
    """Load a snapshot from a JSON file."""
    data = json.loads(Path(path).read_text())
    return Snapshot(
        expression=data["expression"],
        taken_at=data["taken_at"],
        runs=data["runs"],
        label=data.get("label"),
    )


def compare_snapshots(old: Snapshot, new: Snapshot) -> SnapshotDiff:
    """Return which runs were added, removed, or unchanged between two snapshots."""
    old_set = set(old.runs)
    new_set = set(new.runs)
    return SnapshotDiff(
        added=sorted(new_set - old_set),
        removed=sorted(old_set - new_set),
        unchanged=sorted(old_set & new_set),
    )
