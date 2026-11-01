"""Scripted agents, no model, each run as NanoAgent runs the task: read_images, then submit.

An exact agent, which knows MNIST's labels, must pass every question. A reading agent sees only what
the model sees, read_images's text: it takes each digit from the most similar text among the other 99
images (leave-one-out nearest neighbor). Its verdicts must agree with whether it read right, and it
shows that the text alone carries the digit.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from helpers import judge

from contract import ImagesInput
from plugin import read_images
from plugin.read_images import INK
from verifier.digits import LABELS

OPERATORS = {"add": lambda a, b: a + b, "subtract": lambda a, b: a - b, "multiply": lambda a, b: a * b}


def ink(number: int) -> list[int]:
    rows = read_images(ImagesInput(images=[number]), Path(".")).pictures[0].rows
    return [INK.index(char) for row in rows for char in row]


TEXTS = {number: ink(number) for number in range(1, 101)}


def nearest(number: int) -> int:
    """The label of the other image whose text is closest to ``number``'s: a reader of text, not of labels."""
    mine = TEXTS[number]
    others = (n for n in TEXTS if n != number)
    closest = min(others, key=lambda n: sum((a - b) ** 2 for a, b in zip(mine, TEXTS[n])))
    return LABELS[closest]


READ = {number: nearest(number) for number in TEXTS}


@pytest.mark.parametrize("operator", sorted(OPERATORS))
def test_an_exact_agent_passes_every_question(operator: str) -> None:
    for first in range(1, 101):
        second = first % 100 + 1
        digits = (LABELS[first], LABELS[second])
        assert judge(first, second, operator, digits, OPERATORS[operator](*digits))["valid"] is True


@pytest.mark.parametrize("operator", sorted(OPERATORS))
def test_a_reading_agent_is_judged_by_what_it_read(operator: str) -> None:
    for first in range(1, 101):
        second = first % 100 + 1
        digits = (READ[first], READ[second])
        verdict = judge(first, second, operator, digits, OPERATORS[operator](*digits))
        right = digits == (LABELS[first], LABELS[second])
        assert verdict["valid"] is right


def test_the_text_alone_carries_the_digit() -> None:
    correct = sum(READ[n] == LABELS[n] for n in READ)
    print(f"leave-one-out nearest neighbor on read_images's text reads {correct} of 100 digits right")
    assert correct >= 70
