"""
A first look at PyReactLab-Core.

We'll define a chemical reaction as a string and let the package parse
it into structured information: reactants, products, stoichiometric
coefficients, phases, and more.

Docs: https://pyreactlab-core.readthedocs.io/
"""
from IPython.core.display import display, HTML
# Package imports for the first example.
from pyreactlab_core.models.reaction import Reaction


heading("Methanol synthesis from CO2 and hydrogen")
note(
    "We describe the reaction with a compact string. The "
    "<code>(g)</code> markers tell PyReactLab the phase of each "
    "species, and <code>=&gt;</code> separates reactants from products."
)

methanol_synthesis = Reaction(
    name="CO2 Hydrogenation to Methanol",
    reaction="CO2(g) + 3H2(g) => CH3OH(g) + H2O(g)",
)

note(f"Parsed reaction string: <code>{methanol_synthesis.reaction}</code>")

# A small HTML table summarising the parsed properties.
properties = {
    "Reactants": methanol_synthesis.reactants_names,
    "Products": methanol_synthesis.products_names,
    "Reaction phase": methanol_synthesis.reaction_phase,
    "State counts": methanol_synthesis.state_count,
    "Stoichiometry": methanol_synthesis.reaction_stoichiometry,
    "Carbon count per species": methanol_synthesis.carbon_count,
}

rows = "".join(
    f"<tr><th style='text-align:left;padding-right:1em'>{k}</th>"
    f"<td><code>{v}</code></td></tr>"
    for k, v in properties.items()
)
display(HTML(f"<table>{rows}</table>"), append=True)

heading("Reactants and products in detail", level=3)
note("Each reactant/product carries its coefficient, molecule, and state:")
display(methanol_synthesis.reactants, append=True)
display(methanol_synthesis.products, append=True)
