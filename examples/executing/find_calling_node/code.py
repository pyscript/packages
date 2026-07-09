"""
A first taste of `executing`: discover, at runtime, exactly which
piece of source code triggered the current function call.

`executing` looks at the calling frame's bytecode and matches it back
to a node in the parsed AST of the source file. This is the magic
behind libraries like `icecream`, `snoop`, and `stack_data`.

See: https://github.com/alexmojaki/executing
"""
from IPython.core.display import display, HTML
import ast
import inspect
import executing



def whoami():
    """Report the AST node and source text of our caller."""
    # The caller's frame is one level up the stack.
    caller_frame = inspect.currentframe().f_back
    node = executing.Source.executing(caller_frame).node
    if node is None:
        return "(could not identify the calling node)"
    # ast.dump shows the structural shape; ast.unparse recovers source.
    return f"{type(node).__name__}: {ast.unparse(node)!r}"


heading("What called me?")
note(
    "Each line below calls <code>whoami()</code> in a different "
    "syntactic context. <code>executing</code> tells us which AST "
    "node corresponds to each call."
)

# A bare call expression.
result_simple = whoami()

# A call inside a binary operation.
result_in_binop = "prefix: " + whoami()

# A call used as a subscript index.
labels = {"a": "alpha", "b": "beta"}
result_as_key = labels["a"], whoami()

display(HTML(
    "<ul>"
    f"<li>Bare call &rarr; {result_simple}</li>"
    f"<li>Inside concatenation &rarr; {result_in_binop}</li>"
    f"<li>Inside a tuple &rarr; {result_as_key[1]}</li>"
    "</ul>"
), append=True)
