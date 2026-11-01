"""Each tool's and task's typed input and output (see nanoagent.plugin.v0001.contract): declarations only."""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output


class Tool(Enum):
    READ_IMAGE = "read_image"


class Task(Enum):
    DIGIT_MATH = "digit-math"
    SHOW_IMAGE = "show-image"


class Operator(Enum):
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"


IMAGE = "A bundled image's number, 1 to 100; each shows one handwritten digit"
ROWS = (
    "The image's 28 rows of 28 pixels, top to bottom, one string per row: '.' is blank paper and "
    "':', '-', '=', '+', '*', '#', '%', '@' are ink from faintest to darkest"
)


@dataclass
class ImageInput(Output):
    image: Annotated[int, IMAGE]


@dataclass
class ImageOutput(Output):
    image: Annotated[int, IMAGE]
    width: Annotated[int, "The image's width in pixels"]
    height: Annotated[int, "The image's height in pixels"]
    rows: Annotated[list[str], ROWS]


@dataclass
class MathInput(Output):
    first: Annotated[int, "The first image's number, 1 to 100"]
    second: Annotated[int, "The second image's number, 1 to 100"]
    operator: Annotated[
        Operator, "add: first + second; subtract: first - second; multiply: first * second, of the images' digits"
    ]


@dataclass
class MathOutput(Output):
    first: Annotated[int, "The first image's number, as given"]
    second: Annotated[int, "The second image's number, as given"]
    operator: Annotated[Operator, "The operator, as given"]
    first_digit: Annotated[int, "The digit, 0 to 9, that the first image shows, as read from its rows"]
    second_digit: Annotated[int, "The digit, 0 to 9, that the second image shows, as read from its rows"]
    result: Annotated[int, "The operator applied to first_digit and second_digit, e.g. 7 * 3 = 21; may be negative"]


TOOLS = {
    Tool.READ_IMAGE: (ImageInput, ImageOutput),
}
TASKS = {
    Task.DIGIT_MATH: (MathInput, MathOutput),
    Task.SHOW_IMAGE: (ImageInput, ImageOutput),
}
