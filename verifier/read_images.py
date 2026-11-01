"""read_images: the rows it gives are each image's pixels, character for character."""

from .checks import image_problem, result
from .digits import ROWS

SIDE = 28


def verify_input(value):
    if not 1 <= len(value.images) <= 2:
        return result(False, f"ask for one or two images, not {len(value.images)}")
    for number in value.images:
        problem = image_problem(number)
        if problem:
            return result(False, problem)
    return result(True, "input is valid")


def verify_output(input_value, output_value, workspace):
    """``output_value``: a contract ImagesOutput, held to each image's true rows."""
    asked = list(input_value.images)
    given = [item.image for item in output_value.pictures]
    if given != asked:
        return result(False, f"the output is for images {given}, not {asked}")
    if (output_value.width, output_value.height) != (SIDE, SIDE):
        return result(False, f"an image is {SIDE}x{SIDE} px, not {output_value.width}x{output_value.height}")
    for item in output_value.pictures:
        rows = list(item.rows)
        if rows != list(ROWS[item.image]):
            wrong = [y for y, (row, true) in enumerate(zip(rows, ROWS[item.image])) if row != true]
            where = f"row {wrong[0] + 1}" if wrong else f"{len(rows)} rows, not {SIDE}"
            return result(False, f"image {item.image}'s rows are not its pixels: {where} differs")
    return result(True, f"the rows of image{'s' if len(asked) > 1 else ''} {' and '.join(map(str, asked))} are their pixels")
