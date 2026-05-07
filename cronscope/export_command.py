"""High-level export command wiring exporter + output_writer together."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from cronscope.exporter import ExportFormat, export
from cronscope.output_writer import detect_format_from_path, write_output
from cronscope.parser import parse
from cronscope.scheduler import next_runs

_DEFAULT_COUNT = 10
_DEFAULT_FORMAT: ExportFormat = "text"


def run_export(
    expression: str,
    count: int = _DEFAULT_COUNT,
    fmt: Optional[str] = None,
    output_path: Optional[str] = None,
    now: Optional[datetime] = None,
) -> str:
    """Parse *expression*, compute next runs, export and write output.

    Parameters
    ----------
    expression:
        A standard 5-field cron expression.
    count:
        Number of upcoming run times to compute.
    fmt:
        One of ``'json'``, ``'csv'``, or ``'text'``.  When *None* the
        format is inferred from *output_path*; falls back to ``'text'``.
    output_path:
        Optional file path to write the result.  Writes to stdout when
        *None*.
    now:
        Reference time for relative labels.  Defaults to UTC now.

    Returns
    -------
    str
        The exported content string (useful for testing).
    """
    if now is None:
        now = datetime.now(tz=timezone.utc)

    resolved_fmt: ExportFormat = (
        fmt
        or detect_format_from_path(output_path)
        or _DEFAULT_FORMAT
    )  # type: ignore[assignment]

    cron = parse(expression)
    runs: List[datetime] = next_runs(cron, now=now, count=count)
    content = export(runs, now=now, fmt=resolved_fmt, expression=expression)
    write_output(content, path=output_path)
    return content
