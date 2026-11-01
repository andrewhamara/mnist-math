"""read_image: a bundled image's pixels as text, for an agent to read the digit from. It never says which
digit the image shows; the plugin does not know: only the verifier holds MNIST's labels.

Each pixel, 0 (blank paper) to 255 (darkest ink), becomes one character by its ink level in nine
steps: '.' for no ink, then ':', '-', '=', '+', '*', '#', '%', '@'.
"""

from __future__ import annotations

from functools import cache
from pathlib import Path

from PIL import Image

from contract import ImageInput, ImageOutput

# The images live in ui/digits/, where the plugin's page shows them too.
DIGITS = Path(__file__).resolve().parents[2] / "ui" / "digits"
COUNT = 100
SIDE = 28
INK = ".:-=+*#%@"


def image_path(number: int) -> Path:
    path = DIGITS / f"image-{number:03d}.png"
    if not 1 <= number <= COUNT or not path.is_file():
        raise ValueError(f"no image {number}: the images are 1 to {COUNT}")
    return path


def as_text(image: Image.Image) -> list[str]:
    """The image's rows, one character per pixel by its ink level."""
    if image.mode != "L" or image.size != (SIDE, SIDE):
        raise ValueError(f"an image must be {SIDE}x{SIDE} grayscale, not {image.size[0]}x{image.size[1]} {image.mode}")
    pixels = image.load()
    steps = len(INK) - 1
    return ["".join(INK[(pixels[x, y] * steps + 127) // 255] for x in range(SIDE)) for y in range(SIDE)]


@cache
def _rows(number: int) -> tuple[str, ...]:
    """The image's rows, read once: the bundled images never change."""
    with Image.open(image_path(number)) as image:
        return tuple(as_text(image))


def read_image(given: ImageInput, workspace: Path) -> ImageOutput:
    """The image's pixels as 28 rows of text."""
    return ImageOutput(image=given.image, width=SIDE, height=SIDE, rows=list(_rows(given.image)))
