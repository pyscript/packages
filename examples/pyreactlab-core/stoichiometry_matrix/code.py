# ---------------------------------------------------------------------
# Section 2: Build a stoichiometry matrix for a small reaction network.
# ---------------------------------------------------------------------

heading("A two-reaction hydrogenation network")
note(
    "PyReactLab can take a list of reactions and assemble the "
    "stoichiometry matrix you'd use in reactor design or "
    "reaction-engineering math. Negative entries mean a species is "
    "consumed; positive entries mean it's produced."
)

# Use the convenience constructor `rxn` to build Reaction instances.
methanol_synthesis = rxn(
    reaction_str="CO2(g) + 3H2(g) => CH3OH(g) + H2O(g)",
    name="CO2 Hydrogenation to Methanol",
)

ethylene_hydrogenation = rxn(
    reaction_str="C2H4(g) + H2(g) => C2H6(g)",
    name="Ethylene Hydrogenation to Ethane",
)

reactions = [methanol_synthesis, ethylene_hydrogenation]

# Assemble the stoichiometry matrix across the union of all species.
matrix_info = rxns_stoichiometry(reactions=reactions)

components = matrix_info["components"]
rows_dict = matrix_info["stoichiometry_matrices_dict"]

# Wrap the result in a pandas DataFrame for a readable display.
stoich_df = pd.DataFrame(
    rows_dict,
    index=[r.name for r in reactions],
    columns=components,
)

note("Rows are reactions, columns are species (with phase suffixes):")
display(stoich_df, append=True)

heading("Quick sanity checks", level=3)

# Net change per reaction: should be zero only if mass-and-mole balanced
# across this column set; for these reactions, methanol synthesis has a
# net change in moles of gas, which is reaction-engineering reality.
net_change = stoich_df.sum(axis=1).rename("net mole change")
display(net_change.to_frame(), append=True)

# Which reactions consume H2?
h2_consumers = stoich_df.index[stoich_df["H2-g"] < 0].tolist()
note(f"Reactions that consume H2(g): <strong>{h2_consumers}</strong>")
