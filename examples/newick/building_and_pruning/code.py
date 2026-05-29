# ---------------------------------------------------------------------
# Build a tree node-by-node, then trim it down to a subset of leaves.
# ---------------------------------------------------------------------

heading("Building a tree from scratch")
note(
    "We'll model a small file-system-like hierarchy using "
    "<code>Node.create</code> and <code>add_descendant</code>."
)

# Build the root and its immediate children.
root = newick.Node.create(name="root")
docs = newick.Node.create(name="docs")
src = newick.Node.create(name="src")
tests = newick.Node.create(name="tests")
root.add_descendant(docs)
root.add_descendant(src)
root.add_descendant(tests)

# Add some leaves under each branch.
for leaf in ("intro.md", "guide.md"):
    docs.add_descendant(newick.Node.create(name=leaf))
for leaf in ("main.py", "utils.py", "io.py"):
    src.add_descendant(newick.Node.create(name=leaf))
for leaf in ("test_main.py", "test_io.py"):
    tests.add_descendant(newick.Node.create(name=leaf))

display(HTML(f"<pre>{root.ascii_art()}</pre>"), append=True)

# Serialize to Newick text with `dumps`. Round-tripping with `loads`
# gives back an equivalent tree.
heading("Serializing to Newick")
serialized = newick.dumps(root)
note("The same tree as a Newick string:")
display(HTML(f"<pre>{serialized}</pre>"), append=True)

# Pruning: keep only the Python files. With `inverse=True`, the named
# nodes are the ones we *keep*; everything else gets pruned.
heading("Pruning to a subset of leaves")
note(
    "We prune to keep only the <code>.py</code> files, then collapse "
    "internal nodes that no longer branch."
)

python_files = [n.name for n in root.get_leaves() if n.name.endswith(".py")]
root.prune_by_names(python_files, inverse=True)
root.remove_redundant_nodes(keep_leaf_name=True)

display(HTML(f"<pre>{root.ascii_art()}</pre>"), append=True)
note(f"Remaining leaves: <code>{[n.name for n in root.get_leaves()]}</code>")
