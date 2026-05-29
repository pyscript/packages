# ---------------------------------------------------------------------
# The water-gas shift reaction:  CO(g) + H2O(g) -> CO2(g) + H2(g)
# ---------------------------------------------------------------------

heading("Water-gas shift: building the reaction")
note(
    "The water-gas shift is a workhorse of industrial hydrogen "
    "production. We declare each species as a Component, then bundle "
    "them into a Reaction object that pythermocalcdb_nasa can read."
)

CO  = Component(name="carbon monoxide", formula="CO",  state="g")
H2O = Component(name="dihydrogen monoxide", formula="H2O", state="g")
CO2 = Component(name="carbon dioxide", formula="CO2", state="g")
H2  = Component(name="dihydrogen", formula="H2",  state="g")

wgs = Reaction(
    name="Water-Gas Shift",
    reaction="CO(g) + H2O(g) => CO2(g) + H2(g)",
    components=[CO, H2O, CO2, H2],
)

note(f"Reaction: <code>{wgs.reaction}</code>")

heading("The equilibrium-constant API", level=3)
note(
    "Once you have a <code>model_source</code> built from NASA pickles "
    "via <code>pyThermoLinkDB</code>, the calls below give you reaction "
    "thermochemistry and K(T). The full version of <code>Keq</code> "
    "uses Delta G^0(T) directly; <code>Keq_vh_shortcut</code> applies "
    "the Van't Hoff approximation anchored at Delta H^0(298 K)."
)

api_summary = pd.DataFrame({
    "call": [
        "dH_rxn_STD(reaction, temperature, model_source)",
        "dS_rxn_STD(reaction, temperature, model_source)",
        "dG_rxn_STD(reaction, temperature, model_source)",
        "Keq(reaction, temperature, model_source)",
        "Keq_vh_shortcut(reaction, temperature, model_source)",
    ],
    "yields": [
        "Delta H^0(T)  [J/mol]",
        "Delta S^0(T)  [J/(mol K)]",
        "Delta G^0(T)  [J/mol]",
        "K(T) from Delta G^0(T)",
        "K(T) via Van't Hoff from Delta H^0(298 K)",
    ],
})
display(api_summary, append=True)

heading("What K(T) looks like for an exothermic reaction", level=3)
note(
    "WGS is mildly exothermic (Delta H^0_298 ~ -41 kJ/mol), so K "
    "decreases with temperature. Using textbook values for Delta H^0 "
    "and Delta S^0 at 298 K, we sketch the Van't Hoff curve that "
    "<code>Keq_vh_shortcut</code> would return:"
    " <code>ln K(T) = -Delta H^0/(R T) + Delta S^0/R</code>."
)

R = 8.314462618  # J/(mol K)
dH_298 = -41.16e3  # J/mol
dS_298 = -42.08    # J/(mol K)

T_grid = np.linspace(400.0, 1200.0, 81)
ln_K = -dH_298 / (R * T_grid) + dS_298 / R
K = np.exp(ln_K)

fig, ax = plt.subplots(figsize=(8, 4))
ax.semilogy(T_grid, K, color="darkgreen", linewidth=2)
ax.axhline(1.0, color="gray", linestyle="--", linewidth=1)
ax.set_xlabel("Temperature (K)")
ax.set_ylabel("K(T)  (log scale)")
ax.set_title("Van't Hoff sketch: water-gas shift K vs T")
ax.grid(True, which="both", alpha=0.3)
fig.tight_layout()
display(fig, append=True)

note(
    "Swap in real NASA polynomials via <code>model_source</code> and "
    "call <code>Keq(reaction=wgs, temperature=Temperature(value=T, "
    "unit='K'), model_source=model_source)</code> in a loop to get "
    "the exact curve, including the temperature dependence of "
    "Delta H^0 and Delta S^0 that the Van't Hoff shortcut ignores."
)
