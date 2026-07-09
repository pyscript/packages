# ---------------------------------------------------------------------
# Section 2: Build a stoichiometry matrix for a small reaction network.
# ---------------------------------------------------------------------
import pandas as pd
from pyreactlab_core.models.reaction import Reaction
from pyreactlab_core import rxn, rxns_stoichiometry


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

# Note: despite the "_dict" suffix, `stoichiometry_matrices_dict` is a
# list of per-reaction dicts (one {species: coefficient} mapping per
# reaction), aligned with the input `reactions` order. Pandas handles
# this shape natively when given a list of records, inferring columns
# from the union of keys.
rows = matrix_info["stoichiometry_matrices_dict"]

stoich_df = pd.DataFrame(
    rows,
    index=[r.name for r in reactions],
)

# Reindex to the canonical species ordering from `component_list`, so
# the column order is stable rather than dict-iteration-dependent.
stoich_df = stoich_df.reindex(columns=matrix_info["component_list"])

note("Rows are reactions, columns are species (with phase suffixes):")
display(stoich_df, append=True)

heading("Quick sanity checks", level=3)

# Net mole change per reaction: sum of stoichiometric coefficients across
# all species. A negative value means the reaction consumes more moles of
# gas than it produces, which matters for reactor pressure and volume
# calculations. (This is not a mass balance — that would require weighting
# each coefficient by the species' molecular weight.)
net_change = stoich_df.sum(axis=1).rename("net mole change")
display(net_change.to_frame(), append=True)

note(
    "Methanol synthesis shows a net change of -2 moles: four moles of "
    "gas in (1 CO<sub>2</sub> + 3 H<sub>2</sub>) become two moles out "
    "(1 CH<sub>3</sub>OH + 1 H<sub>2</sub>O). Ethylene hydrogenation "
    "loses one mole (2 in, 1 out). Both reactions favour higher "
    "pressure by Le Chatelier's principle."
)

# Which reactions consume H2?
h2_consumers = stoich_df.index[stoich_df["H2-g"] < 0].tolist()
note(f"Reactions that consume H<sub>2</sub>(g): <strong>{h2_consumers}</strong>")