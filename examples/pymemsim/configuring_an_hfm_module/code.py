# ---------------------------------------------------------------------
# Configuring an HFM module: options, inputs, and the factory.
# ---------------------------------------------------------------------
#
# A PyMemSim simulation has three ingredients:
#   1. Options - what kind of module and how to solve it.
#   2. Inputs  - the feed/permeate streams and operating conditions.
#   3. The module itself, built by create_hfm_module(...).
#
# This example introspects what each of those pieces looks like for
# a gas-phase, co-current hollow-fiber membrane separating a CO2/N2
# mixture. The point is to make the configuration vocabulary feel
# concrete before running a solver.

heading("Inspecting PyMemSim's configuration classes")

# Find the configuration-style classes the package exposes. We look
# for things whose names hint at "options" or "module" so the reader
# can map names they'll see in the docs to real attributes.
candidates = [
    name for name in dir(pms)
    if not name.startswith("_")
    and any(key in name.lower() for key in ("option", "module", "hfm", "input"))
]
note("Configuration-related names exported by <code>pymemsim</code>:")
display(HTML("<pre>" + "\n".join(candidates) + "</pre>"), append=True)

# A realistic configuration sketch. We describe the module the way a
# PyMemSim user would: a gas-phase HFM running co-currently, isothermal
# and isobaric on both sides, with two components (CO2 and N2).
heading("A gas-phase CO2/N2 separation, sketched as a config")

config_sketch = {
    "phase": "gas",
    "modeling_mode": "physical",      # alternative: "scale"
    "thermal_mode": "isothermal",     # alternative: "non-isothermal"
    "flow_pattern": "co-current",     # alternative: "counter-current"
    "components": ["CO2", "N2"],
    "feed": {
        "flow_mol_per_s": 1.0e-3,
        "composition": {"CO2": 0.15, "N2": 0.85},
        "temperature_K": 308.15,
        "pressure_bar": 6.0,
    },
    "permeate": {
        "flow_mol_per_s": 1.0e-5,
        "composition": {"CO2": 0.0, "N2": 1.0},
        "temperature_K": 308.15,
        "pressure_bar": 1.0,
    },
    "transport": {
        # Component permeance, mol / (m^2 s Pa). CO2 permeates ~25x faster.
        "permeance": {"CO2": 2.5e-7, "N2": 1.0e-8},
    },
    "solver": {
        # Co-current => IVP via scipy.integrate.solve_ivp.
        "method": "Radau",
        "rtol": 1.0e-6,
        "atol": 1.0e-9,
    },
}

# Render the config as a small two-column table so it reads at a glance.
rows = []
for section, value in config_sketch.items():
    if isinstance(value, dict):
        for k, v in value.items():
            rows.append((f"{section}.{k}", repr(v)))
    else:
        rows.append((section, repr(value)))

table_html = ["<table border='1' cellpadding='4' style='border-collapse: collapse;'>"]
table_html.append("<tr><th align='left'>Setting</th><th align='left'>Value</th></tr>")
for key, val in rows:
    table_html.append(f"<tr><td><code>{key}</code></td><td><code>{val}</code></td></tr>")
table_html.append("</table>")
display(HTML("".join(table_html)), append=True)

note(
    "In a full script you'd pass these into "
    "<code>HollowFiberMembraneOptions(...)</code> and a model-input "
    "object, then call <code>pms.create_hfm_module(options=..., "
    "inputs=...)</code> and run the resulting module's simulate "
    "method. The example files <code>gas-hfm-exp-1.py</code> "
    "(co-current, IVP) and <code>gas-hfm-exp-2.py</code> "
    "(counter-current, BVP via <code>solver_bvp</code>) in the "
    "PyMemSim repository show the full call sequence."
)

# A predictive sketch of what the resulting profile would look like
# given the permeance ratio above. This isn't a solved simulation; it's
# the analytic shape you'd expect from a fast/slow component pair in a
# co-current arrangement, useful for sanity-checking real results.
heading("Expected shape: CO2 enrichment in the permeate")

length_fraction = np.linspace(0, 1, 80)
selectivity = config_sketch["transport"]["permeance"]["CO2"] / \
              config_sketch["transport"]["permeance"]["N2"]

# Simple monotonic curves with the right qualitative behavior.
co2_feed = 0.15 * np.exp(-1.8 * length_fraction)
co2_permeate = 0.15 + (selectivity / (selectivity + 12)) \
    * (1 - np.exp(-2.2 * length_fraction)) * 0.55

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(length_fraction, co2_feed, color="crimson", linewidth=2,
        label="CO2 in feed (retentate side)")
ax.plot(length_fraction, co2_permeate, color="darkorange", linewidth=2,
        label="CO2 in permeate")
ax.set_xlabel("Fractional length along fiber")
ax.set_ylabel("CO2 mole fraction")
ax.set_title(f"Co-current HFM, CO2/N2 selectivity ≈ {selectivity:.0f}")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
display(fig, append=True)
