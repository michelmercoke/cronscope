"""Detect anomalous gaps or bursts in a cron schedule."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from cronscope.scheduler import next_runs
from cronscope.parser import parse


@dataclass
class AnomalyReport:
    expression: str
    total_runs: int
    mean_gap_seconds: float
    std_gap_seconds: float
    gaps: List[float] = field(default_factory=list)
    burst_windows: List[tuple] = field(default_factory=list)  # (start, end, count)
    long_gaps: List[tuple] = field(default_factory=list)      # (start, end, seconds)


def _mean(values: List[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _std(values: List[float], mean: float) -> float:
    if len(values) < 2:
        return 0.0
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    return variance ** 0.5


def detect_anomalies(
    expression: str,
    start: datetime,
    count: int = 500,
    burst_threshold: int = 5,
    burst_window_minutes: int = 10,
    long_gap_multiplier: float = 3.0,
) -> AnomalyReport:
    """Analyse *count* upcoming runs and flag bursts and long gaps."""
    expr = parse(expression)
    runs = next_runs(expr, start, count)

    if len(runs) < 2:
        return AnomalyReport(
            expression=expression,
            total_runs=len(runs),
            mean_gap_seconds=0.0,
            std_gap_seconds=0.0,
        )

    gaps: List[float] = [
        (runs[i + 1] - runs[i]).total_seconds() for i in range(len(runs) - 1)
    ]
    mean_gap = _mean(gaps)
    std_gap = _std(gaps, mean_gap)
    threshold_long = mean_gap + long_gap_multiplier * std_gap

    long_gaps = []
    for i, g in enumerate(gaps):
        if g > threshold_long:
            long_gaps.append((runs[i], runs[i + 1], g))

    # Burst detection: sliding window of burst_window_minutes
    burst_secs = burst_window_minutes * 60
    burst_windows = []
    i = 0
    while i < len(runs):
        window = [runs[i]]
        j = i + 1
        while j < len(runs) and (runs[j] - runs[i]).total_seconds() <= burst_secs:
            window.append(runs[j])
            j += 1
        if len(window) >= burst_threshold:
            burst_windows.append((window[0], window[-1], len(window)))
            i = j
        else:
            i += 1

    return AnomalyReport(
        expression=expression,
        total_runs=len(runs),
        mean_gap_seconds=mean_gap,
        std_gap_seconds=std_gap,
        gaps=gaps,
        burst_windows=burst_windows,
        long_gaps=long_gaps,
    )
