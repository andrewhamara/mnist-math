"""Writes the bundled images, ui/digits/image-NNN.png, and their labels and text to verifier/digits.py.

    uv run python -m plugin.tools_dev.make_digits [<folder with the MNIST test files>]

The images are the first 10 of each digit, 0 to 9, in the MNIST test set (t10k), numbered 1 to 100
in an order shuffled with a fixed seed, so an image's number says nothing about its digit. The
MNIST files are downloaded from PyTorch's mirror unless a folder holding them is given, and are
checked against their published MD5 sums either way. Running it again writes the same files.
"""

from __future__ import annotations

import gzip
import hashlib
import random
import struct
import sys
import tempfile
import urllib.request
from pathlib import Path

from PIL import Image

from plugin.read_images import COUNT, DIGITS, SIDE, as_text

ROOT = Path(__file__).resolve().parents[3]
TRUTH = ROOT / "verifier" / "digits.py"
MIRROR = "https://ossci-datasets.s3.amazonaws.com/mnist/"
# torchvision's published MD5 sums of the MNIST test set.
FILES = {
    "t10k-images-idx3-ubyte.gz": "9fb629c4189551a2d022fa330f9573f3",
    "t10k-labels-idx1-ubyte.gz": "ec29112dd5afa0611ce80d1b7f02629c",
}
PER_DIGIT = 10
SEED = 480


def mnist(folder: Path) -> tuple[list[bytes], list[int]]:
    """The MNIST test set's images (784 bytes each) and labels, from ``folder``, downloading what is missing."""
    for name, md5 in FILES.items():
        path = folder / name
        if not path.is_file():
            urllib.request.urlretrieve(MIRROR + name, path)
        if hashlib.md5(path.read_bytes()).hexdigest() != md5:
            raise SystemExit(f"{path} is not MNIST's {name}: its MD5 is not {md5}")
    images = gzip.decompress((folder / "t10k-images-idx3-ubyte.gz").read_bytes())
    labels = gzip.decompress((folder / "t10k-labels-idx1-ubyte.gz").read_bytes())
    count, rows, cols = struct.unpack(">III", images[4:16])
    if (struct.unpack(">I", labels[4:8])[0], rows, cols) != (count, SIDE, SIDE):
        raise SystemExit("the MNIST files do not hold 28x28 images with one label each")
    size = SIDE * SIDE
    return [images[16 + i * size : 16 + (i + 1) * size] for i in range(count)], list(labels[8:])


def main() -> None:
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(tempfile.mkdtemp(prefix="mnist-"))
    images, labels = mnist(folder)
    chosen = [index for digit in range(10) for index in [i for i, label in enumerate(labels) if label == digit][:PER_DIGIT]]
    random.Random(SEED).shuffle(chosen)
    if len(chosen) != COUNT:
        raise SystemExit(f"chose {len(chosen)} images, not {COUNT}")
    DIGITS.mkdir(parents=True, exist_ok=True)
    truth = []
    for number, index in enumerate(chosen, 1):
        image = Image.frombytes("L", (SIDE, SIDE), images[index])
        path = DIGITS / f"image-{number:03d}.png"
        image.save(path, optimize=True)
        with Image.open(path) as saved:
            if saved.tobytes() != images[index]:
                raise SystemExit(f"{path} does not hold MNIST test image {index} exactly")
            truth.append((number, labels[index], index, as_text(saved)))
    lines = [
        '"""Each bundled image\'s MNIST label, its index in the MNIST test set, and its rows as read_images gives',
        'them, as src/plugin/tools_dev/make_digits.py wrote them. Generated: do not edit."""',
        "",
        f"COUNT = {COUNT}",
        "LABELS = {",
        *(f"    {number}: {label}," for number, label, _, _ in truth),
        "}",
        "MNIST_INDEX = {",
        *(f"    {number}: {index}," for number, _, index, _ in truth),
        "}",
        "ROWS = {",
    ]
    for number, _, _, rows in truth:
        lines.append(f"    {number}: (")
        lines += [f"        {row!r}," for row in rows]
        lines.append("    ),")
    lines.append("}")
    TRUTH.write_text("\n".join(lines) + "\n")
    print(f"wrote {COUNT} images to {DIGITS} and their labels to {TRUTH}")


if __name__ == "__main__":
    main()
