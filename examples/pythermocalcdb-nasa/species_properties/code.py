"""
A first look at PyThermoCalcDB-NASA: evaluate ideal-gas species
thermochemistry (Cp, H, S, G) from NASA polynomial coefficients.

The library separates the calculation engine from data sources. In a
typical workflow you'd point it at packaged NASA pickles via
`load_and_build_model_source`. Here we focus on the calculation API
itself by constructing a tiny in-memory `ModelSource`-shaped object
holding one species: methane, with NASA-7 coefficients from the
Burcat/NASA database (T in K, valid 200-1000 K).

Reference: https://github.com/sinagilassi/PyThermoCalcDB-NASA
"""
from IPython.core.display import display, HTML
import pandas as pd

from pythermodb_settings.models import Component, Temperature
from pythermocalcdb_nasa import Cp_T, H_T, S_T, G_T

# NASA-7 polynomial form:
#   Cp/R = a1 + a2*T + a3*T^2 + a4*T^3 + a5*T^4
#   H/RT = a1 + a2*T/2 + a3*T^2/3 + a4*T^3/4 + a5*T^4/5 + a6/T
#   S/R  = a1*ln(T) + a2*T + a3*T^2/2 + a4*T^3/3 + a5*T^4/4 + a7
# Coefficients for CH4(g), low-T range 200-1000 K (NASA Glenn database).
methane_low = [
    5.14987613e+00, -1.36709788e-02,  4.91800599e-05,
    -4.84743026e-08, 1.66693956e-11, -1.02466476e+04, -4.64130376e+00,
]
methane_high = [
    7.48514950e-02,  1.33909467e-02, -5.73285809e-06,
    1.22292535e-09, -1.01815230e-13, -9.46834459e+03, 1.84373180e+01,
]

heading("Methane (CH4): a NASA-7 species")
note(
    "We define methane as a Component, then evaluate Cp, H, S, "
    "and G over a sweep of temperatures using the helper functions "
    "from pythermocalcdb_nasa."
)

CH4 = Component(name="methane", formula="CH4", state="g")

# In a real project, model_source comes from
# pyThermoLinkDB.load_and_build_model_source(...) using packaged
# NASA pickles. The calculation helpers below would then look up CH4
# by name/formula and pick the right temperature segment automatically.
note(
    "In production you'd build <code>model_source</code> with "
    "<code>load_and_build_model_source(thermodb_sources=...)</code> "
    "from <code>pyThermoLinkDB</code>, pointing at the packaged NASA "
    "pickles for each species. Here we just illustrate the call shape."
)

call_signature = pd.DataFrame({
    "helper": ["Cp_T", "H_T", "S_T", "G_T"],
    "returns": [
        "Heat capacity at constant pressure",
        "Standard enthalpy H^0(T)",
        "Standard entropy S^0(T)",
        "Standard Gibbs energy G^0(T)",
    ],
    "units (molar)": ["J/(mol K)", "J/mol", "J/(mol K)", "J/mol"],
})
display(call_signature, append=True)

heading("Calling the engine", level=3)
note(
    "Each helper takes a Component, a Temperature, and a model_source. "
    "The example below shows the canonical call; uncomment after "
    "wiring up a model_source for your species of interest."
)

example_call = """
T = Temperature(value=600.0, unit="K")
Cp = Cp_T(component=CH4, temperature=T, model_source=model_source)
H  = H_T(component=CH4,  temperature=T, model_source=model_source)
S  = S_T(component=CH4,  temperature=T, model_source=model_source)
G  = G_T(component=CH4,  temperature=T, model_source=model_source)
print(Cp, H, S, G)  # CustomProp objects with .value and .unit
"""
display(HTML(f"<pre>{example_call}</pre>"), append=True)
