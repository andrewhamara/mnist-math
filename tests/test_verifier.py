from __future__ import annotations

from pathlib import Path

import pytest
from helpers import checks, image_of, judge
from slimconfig import build_output, plain_output

import verifier
from contract import TASKS, TOOLS, ImageInput, Task, Tool
from plugin import read_image
from verifier.digits import LABELS

# Correct


def test_approves_the_right_digits_and_result() -> None:
    a, b = image_of(7), image_of(3)
    verdict = judge(a, b, "multiply", (7, 3), 21)
    assert verdict["valid"] is True and verdict["score"] == 1.0
    assert verdict["message"] == f"All 7 checks hold: image {a} is a 7 and image {b} is a 3; 7 × 3 = 21."


@pytest.mark.parametrize(("operator", "result"), [("add", 10), ("subtract", 4), ("multiply", 21)])
def test_every_operator(operator: str, result: int) -> None:
    assert judge(image_of(7), image_of(3), operator, (7, 3), result)["valid"] is True


# Boundary


def test_subtraction_can_be_negative() -> None:
    assert judge(image_of(2), image_of(9), "subtract", (2, 9), -7)["valid"] is True


def test_the_same_image_twice() -> None:
    n = image_of(6)
    assert judge(n, n, "multiply", (6, 6), 36)["valid"] is True


def test_multiplying_by_zero() -> None:
    assert judge(image_of(0), image_of(8), "multiply", (0, 8), 0)["valid"] is True


def test_the_largest_and_smallest_results() -> None:
    assert judge(image_of(9), image_of(9, 1), "multiply", (9, 9), 81)["valid"] is True
    assert judge(image_of(0), image_of(9), "subtract", (0, 9), -9)["valid"] is True


# Incorrect


def test_a_misread_digit_scores_a_quarter() -> None:
    a, b = image_of(4), image_of(9)
    verdict = judge(a, b, "add", (9, 9), 18)
    assert verdict["valid"] is False and verdict["score"] == 0.25
    assert verdict["message"].startswith(f"first-digit: Image {a} shows a 4 (MNIST's label), not a 9.")
    assert checks(verdict)["arithmetic"] is True and checks(verdict)["result"] is False


def test_right_digits_with_wrong_arithmetic_score_half() -> None:
    verdict = judge(image_of(7), image_of(8), "multiply", (7, 8), 54)
    assert verdict["valid"] is False and verdict["score"] == 0.5
    assert verdict["message"].startswith("arithmetic: 7 × 8 is 56, not 54.")


def test_wrong_digits_with_a_lucky_result_are_caught() -> None:
    # 2 × 3 = 6, read as 1 × 6 = 6: the result is right, both digits are wrong.
    verdict = judge(image_of(2), image_of(3), "multiply", (1, 6), 6)
    assert verdict["valid"] is False and verdict["score"] == 0.5
    assert checks(verdict)["result"] is True and checks(verdict)["first-digit"] is False


def test_both_digits_wrong_scores_zero() -> None:
    verdict = judge(image_of(1), image_of(7), "add", (7, 1), 9)
    assert verdict["valid"] is False and verdict["score"] == 0.0


# Malformed and missing


@pytest.mark.parametrize("read", [(10, 3), (-1, 3), (7, 99)])
def test_a_digit_out_of_range_scores_zero(read: tuple[int, int]) -> None:
    verdict = judge(image_of(7), image_of(3), "add", read, sum(read))
    assert verdict["valid"] is False and verdict["score"] == 0.0 and verdict["message"].startswith("digits-form:")
    assert checks(verdict)["first-digit"] is None


def test_answering_another_question_scores_zero() -> None:
    a, b = image_of(7), image_of(3)
    for changes in ({"first": b, "second": a}, {"operator": "add"}, {"second": image_of(5)}):
        verdict = judge(a, b, "multiply", (7, 3), 21, changes)
        assert verdict["valid"] is False and verdict["score"] == 0.0 and verdict["message"].startswith("same-question:")


@pytest.mark.parametrize(("first", "second"), [(0, 5), (5, 101)])
def test_an_image_that_does_not_exist_scores_zero(first: int, second: int) -> None:
    verdict = judge(first, second, "add", (1, 1), 2)
    assert verdict["valid"] is False and verdict["score"] == 0.0 and verdict["message"].startswith("images:")


# Tool calls


def test_checks_read_image_calls() -> None:
    def verify_input(number: int) -> bool:
        return verifier.verify_input("read_image", build_output({"image": number}, TOOLS[Tool.READ_IMAGE][0]))["valid"]

    assert verify_input(1) and verify_input(100) and not verify_input(0) and not verify_input(101)

    def verify_output(number: int, made: dict) -> dict:
        given, output = TOOLS[Tool.READ_IMAGE]
        return verifier.verify_output("read_image", build_output({"image": number}, given), build_output(made, output), ".")

    found = plain_output(read_image(ImageInput(image=4), Path(".")))
    assert verify_output(4, found)["valid"] is True
    altered = found | {"rows": [*found["rows"][:10], "@" * 28, *found["rows"][11:]]}
    assert "row 11 differs" in verify_output(4, altered)["message"]
    assert verify_output(5, found)["valid"] is False
    assert verify_output(4, found | {"rows": found["rows"][:27]})["valid"] is False


def test_the_show_image_task_is_judged_as_its_tool() -> None:
    found = plain_output(read_image(ImageInput(image=8), Path(".")))
    given, made = TASKS[Task.SHOW_IMAGE]
    verdict = verifier.verify_task("show-image", build_output({"image": 8}, given), build_output(found, made), None, ".")
    assert verdict["valid"] is True


def test_the_verdict_is_the_same_twice() -> None:
    assert judge(1, 2, "add", (3, 4), 8) == judge(1, 2, "add", (3, 4), 8)
    assert LABELS[1] in range(10)
