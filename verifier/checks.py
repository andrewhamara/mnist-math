"""Checks shared by the verifiers. Pure functions of contract instances and the images' truth."""

from .digits import COUNT

# operator -> (its symbol, its function)
OPERATORS = {
    "add": ("+", lambda a, b: a + b),
    "subtract": ("-", lambda a, b: a - b),
    "multiply": ("×", lambda a, b: a * b),
}


def result(valid, message, *, score=None, **details):
    return {
        "valid": valid,
        "score": float(valid) if score is None else score,
        "message": message,
        "details": details,
    }


def image_problem(number):
    if not 1 <= number <= COUNT:
        return f"no image {number}: the images are 1 to {COUNT}"
    return None
