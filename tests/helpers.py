"""Shared test helpers: images by label, and judging a submission as NanoAgent's sandbox would."""

from __future__ import annotations

from slimconfig import build_output

import verifier
from contract import TASKS, Task
from verifier.digits import LABELS


def image_of(digit: int, skip: int = 0) -> int:
    """The number of an image showing ``digit`` (the skip-th one)."""
    return [number for number, label in sorted(LABELS.items()) if label == digit][skip]


def judge(first: int, second: int, operator: str, read: tuple[int, int], result: int, changes: dict | None = None) -> dict:
    given, made = TASKS[Task.DIGIT_MATH]
    question = {"first": first, "second": second, "operator": operator}
    answer = question | {"first_digit": read[0], "second_digit": read[1], "result": result} | (changes or {})
    return verifier.verify_task("digit-math", build_output(question, given), build_output(answer, made), None, ".")


def checks(verdict: dict) -> dict:
    return {item["id"]: item["ok"] for item in verdict["details"]["constraints"]}
