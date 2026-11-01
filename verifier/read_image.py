"""read_image: the rows it gives are the image's pixels, character for character."""

from .checks import image_problem, result
from .digits import ROWS

SIDE = 28


def verify_input(value):
    problem = image_problem(value.image)
    if problem:
        return result(False, problem)
    return result(True, "input is valid")


def verify_output(input_value, output_value, workspace):
    """``output_value``: a contract ImageOutput, held to the image's true rows."""
    number = input_value.image
    if output_value.image != number:
        return result(False, f"the output is for image {output_value.image}, not image {number}")
    if (output_value.width, output_value.height) != (SIDE, SIDE):
        return result(False, f"an image is {SIDE}x{SIDE} px, not {output_value.width}x{output_value.height}")
    rows = list(output_value.rows)
    if rows != list(ROWS[number]):
        wrong = [y for y, (row, true) in enumerate(zip(rows, ROWS[number])) if row != true]
        where = f"row {wrong[0] + 1}" if wrong else f"{len(rows)} rows, not {SIDE}"
        return result(False, f"image {number}'s rows are not its pixels: {where} differs")
    return result(True, f"image {number}'s {SIDE} rows are its pixels")
