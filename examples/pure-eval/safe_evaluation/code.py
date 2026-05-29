"""
A first look at pure_eval: evaluating AST nodes without side effects.

Imagine you're writing a debugger or REPL helper that wants to peek
at the values of expressions on a line of source code. Calling eval()
is dangerous because it can run arbitrary code (network calls,
property side effects, mutations). pure_eval refuses to do anything
that might have a side effect.

See: https://github.com/alexmojaki/pure_eval
"""
from IPython.core.display import display, HTML


# A class with a property that has an observable side effect: it
# prints whenever it's accessed. A naive eval() would trigger this.
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    @property
    def area(self):
        # Pretend this is an expensive database call or HTTP request.
        print("Calculating area... (side effect!)")
        return self.width * self.height


rect = Rectangle(3, 5)

heading("1. Parsing source into an AST")
note(
    "We have a tuple expression referencing three attributes of "
    "<code>rect</code>. Two are plain data; one is a property that "
    "runs code when accessed."
)

source = "(rect.width, rect.height, rect.area)"
tree = ast.parse(source, mode="eval")
the_tuple = tree.body

display(HTML(f"<pre>source = {source}</pre>"), append=True)

heading("2. Evaluating safe nodes")
note(
    "We build an <code>Evaluator</code> from a dict of known names "
    "and ask it for the value of each AST node. Plain attribute "
    "lookups on the data succeed."
)

evaluator = Evaluator({"rect": rect})

for node in the_tuple.elts[:2]:
    label = ast.unparse(node)
    value = evaluator[node]
    note(f"<code>{label}</code> &rarr; <strong>{value}</strong>")

heading("3. Refusing to trigger side effects")
note(
    "Asking for <code>rect.area</code> would invoke the property "
    "and print a message. <code>pure_eval</code> raises "
    "<code>CannotEval</code> instead."
)

area_node = the_tuple.elts[2]
try:
    evaluator[area_node]
except CannotEval:
    note(
        "Caught <code>CannotEval</code> for "
        f"<code>{ast.unparse(area_node)}</code>. No side effect was "
        "triggered."
    )
