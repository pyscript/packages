# ---------------------------------------------------------------------
# Many phylogenetics tools (BEAST, MrBayes, TreeAnnotator, ...) embed
# extra per-node data in Newick comments enclosed in square brackets.
# The `newick` package can parse these as structured properties when
# they follow the NHX or `&key=value,...` conventions.
# ---------------------------------------------------------------------

heading("Reading NHX-style annotations")
note(
    "Here each tip carries a species code and a support value, "
    "stored in the <code>[&&NHX:...]</code> comment after the node name."
)

annotated = (
    "((mouse[&&NHX:species=Mus_musculus:support=98],"
    "rat[&&NHX:species=Rattus_norvegicus:support=95])Rodentia"
    "[&&NHX:support=99],"
    "human[&&NHX:species=Homo_sapiens:support=100])Mammalia;"
)

tree = newick.loads(annotated)[0]

# `walk` yields every node in the tree. `Node.properties` is a dict
# parsed from the NHX-style comment; `Node.comment` is the raw text.
heading("Per-node properties")
for node in tree.walk():
    if node.properties:
        props = ", ".join(f"{k}={v}" for k, v in node.properties.items())
        display(HTML(f"<li><code>{node.name}</code> &rarr; {props}</li>"), append=True)

# Comments can also be ignored entirely at parse time, which is handy
# when you just want the bare topology.
heading("Stripping comments")
bare = newick.loads(annotated, strip_comments=True)[0]
note("The same tree, parsed with <code>strip_comments=True</code>:")
display(HTML(f"<pre>{bare.newick}</pre>"), append=True)

# Quoted labels let you put otherwise-reserved characters in node names.
heading("Quoted labels")
note(
    "Single-quoted labels can contain commas, parentheses, and colons. "
    "Doubled single quotes <code>''</code> represent a literal apostrophe."
)
quoted = newick.loads("('Genus species (strain 1)','O''Brien lab isolate')Sample;")[0]
display(HTML(f"<pre>{quoted.ascii_art()}</pre>"), append=True)
for leaf in quoted.get_leaves():
    display(HTML(
        f"<li>name=<code>{leaf.name}</code>, "
        f"unquoted=<code>{leaf.unquoted_name}</code></li>"
    ), append=True)
