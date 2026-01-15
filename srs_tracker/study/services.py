from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class Sm2Result:
    repetitions: int
    interval_days: int
    ease_factor: float
    next_review_at: date


def sm2_calculate(
    *,
    quality: int,
    repetitions: int,
    interval_days: int,
    ease_factor: float,
    review_date: date,
) -> Sm2Result:
    if quality < 0 or quality > 5:
        raise ValueError("quality must be in range 0..5")

    # Update ease factor
    q = quality
    ef = ease_factor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    if ef < 1.3:
        ef = 1.3

    if quality < 3:
        reps = 0
        interval = 1
    else:
        reps = repetitions + 1
        if reps == 1:
            interval = 1
        elif reps == 2:
            interval = 6
        else:
            interval = int(round(interval_days * ef)) if interval_days > 0 else 6

    next_date = review_date + timedelta(days=interval)
    return Sm2Result(repetitions=reps, interval_days=interval, ease_factor=ef, next_review_at=next_date)
