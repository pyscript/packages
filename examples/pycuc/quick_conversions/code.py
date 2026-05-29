"""
A first look at PyCUC: convert quantities between units in a single
line, using either a from/to pair or a compact "MPa => Pa" string.

PyCUC bundles conversions for many physical quantities (pressure,
temperature, energy, length, mass, volume, ...). See the project
docs at https://github.com/sinagilassi/pycuc for the full list.
"""
from IPython.core.display import display, HTML

heading("Reactor pressure: from megapascals to friendlier units")
note(
    "An engineer recorded a reactor pressure of 2.5 MPa and wants "
    "to share it in pascals, bar, and psi for different audiences."
)

reactor_pressure_mpa = 2.5

# convert_from_to(value, from_unit, to_unit) is the most explicit form.
in_pascals = pycuc.convert_from_to(reactor_pressure_mpa, "MPa", "Pa")
in_bar = pycuc.convert_from_to(reactor_pressure_mpa, "MPa", "bar")
in_psi = pycuc.convert_from_to(reactor_pressure_mpa, "MPa", "psi")

note(
    f"{reactor_pressure_mpa} MPa is "
    f"<strong>{in_pascals:,.0f} Pa</strong>, "
    f"<strong>{in_bar:.2f} bar</strong>, "
    f"and <strong>{in_psi:.2f} psi</strong>."
)

heading("The shorthand: pycuc.to(value, 'from => to')")
note(
    "If you prefer something terser, pycuc.to() takes a single "
    "string describing the conversion."
)

oven_temperature_c = 180.0
oven_in_kelvin = pycuc.to(oven_temperature_c, "C => K")
oven_in_fahrenheit = pycuc.to(oven_temperature_c, "C => F")

note(
    f"An oven at {oven_temperature_c} &deg;C is "
    f"<strong>{oven_in_kelvin:.2f} K</strong> or "
    f"<strong>{oven_in_fahrenheit:.1f} &deg;F</strong>."
)

heading("Discovering what units are available")
note(
    "pycuc.check_reference(category) lists the units PyCUC knows "
    "about for a given quantity. Here are the pressure units:"
)

pressure_units = pycuc.check_reference("pressure")
display(pressure_units, append=True)
