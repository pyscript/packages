# ---------------------------------------------------------------------
# Building an arithmetic expression parser with infix_notation.
# ---------------------------------------------------------------------
#
# infix_notation is the high-level helper for expressions with operator
# precedence. You give it an operand and a list of (operator, arity,
# associativity, action) tuples, ordered from highest to lowest precedence.

import pyparsing as pp
from pyparsing import (
    one_of, infix_notation, OpAssoc, pyparsing_common,
)


heading("Arithmetic with operator precedence")
note(
    "We'll parse expressions like <code>2 + 3 * (4 - 1)</code> and "
    "evaluate them on the fly using parse actions."
)

# Each parse action receives the matched tokens and returns the computed
# value. By returning a number, we replace the matched tokens in-place so
# higher-precedence rules see already-evaluated sub-expressions.

def eval_signed(tokens):
    sign, value = tokens[0]
    return -value if sign == "-" else value


def eval_binop(tokens):
    # Tokens are flat: [a, op, b, op, c, ...] for left-associative chains.
    flat = tokens[0]
    result = flat[0]
    for op, rhs in zip(flat[1::2], flat[2::2]):
        if op == "+": result += rhs
        elif op == "-": result -= rhs
        elif op == "*": result *= rhs
        elif op == "/": result /= rhs
    return result


number = pyparsing_common.number  # parses ints and floats, returns numerics

expression = pp.Forward()
expression <<= infix_notation(
    number,
    [
        (one_of("+ -"), 1, OpAssoc.RIGHT, eval_signed),
        (one_of("* /"), 2, OpAssoc.LEFT, eval_binop),
        (one_of("+ -"), 2, OpAssoc.LEFT, eval_binop),
    ],
)

cases = [
    "2 + 3",
    "2 + 3 * 4",
    "(2 + 3) * 4",
    "10 - 2 - 3",            # left-associative subtraction
    "-5 + 2 * -3",           # unary minus
    "1 + 2 * 3 - 4 / 2",
]

rows = ["<table><tr><th>Expression</th><th>Result</th></tr>"]
for text in cases:
    value = expression.parse_string(text, parse_all=True)[0]
    rows.append(f"<tr><td><code>{text}</code></td><td>{value}</td></tr>")
rows.append("</table>")
display(HTML("".join(rows)), append=True)

note(
    "Note how parse actions turn the parser into an evaluator: "
    "each layer reduces matched tokens to a Python number, so by the "
    "time we reach the top of the stack, parsing and evaluation are done."
)
