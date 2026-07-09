"""
A first look at python-igraph.

We model a small social network of office colleagues, then ask
igraph a few classic questions: who knows whom, who is most
connected, and how short are the chains of acquaintance?

Docs: https://python.igraph.org
"""
from IPython.core.display import display, HTML
import igraph as ig
import matplotlib.pyplot as plt


heading("A small office social network")
note(
    "Eight colleagues; an edge means 'these two regularly chat'. "
    "We build the graph from a list of name pairs."
)

people = ["Ava", "Ben", "Cleo", "Dan", "Eli", "Fay", "Gus", "Hana"]
chats = [
    ("Ava", "Ben"), ("Ava", "Cleo"), ("Ben", "Cleo"),
    ("Cleo", "Dan"), ("Dan", "Eli"), ("Eli", "Fay"),
    ("Fay", "Gus"), ("Gus", "Hana"), ("Hana", "Eli"),
    ("Ava", "Dan"), ("Ben", "Fay"),
]

# Build an undirected graph by passing the named edge list directly.
office = ig.Graph.TupleList(chats, directed=False)

note(
    f"Vertices: <strong>{office.vcount()}</strong>, "
    f"edges: <strong>{office.ecount()}</strong>, "
    f"connected: <strong>{office.is_connected()}</strong>."
)

# Centrality: degree (raw count) and betweenness (bridge-like role).
degree = office.degree()
betweenness = office.betweenness()
names = office.vs["name"]

summary_rows = "".join(
    f"<tr><td>{n}</td><td>{d}</td><td>{b:.1f}</td></tr>"
    for n, d, b in sorted(
        zip(names, degree, betweenness),
        key=lambda row: row[1],
        reverse=True,
    )
)
display(HTML(
    "<table border='1' cellpadding='4'>"
    "<tr><th>Person</th><th>Degree</th><th>Betweenness</th></tr>"
    f"{summary_rows}</table>"
), append=True)

# Shortest path between two people on opposite ends of the network.
path_ids = office.get_shortest_paths("Ava", to="Hana")[0]
path_names = [office.vs[i]["name"] for i in path_ids]
note("Shortest acquaintance chain from Ava to Hana: "
     f"<strong>{' &rarr; '.join(path_names)}</strong>")

# A simple matplotlib visualisation. igraph integrates with matplotlib
# via ig.plot(graph, target=ax, ...).
heading("Visualising the network")
fig, ax = plt.subplots(figsize=(6, 5))
layout = office.layout("kk")  # Kamada-Kawai force-directed layout
ig.plot(
    office,
    target=ax,
    layout=layout,
    vertex_label=office.vs["name"],
    vertex_size=30,
    vertex_color="lightyellow",
    edge_color="gray",
)
ax.set_axis_off()
fig.tight_layout()
display(fig, append=True)
