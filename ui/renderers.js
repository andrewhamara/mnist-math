// How this plugin's page draws its tasks' outputs: the digit images themselves (ui/digits/), drawn
// large with their pixels kept sharp. A digit-math answer shows both images with the digit the agent
// read under each (and MNIST's label beside a wrong one), the arithmetic, and the verdict's checks;
// show-image shows one image and the text of its pixels that the agent reads.
import { disclosure, h } from "./kit/components.js";

const SYMBOLS = { add: "+", subtract: "−", multiply: "×" };
const file = (n) => `digits/image-${String(n).padStart(3, "0")}.png`;

const digitImage = (n) => h("img", { class: "digit-img", src: file(n), alt: `Image ${n}`, width: 28, height: 28 });

const MARKS = { true: ["✓", "ok"], false: ["✗", "bad"], null: ["·", "skipped"] };

/** The verdict's checks, each with its mark and, when it failed or was skipped, why. */
const checks = (constraints) =>
  h(
    "ol",
    { class: "digit-checks" },
    constraints.map(({ id, constraint, ok, message }) => {
      const [mark, tone] = MARKS[String(ok)];
      return h(
        "li",
        { class: `digit-check ${tone}` },
        h("span", { class: "digit-mark", text: mark }),
        h("span", {}, h("code", { text: id }), ` ${constraint}`, message ? h("span", { class: "digit-why", text: message }) : null),
      );
    }),
  );

/** One image with what the agent read, and MNIST's label when they differ. */
function tile(n, read, truth) {
  const right = truth === null || truth === undefined || read === truth;
  return h(
    "figure",
    { class: `digit-tile ${right ? "" : "wrong"}` },
    digitImage(n),
    h(
      "figcaption",
      {},
      h("span", { class: "muted", text: `Image ${n}` }),
      h("span", { class: "digit-read" }, "read as ", h("strong", { text: String(read) })),
      right ? null : h("span", { class: "digit-truth", text: `MNIST says ${truth}` }),
    ),
  );
}

export default {
  ImageOutput: ({ image, rows }) =>
    h(
      "div",
      { class: "digit-card" },
      h("div", { class: "digit-pair" }, h("figure", { class: "digit-tile" }, digitImage(image), h("figcaption", { class: "muted", text: `Image ${image}` }))),
      disclosure({ summary: "The text the agent reads", className: "digit-text" }, h("pre", { class: "digit-rows", text: rows.join("\n") })),
    ),
  MathOutput: ({ first, second, operator, first_digit, second_digit, result }, { verdict }) => {
    const details = verdict.details || {};
    const truth = details.expected || null;
    const symbol = SYMBOLS[operator] || operator;
    const right = truth && result === truth.result;
    return h(
      "div",
      { class: "digit-card" },
      h(
        "div",
        { class: "digit-pair" },
        tile(first, first_digit, truth && truth.first_digit),
        h("span", { class: "digit-op", text: symbol }),
        tile(second, second_digit, truth && truth.second_digit),
      ),
      h("p", { class: "digit-sum" }, h("strong", { text: `${first_digit} ${symbol} ${second_digit} = ${result}` })),
      truth && !right
        ? h("p", { class: "digit-answer muted", text: `Right answer: ${truth.first_digit} ${symbol} ${truth.second_digit} = ${truth.result}` })
        : null,
      details.constraints ? checks(details.constraints) : null,
    );
  },
};
