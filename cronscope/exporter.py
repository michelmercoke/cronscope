"""Export cron schedule results to various formats (JSON, CSV, plain text)."""

from __future__ import annotations

import csv
import io
import json
from datetime import datetime
from typing import List, Literal

from cronscope.formatter import format_datetime, format_relative

ExportFormat = Literal["json", "csv", "text"]


def _runs_to_dicts(runs: List[datetime], now: datetime) -> List[dict]:
    """Convert a list of datetimes to serialisable dicts."""
    result = []
    for i, dt in enumerate(runs, start=1):
        result.append(
            {
                "index": i,
                "datetime": format_datetime(dt),
                "relative": format_relative(dt, now),
                "timestamp": int(dt.timestamp()),
            }
        )
    return result


def export_json(runs: List[datetime], now: datetime, expression: str) -> str:
    """Serialise schedule runs to a JSON string."""
    payload = {
        "expression": expression,
        "generated_at": format_datetime(now),
        "count": len(runs),
        "runs": _runs_to_dicts(runs, now),
    }
    return json.dumps(payload, indent=2)


def export_csv(runs: List[datetime], now: datetime) -> str:
    """Serialise schedule runs to a CSV string."""
    output = io.StringIO()
    writer = csv.DictWriter(
        output, fieldnames=["index", "datetime", "relative", "timestamp"]
    )
    writer.writeheader()
    writer.writerows(_runs_to_dicts(runs, now))
    return output.getvalue()


def export_text(runs: List[datetime], now: datetime) -> str:
    """Serialise schedule runs to a plain-text list."""
    lines = []
    for entry in _runs_to_dicts(runs, now):
        lines.append(f"{entry['index']:>3}. {entry['datetime']}  ({entry['relative']})")
    return "\n".join(lines)


def export(
    runs: List[datetime],
    now: datetime,
    fmt: ExportFormat = "text",
    expression: str = "",
) -> str:
    """Dispatch to the appropriate exporter."""
    if fmt == "json":
        return export_json(runs, now, expression)
    if fmt == "csv":
        return export_csv(runs, now)
    return export_text(runs, now)
