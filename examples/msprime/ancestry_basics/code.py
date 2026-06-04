"""
A first look at msprime: simulating the genealogy of a sample.

msprime simulates the ancestral history of a sample of chromosomes
drawn from a population. The result is a "tree sequence" -- a compact
representation of all the genealogical trees along a chromosome.

Docs: https://tskit.dev/msprime/docs/stable/
"""
from IPython.core.display import display, HTML

import numpy as np
import matplotlib.pyplot as plt
import msprime


heading("A small coalescent simulation")
note(
    "We sample 6 diploid individuals (so 12 chromosomes) from a "
    "population of effective size 10,000 and simulate their shared "
    "ancestry back to a common ancestor."
)

ancestry = msprime.sim_ancestry(
    samples=6,
    population_size=10_000,
    random_seed=42,
)

note(f"Tree sequence summary:")
display(HTML(f"<pre>{ancestry}</pre>"), append=True)

# With no recombination there is a single tree spanning the whole
# sequence. Pull it out and look at it.
tree = ancestry.first()
note(
    f"Number of trees: <strong>{ancestry.num_trees}</strong>. "
    f"Time to most recent common ancestor (TMRCA): "
    f"<strong>{tree.tmrca(0, 1):.0f}</strong> generations "
    f"(for samples 0 and 1)."
)

heading("The genealogy as text")
note(
    "Tskit can render trees as ASCII art. Leaves are present-day "
    "samples; internal nodes are inferred ancestors with their "
    "ages in generations."
)
display(HTML(f"<pre>{tree.draw_text()}</pre>"), append=True)
