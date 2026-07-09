# ---------------------------------------------------------------------
# Build a tiny `icecream`-style debug helper.
#
# When you call `show(some_expr, other_expr)`, it prints both the
# *source text* of each argument and its runtime value. This is the
# core trick behind libraries like `icecream` and `snoop`.
# ---------------------------------------------------------------------

heading("A mini print-debugger powered by executing")
note(
    "<code>show(...)</code> identifies its own <code>Call</code> "
    "node in the caller's source, then walks the argument AST nodes "
    "to recover the original text of each expression."
)


def show(*values):
    """Display each argument as `source = value`."""
    caller_frame = inspect.currentframe().f_back
    call_node = executing.Source.executing(caller_frame).node

    rows = []
    if isinstance(call_node, ast.Call):
        # Pair each AST argument node with its evaluated value.
        for arg_node, value in zip(call_node.args, values):
            source_text = ast.unparse(arg_node)
            rows.append((source_text, repr(value)))
    else:
        # Fallback if we couldn't identify the call (e.g. inside an
        # expression the parser handles unusually).
        for value in values:
            rows.append(("?", repr(value)))

    body = "".join(
        f"<tr><td><code>{src}</code></td>"
        f"<td><code>{val}</code></td></tr>"
        for src, val in rows
    )
    display(HTML(
        "<table><thead><tr><th>expression</th><th>value</th>"
        f"</tr></thead><tbody>{body}</tbody></table>"
    ), append=True)


# A small story: a basket of fruit and a few derived quantities.
basket = {"apples": 4, "pears": 2, "plums": 7}
total = sum(basket.values())
heaviest = max(basket, key=basket.get)

show(basket, total, heaviest, total * 1.5, basket["apples"] + basket["pears"])
