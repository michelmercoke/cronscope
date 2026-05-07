"""Write exported content to stdout or a file path."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional


def write_output(content: str, path: Optional[str] = None) -> None:
    """Write *content* to *path* if given, otherwise to stdout.

    Parameters
    ----------
    content:
        The text to write.
    path:
        Optional file-system path.  Parent directories are created
        automatically.  If ``None`` or empty, output goes to stdout.
    """
    if not path:
        sys.stdout.write(content)
        if not content.endswith("\n"):
            sys.stdout.write("\n")
        return

    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")


def detect_format_from_path(path: Optional[str]) -> Optional[str]:
    """Infer export format from a file extension.

    Returns ``None`` when the extension is unknown or no path is given.
    """
    if not path:
        return None
    suffix = Path(path).suffix.lower()
    mapping = {
        ".json": "json",
        ".csv": "csv",
        ".txt": "text",
        ".text": "text",
    }
    return mapping.get(suffix)
