"""The digit-math task's verdict: the digits the agent read and its result, against MNIST's labels.

Seven constraints, in order; every one must hold. Each is {id, constraint, ok, expected, actual,
message}: ok is true, false, or null when a constraint it needs did not hold. Any failure of 1 to 3
scores 0. Otherwise each digit read right is worth 0.25 and the right result 0.5, at most 0.99
unless all seven hold.
"""

from .checks import OPERATORS, image_problem, result
from .digits import LABELS, MNIST_INDEX

CONSTRAINTS = (
    ("images", "Both images exist"),
    ("same-question", "The submission answers the question asked: its images and operator"),
    ("digits-form", "Each digit read is one of 0 to 9"),
    ("arithmetic", "The result is the operator applied to the digits the agent read"),
    ("first-digit", "The first image's digit is read right"),
    ("second-digit", "The second image's digit is read right"),
    ("result", "The result is right"),
)
GUARDS = 3  # constraints 1 to 3: a failure scores 0


def verify_task(arguments, output, reference, workspace):
    """``arguments``: a contract MathInput; ``output``: MathOutput. No reference: the verifier holds the labels."""
    checks = {}

    def put(key, ok, expected=None, actual=None, message=""):
        checks[key] = {"ok": ok, "expected": expected, "actual": actual, "message": "" if ok else message}

    first, second, name = arguments.first, arguments.second, arguments.operator.value
    symbol, apply = OPERATORS[name]
    problem = image_problem(first) or image_problem(second)
    put("images", problem is None, message=problem)
    asked = (first, second, name)
    answered = (output.first, output.second, output.operator.value)
    put(
        "same-question",
        answered == asked,
        list(asked),
        list(answered),
        f"The question was {name} images {first} and {second}; the submission answers {answered[2]} images "
        f"{answered[0]} and {answered[1]}.",
    )
    read = (output.first_digit, output.second_digit)
    bad = [digit for digit in read if not 0 <= digit <= 9]
    put("digits-form", not bad, actual=list(read), message=f"{bad[0]} is not a digit: a digit is 0 to 9." if bad else "")
    expected = None
    if problem is None:
        truth = (LABELS[first], LABELS[second])
        expected = {"first_digit": truth[0], "second_digit": truth[1], "result": apply(*truth)}
    if not bad:
        own = apply(*read)
        put(
            "arithmetic",
            output.result == own,
            own,
            output.result,
            f"{read[0]} {symbol} {read[1]} is {own}, not {output.result}.",
        )
    if expected is not None and not bad:
        for key, number, digit, true in (("first-digit", first, read[0], truth[0]), ("second-digit", second, read[1], truth[1])):
            put(key, digit == true, true, digit, f"Image {number} shows a {true} (MNIST's label), not a {digit}.")
        put(
            "result",
            output.result == expected["result"],
            expected["result"],
            output.result,
            f"{truth[0]} {symbol} {truth[1]} is {expected['result']}, not {output.result}.",
        )

    constraints = []
    for key, text in CONSTRAINTS:
        check = checks.get(key)
        if check is None:
            waiting = next(k for k, _ in CONSTRAINTS if checks.get(k, {"ok": True})["ok"] is False)
            check = {"ok": None, "expected": None, "actual": None, "message": f"Not checked: {waiting} did not hold."}
        constraints.append({"id": key, "constraint": text, **check})
    failed = [item for item in constraints if item["ok"] is False]
    details = {"constraints": constraints, "expected": expected}
    if problem is None:
        details["mnist_index"] = [MNIST_INDEX[first], MNIST_INDEX[second]]
    if not failed:
        return result(
            True,
            f"All {len(CONSTRAINTS)} checks hold: image {first} is a {truth[0]} and image {second} is a {truth[1]}; "
            f"{truth[0]} {symbol} {truth[1]} = {expected['result']}.",
            **details,
        )
    first_failed = failed[0]
    message = f"{first_failed['id']}: {first_failed['message']}" + (f" (+{len(failed) - 1} more)" if len(failed) > 1 else "")
    if any(item["ok"] is not True for item in constraints[:GUARDS]):
        return result(False, message, score=0.0, **details)
    ok = {item["id"]: item["ok"] for item in constraints}
    score = 0.25 * ok["first-digit"] + 0.25 * ok["second-digit"] + 0.5 * ok["result"]
    return result(False, message, score=min(0.99, score), **details)
