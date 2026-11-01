# MNIST Math

A `nanoagent.plugin/v0001` plugin: arithmetic on handwritten digits, where the
agent does the seeing. 100 bundled images are real handwritten digits from
the MNIST dataset. The agent's only tool turns an image's pixels into 28 rows
of text, one character per pixel by how dark the ink is, and never says which
digit it is. The agent must read both digits from the shape of their ink,
then add, subtract or multiply them. The verifier holds MNIST's own labels,
which nothing the agent can reach has, and checks each digit and the result.

## Tools

| Tool | Does | Code |
|---|---|---|
| `read_image` | Gives an image's 28x28 pixels as 28 rows of text: `.` for blank paper, then `:` `-` `=` `+` `*` `#` `%` `@` for ink from faintest to darkest. It does not know, and never says, which digit the image shows | `src/plugin/read_image.py` |

### Tasks

| Task | Does | Runner |
|---|---|---|
| `digit-math` | Reads the digits in two images and adds, subtracts or multiplies them, e.g. "multiply the digits in images 4 and 8" | `agent`, with `read_image`; no reference (the verifier holds the labels) |
| `show-image` | Shows one image and the text of its pixels the agent reads | `tool` (`read_image`) |

The page shows the images themselves (`ui/renderers.js`): `digit-math` with
both images, the digit the agent read under each, MNIST's label beside a
wrong one, the arithmetic and the verdict's checks; `show-image` with the
image and its text.

## The task

The input is two image numbers, 1 to 100, and an operator: `add`
(first + second), `subtract` (first - second, which can be negative) or
`multiply` (first × second). The agent submits the question as given, the two
digits it read, and the result of the operator applied to them.

Unlike a detector that names what it sees, `read_image` hands over the raw
pixels: this is the agent's perception task. Here is image 4, as the agent
gets it:

```text
...........:...::=+++@%%-...
........=**%#*#@@@@@@@@@+...
.......-%@@@@@@#***=--@%:...
......:%@#%@#-:.......-:....
.....:@@#.-%:...............
.....+@@%*=-:...............
.....-@@@@@@%+-.............
......::::-#@@@+-...........
............-+@@@+..........
..............-*@@*.........
................+@@=........
.................=@#........
.................=@@-.......
................:%@@:.......
...............-%@@=........
..............-%@@*.........
.......-....:#@@@*..........
.......#+-=*@@@%-...........
.......*@@@@@@+.............
........+#@%+:..............
```

(the 6 blank rows above it and 2 below are left out here). It is a 5.

## Ground truth

The images are the first 10 of each digit, 0 to 9, in the MNIST test set,
numbered 1 to 100 in an order shuffled with a fixed seed, so an image's
number says nothing about its digit. `src/plugin/tools_dev/make_digits.py`
downloads the MNIST test files, checks them against their published MD5 sums,
writes each image's exact pixels to `ui/digits/image-NNN.png`, and writes its
label, its index in the MNIST test set and its rows of text to
`verifier/digits.py`. Only the verifier holds the labels: the tool the agent
calls reads pixels and has no labels to leak. The verifier imports only the
standard library and judges from those labels.

## Constraints

`verifier/task.py` judges a `digit-math` submission against 7 constraints,
in order. Each entry of `details.constraints` is
`{id, constraint, ok, expected, actual, message}`; `ok` is `null` when a
constraint it needs did not hold.

| # | id | What it checks |
|---|---|---|
| 1 | `images` | Both images exist |
| 2 | `same-question` | The submission answers the question asked: its images and operator |
| 3 | `digits-form` | Each digit read is one of 0 to 9 |
| 4 | `arithmetic` | The result is the operator applied to the digits the agent read |
| 5 | `first-digit` | The first image's digit is read right |
| 6 | `second-digit` | The second image's digit is read right |
| 7 | `result` | The result is right |

Valid only when all 7 hold, with score 1.0. Any failure of 1 to 3 scores 0.
Otherwise each digit read right is worth 0.25 and the right result 0.5, at
most 0.99. Constraint 4 tells a reading mistake from an arithmetic mistake.
`read_image`'s every output is checked too: its rows must be the image's
pixels, character for character.

## Limitations

- **Labels are MNIST's.** A few MNIST digits are hard to read even for people; the verifier follows the dataset's label, which is the ground truth by definition.
- **Text, not an image.** The agent reads a picture written out as characters, which tests reading shapes from a grid rather than vision on images.
- **Lucky results.** A wrong pair of digits can give the right result (2 × 3 and 1 × 6 are both 6); the digit checks catch that, and the score gives the result half.
- **A fixed set of 100 images** could in principle be memorized; other MNIST images make new sets.

## Data

The images are from the MNIST database of handwritten digits by Yann LeCun,
Corinna Cortes and Christopher J. C. Burges, available under the Creative
Commons Attribution-Share Alike 3.0 license; the images and labels in
`ui/digits/` and `verifier/digits.py` are under that license. The code is
under the MIT license in `LICENSE`.

## Layout

```text
.
├── nanoagent.yaml   # manifest: id, runtime, permissions (no network), tools, tasks and the agent's instructions
├── contract.py      # each tool's and task's typed input and output: slimconfig Output classes
├── README.md
├── LICENSE
├── pyproject.toml   # pillow reads the images' PNGs
├── uv.lock
├── .gitignore
├── .env             # needed environment variable names (none here)
├── src/plugin/      # the MCP server (__main__.py), read_image.py, and tools_dev/make_digits.py
├── tests/           # the tool, the verifier, and scripted agents (an exact one, and one that reads the text)
├── ui/              # digits/ (the 100 PNGs, which read_image reads and the page shows) and
│                    #   renderers.js/.css (the images on the result cards)
├── product/         # the product page a catalog shows: product.yaml and icon.svg
└── verifier/        # deterministic verifier: digits.py (the labels and rows), one module per tool,
                     #   and task.py for digit-math
```

## Develop and run

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv run python -m plugin.tools_dev.make_digits   # downloads MNIST's test set and rewrites the same files
```

NanoAgent passes the folder the plugin may write to as `NANOAGENT_WORKSPACE`;
this plugin writes nothing there.
