# ---------------------------------------------------------------------
# Community detection on a planted-clusters graph.
# ---------------------------------------------------------------------

heading("Finding communities in a generated graph")
note(
    "igraph ships with many graph generators. "
    "<code>SBM</code> creates a stochastic block model: "
    "groups of vertices that connect densely within and sparsely "
    "between. We then ask igraph to recover those groups."
)

# Three blocks of 12, 10, and 8 vertices. The block matrix gives the
# probability of an edge between (and within) blocks.
block_sizes = [12, 10, 8]
edge_probabilities = [
    [0.45, 0.04, 0.02],
    [0.04, 0.50, 0.05],
    [0.02, 0.05, 0.55],
]
ig.set_random_number_generator(__import__("random").Random(7))
graph = ig.Graph.SBM(
    n=sum(block_sizes),
    pref_matrix=edge_probabilities,
    block_sizes=block_sizes,
    directed=False,
)

note(f"Generated graph: {graph.vcount()} vertices, "
     f"{graph.ecount()} edges.")

# Run a fast modularity-based community detection algorithm.
communities = graph.community_multilevel()
note(
    f"Detected <strong>{len(communities)}</strong> communities. "
    f"Modularity score: <strong>{communities.modularity:.3f}</strong> "
    "(higher is better; > 0.3 suggests meaningful structure)."
)

# Show the size of each detected community.
sizes = sorted((len(c) for c in communities), reverse=True)
note("Community sizes (largest first): " +
     ", ".join(str(s) for s in sizes))

# Colour the vertices by community membership and plot.
palette = ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00"]
membership = communities.membership
vertex_colors = [palette[m % len(palette)] for m in membership]

fig, ax = plt.subplots(figsize=(7, 6))
ig.plot(
    graph,
    target=ax,
    layout=graph.layout("fr"),  # Fruchterman-Reingold
    vertex_color=vertex_colors,
    vertex_size=18,
    edge_color="lightgray",
    edge_width=0.6,
)
ax.set_axis_off()
ax.set_title("Communities recovered by multilevel modularity")
fig.tight_layout()
display(fig, append=True)
