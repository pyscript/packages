"""
A first look at the `newick` package.

The Newick format is a compact, parenthesis-based notation for trees,
widely used in bioinformatics to describe phylogenies. The `newick`
package parses Newick strings into a tree of `Node` objects you can
inspect and walk.

See https://en.wikipedia.org/wiki/Newick_format for a primer.
"""
from IPython.core.display import display, HTML

import newick


# A tiny phylogeny relating four primates. The numbers after the colons
# are branch lengths (e.g. millions of years of divergence).
primates = "((Human:6.0,Chimp:6.0)HomoPan:2.0,(Gorilla:8.0,Orangutan:14.0)Great:1.0)Primates;"

# `loads` parses a Newick string and returns a list of trees (Newick
# files can hold more than one), so we take the first.
tree = newick.loads(primates)[0]

heading("A primate phylogeny")
note(f"Root node name: <code>{tree.name}</code>")
note("Direct descendants of the root, with their branch lengths:")
for child in tree.descendants:
    display(HTML(f"<li><code>{child.name}</code>: {child.length}</li>"), append=True)

# `ascii_art` draws the topology as text, which is great for a quick
# sanity check.
heading("Topology")
display(HTML(f"<pre>{tree.ascii_art()}</pre>"), append=True)

# `get_leaves` returns just the tip nodes (the species, in our case).
heading("Leaves")
note("The tip nodes correspond to the species at the leaves of the tree:")
leaf_names = [leaf.name for leaf in tree.get_leaves()]
display(HTML(f"<p><code>{leaf_names}</code></p>"), append=True)
