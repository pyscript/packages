# ---------------------------------------------------------------------
# Building a demographic model: two populations that split in the past.
# ---------------------------------------------------------------------

heading("Two populations diverging from a common ancestor")
note(
    "We define a Demography with two present-day populations, A and B, "
    "that split from an ancestral population ANC 2,000 generations ago. "
    "Then we sample 20 diploids from each and compare their genetic "
    "diversity (pi) and divergence (Fst)."
)

demography = msprime.Demography()
demography.add_population(name="A", initial_size=10_000)
demography.add_population(name="B", initial_size=5_000)
demography.add_population(name="ANC", initial_size=10_000)
demography.add_population_split(
    time=2_000, derived=["A", "B"], ancestral="ANC",
)

note("Population table from the demography:")
display(HTML(f"<pre>{demography.debug()}</pre>"), append=True)

ancestry = msprime.sim_ancestry(
    samples={"A": 20, "B": 20},
    demography=demography,
    sequence_length=2_000_000,
    recombination_rate=1e-8,
    random_seed=99,
)
mutated = msprime.sim_mutations(ancestry, rate=1e-8, random_seed=99)

# Sample sets, expressed as lists of sample node IDs per population.
samples_A = mutated.samples(population=0)
samples_B = mutated.samples(population=1)

# Diversity within each population, and Fst between them.
pi_A = mutated.diversity(sample_sets=samples_A)
pi_B = mutated.diversity(sample_sets=samples_B)
fst = mutated.Fst(sample_sets=[samples_A, samples_B])

note(
    f"Variant sites: <strong>{mutated.num_sites:,}</strong>. "
    f"Population A pi = <strong>{pi_A:.5f}</strong>, "
    f"Population B pi = <strong>{pi_B:.5f}</strong>, "
    f"Fst(A, B) = <strong>{fst:.4f}</strong>."
)

heading("Allele frequency spectrum, per population")
note(
    "The site frequency spectrum (SFS) counts variants by how many "
    "samples carry the derived allele. Population A has more "
    "diversity, so its spectrum extends further to the right."
)

afs_A = mutated.allele_frequency_spectrum(
    sample_sets=[samples_A], polarised=True, span_normalise=False,
)
afs_B = mutated.allele_frequency_spectrum(
    sample_sets=[samples_B], polarised=True, span_normalise=False,
)

# Drop the monomorphic (0 and n) bins for plotting.
freqs_A = afs_A[1:-1]
freqs_B = afs_B[1:-1]
x = np.arange(1, len(freqs_A) + 1)

fig, ax = plt.subplots(figsize=(9, 4))
width = 0.4
ax.bar(x - width / 2, freqs_A, width, color="steelblue", label="A")
ax.bar(x + width / 2, freqs_B, width, color="indianred", label="B")
ax.set_title("Site frequency spectrum")
ax.set_xlabel("Derived allele count in sample")
ax.set_ylabel("Number of variant sites")
ax.legend()
fig.tight_layout()
display(fig, append=True)
