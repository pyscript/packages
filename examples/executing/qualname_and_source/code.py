# ---------------------------------------------------------------------
# Beyond the AST node: ask `executing` for the qualified name of the
# currently executing function, and for the line/column range of the
# specific node within the source.
# ---------------------------------------------------------------------

heading("Qualified names from any frame")
note(
    "<code>Source.for_frame(frame).code_qualname(frame.f_code)</code> "
    "returns the dotted <code>__qualname__</code> of the function "
    "currently running in that frame &mdash; including nested "
    "functions and methods."
)


class Telescope:
    def observe(self, target):
        return self._record(target)

    def _record(self, target):
        frame = inspect.currentframe()
        source = executing.Source.for_frame(frame)
        return source.code_qualname(frame.f_code)


def outer():
    def inner():
        frame = inspect.currentframe()
        source = executing.Source.for_frame(frame)
        return source.code_qualname(frame.f_code)
    return inner()


display(HTML(
    "<ul>"
    f"<li>Method qualname: <code>{Telescope().observe('Vega')}</code></li>"
    f"<li>Nested function qualname: <code>{outer()}</code></li>"
    "</ul>"
), append=True)


# ---------------------------------------------------------------------
# Locate the calling expression's exact position in the source.
# ---------------------------------------------------------------------

heading("Where in the source did this call happen?")
note(
    "AST nodes carry line and column information. We can combine "
    "<code>executing</code>'s node identification with those "
    "attributes to point at the precise span of code."
)


def locate():
    """Return a description of where the caller invoked us."""
    caller_frame = inspect.currentframe().f_back
    executing_info = executing.Source.executing(caller_frame)
    node = executing_info.node
    if node is None:
        return "unknown location"
    filename = caller_frame.f_code.co_filename
    return (
        f"{type(node).__name__} in {filename} "
        f"at line {node.lineno}, cols {node.col_offset}"
        f"&ndash;{node.end_col_offset}: <code>{ast.unparse(node)}</code>"
    )


# Two distinct call sites; each gets its own location report.
report_a = locate()
report_b = locate()

display(HTML(f"<p>First call: {report_a}</p>"), append=True)
display(HTML(f"<p>Second call: {report_b}</p>"), append=True)
