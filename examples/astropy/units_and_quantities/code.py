"""
A first taste of astropy: physical quantities with units.

Astropy's `units` sub-package lets you attach physical units to numbers
so calculations carry their units along, convert between them, and
catch dimensional mistakes. Combined with `astropy.constants`, you can
write physics in code that reads almost like a textbook.

Docs: https://docs.astropy.org/en/stable/units/
"""
from IPython.core.display import display, HTML


import astropy.units as u
from astropy.constants import G, M_sun, R_sun, c


heading("1. Attach units to numbers")
note(
    "Multiply a value by a unit to get a Quantity. Quantities behave "
    "like numbers but remember what they are."
)

distance_to_moon = 384_400 * u.km
flight_time = 3 * u.day
average_speed = distance_to_moon / flight_time

note(
    f"A spacecraft covering {distance_to_moon} in {flight_time} "
    f"averages <strong>{average_speed.to(u.km / u.h):.0f}</strong>."
)

heading("2. Unit conversion")
note("Use `.to(...)` to convert between compatible units.")

wavelength = 656.3 * u.nm  # H-alpha line
display(HTML(
    f"<ul>"
    f"<li>{wavelength} = {wavelength.to(u.angstrom)}</li>"
    f"<li>{wavelength} = {wavelength.to(u.m):.3e}</li>"
    f"</ul>"
), append=True)

# Frequency from wavelength using the speed of light constant.
frequency = (c / wavelength).to(u.THz)
note(f"H-alpha frequency: <strong>{frequency:.3f}</strong>.")

heading("3. Physics with constants: escape velocity from the Sun")
note(
    "The escape velocity from a body of mass M and radius R is "
    "v = sqrt(2 G M / R). Astropy carries the units through, so the "
    "answer comes out in m/s without manual bookkeeping."
)

escape_velocity = ((2 * G * M_sun / R_sun) ** 0.5).to(u.km / u.s)
note(f"Solar escape velocity: <strong>{escape_velocity:.1f}</strong>.")

heading("4. Units catch mistakes")
note(
    "Adding incompatible units raises a UnitConversionError. Try "
    "uncommenting the broken line below to see it fail loudly."
)
safe_sum = 5 * u.m + 30 * u.cm
note(f"5 m + 30 cm = {safe_sum.to(u.m)}")
# broken = 5 * u.m + 30 * u.kg  # would raise UnitConversionError
