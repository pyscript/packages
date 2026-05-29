# ---------------------------------------------------------------------
# Adding recombination and layering mutations onto the genealogy.
# ---------------------------------------------------------------------

heading("Recombination breaks the chromosome into pieces")
note(
    "With recombination, different segments of the chromosome have "
    "different genealogical trees. We simulate a 1 Mb chromosome "
    "for 10 diploid samples."
)

ancestry = msprime.sim_ancestry(
    samples=10,
    population_size=10_000,
    sequence_length=1_000_000,
    recombination_rate=1e-8,
    random_seed=7,
)

note(
    f"Trees along the 1 Mb chromosome: "
    f"<strong>{ancestry.num_trees}</strong>."
)

# Each tree spans an interval. Show the first few.
spans = []
for tree in ancestry.trees():
    spans.append((tree.interval.left, tree.interval.right, tree.num_edges))
    if len(spans) >= 5:
        break

note("First five trees (interval and edge count):")
rows = "".join(
    f"<tr><td>{l:,.0f}</td><td>{r:,.0f}</td><td>{e}</td></tr>"
    for l, r, e in spans
)
display(HTML(
    "<table border='1' cellpadding='4'>"
    "<tr><th>left</th><th>right</th><th>edges</th></tr>"
    f"{rows}</table>"
), append=True)

heading("Sprinkle mutations onto the genealogy")
note(
    "sim_mutations adds neutral mutations along the branches at a "
    "given per-site, per-generation rate. The result is genetic "
    "variation we can analyze."
)

mutated = msprime.sim_mutations(
    ancestry,
    rate=1e-8,
    random_seed=7,
)

note(
    f"Variant sites generated: "
    f"<strong>{mutated.num_sites}</strong>."
)

# Plot the distribution of variant positions along the chromosome.
positions = np.array([site.position for site in mutated.sites()])

fig, ax = plt.subplots(figsize=(9, 3))
ax.hist(positions, bins=40, color="seagreen", edgecolor="white")
ax.set_title("Distribution of mutations along the 1 Mb chromosome")
ax.set_xlabel("Position (bp)")
ax.set_ylabel("Number of variant sites")
fig.tight_layout()
display(fig, append=True)
