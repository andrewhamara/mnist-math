from __future__ import annotations

from collections import Counter
from pathlib import Path

import pytest
from PIL import Image

from contract import ImagesInput
from plugin import read_images
from plugin.read_images import INK, as_text
from verifier.digits import LABELS, ROWS

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("number", range(1, 101))
def test_gives_each_images_pixels_as_its_rows(tmp_path: Path, number: int) -> None:
    found = read_images(ImagesInput(images=[number]), tmp_path)
    assert (found.width, found.height) == (28, 28) and [item.image for item in found.pictures] == [number]
    rows = found.pictures[0].rows
    assert rows == list(ROWS[number]) and all(len(row) == 28 and set(row) <= set(INK) for row in rows)


def test_gives_two_images_in_the_order_asked_and_the_same_image_twice(tmp_path: Path) -> None:
    found = read_images(ImagesInput(images=[8, 4]), tmp_path)
    assert [(item.image, item.rows) for item in found.pictures] == [(8, list(ROWS[8])), (4, list(ROWS[4]))]
    twice = read_images(ImagesInput(images=[6, 6]), tmp_path)
    assert [item.image for item in twice.pictures] == [6, 6]


@pytest.mark.parametrize("images", [[], [1, 2, 3]])
def test_refuses_other_than_one_or_two_images(tmp_path: Path, images: list[int]) -> None:
    with pytest.raises(ValueError, match="one or two images"):
        read_images(ImagesInput(images=images), tmp_path)


def test_ten_images_of_each_digit() -> None:
    assert Counter(LABELS.values()) == {digit: 10 for digit in range(10)}


@pytest.mark.parametrize("number", [0, 101, -1])
def test_refuses_an_image_that_is_not_bundled(tmp_path: Path, number: int) -> None:
    with pytest.raises(ValueError, match="no image"):
        read_images(ImagesInput(images=[4, number]), tmp_path)


def test_ink_levels_run_from_blank_to_darkest() -> None:
    image = Image.new("L", (28, 28), 0)
    image.putpixel((0, 0), 255)
    image.putpixel((1, 0), 128)
    rows = as_text(image)
    assert rows[0][:3] == "@+." and rows[1] == "." * 28


def test_refuses_an_image_that_is_not_28x28_grayscale() -> None:
    with pytest.raises(ValueError, match="28x28 grayscale"):
        as_text(Image.new("RGB", (28, 28)))
    with pytest.raises(ValueError, match="28x28 grayscale"):
        as_text(Image.new("L", (32, 32)))


def test_nothing_the_agent_can_reach_holds_the_labels() -> None:
    # The plugin the agent calls has no labels: none of its code imports the verifier or uses its table.
    for path in (ROOT / "src").rglob("*.py"):
        if path.name == "make_digits.py":
            continue  # the generator writes the labels; the plugin never runs it
        code = [line for line in path.read_text().splitlines() if not line.lstrip().startswith("#")]
        imports = [line for line in code if line.lstrip().startswith(("import ", "from "))]
        assert not any("verifier" in line for line in imports), path
        assert not any("LABELS" in line for line in code), path
    # The image files are named by number only, in shuffled order: the numbers do not follow the labels.
    assert sorted(path.name for path in (ROOT / "ui" / "digits").iterdir()) == [f"image-{n:03d}.png" for n in range(1, 101)]
    assert [LABELS[n] for n in range(1, 101)] != sorted(LABELS.values())
