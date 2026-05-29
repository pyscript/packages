# ---------------------------------------------------------------------
# Section 3: Streaming with CloudPickler, and composing pickled callables.
# ---------------------------------------------------------------------

heading("Using CloudPickler with a stream")
note(
    "<code>cloudpickle.dumps</code> is a convenience wrapper around "
    "<code>CloudPickler</code>. When you want to write several objects "
    "into a single stream (a file, a socket, a BytesIO buffer), you "
    "use the pickler directly."
)

# Build a small pipeline of transformations as plain Python callables.
def normalize(text):
    """Strip whitespace and lowercase."""
    return text.strip().lower()

def tokenize(text):
    """Split on whitespace."""
    return text.split()

def word_count(tokens):
    """Count tokens, returning a dict."""
    counts = {}
    for token in tokens:
        counts[token] = counts.get(token, 0) + 1
    return counts


buffer = io.BytesIO()
pickler = cloudpickle.CloudPickler(buffer)
for stage in (normalize, tokenize, word_count):
    pickler.dump(stage)

note(
    f"Wrote 3 callables into a single buffer "
    f"(<strong>{buffer.tell()}</strong> bytes total)."
)

# Read them back one at a time with the standard pickle.Unpickler.
buffer.seek(0)
unpickler = pickle.Unpickler(buffer)
stages = [unpickler.load() for _ in range(3)]

# Now compose the restored stages into a tiny pipeline.
sample = "  The quick brown fox jumps over the lazy dog. The dog sleeps.  "

current = sample
for stage in stages:
    current = stage(current)

note(f"Input: <code>{sample!r}</code>")
display(HTML(
    "<p>Result after running the unpickled pipeline:</p>"
    f"<pre>{current}</pre>"
), append=True)

heading("Recursive and self-referential structures")
note(
    "cloudpickle handles cyclic references the same way pickle does, "
    "which matters when serializing graphs, ASTs, or any structure "
    "that points back at itself."
)

graph = {"name": "root", "children": []}
child = {"name": "child", "parent": graph}
graph["children"].append(child)

restored_graph = pickle.loads(cloudpickle.dumps(graph))

note(
    f"Round-tripped a self-referential dict. "
    f"<code>restored['children'][0]['parent'] is restored</code> &rarr; "
    f"<strong>{restored_graph['children'][0]['parent'] is restored_graph}</strong>."
)
