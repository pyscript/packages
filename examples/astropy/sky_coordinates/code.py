# ---------------------------------------------------------------------
# Working with sky coordinates: SkyCoord, frames, and separations.
# ---------------------------------------------------------------------


import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u
from astropy.coordinates import SkyCoord


heading("Locating things on the sky")
note(
    "`SkyCoord` represents positions on the celestial sphere. You can "
    "build it from sexagesimal strings, decimal degrees, or arrays, "
    "convert between frames, and compute angular separations."
)

# A handful of famous objects, in equatorial (ICRS) coordinates.
names = ["Sirius", "Betelgeuse", "Vega", "Polaris", "Andromeda (M31)"]
catalog = SkyCoord(
    ra=["06h45m08.9s", "05h55m10.3s", "18h36m56.3s",
        "02h31m49.1s", "00h42m44.3s"],
    dec=["-16d42m58s", "+07d24m25s", "+38d47m01s",
         "+89d15m51s", "+41d16m09s"],
    frame="icrs",
)

note("Decimal-degree view of the catalog:")
for name, coord in zip(names, catalog):
    display(HTML(
        f"<code>{name:<18}</code> "
        f"RA = {coord.ra.deg:7.3f}°, Dec = {coord.dec.deg:+7.3f}°"
    ), append=True)

heading("Angular separations from Sirius")
sirius = catalog[0]
separations = catalog.separation(sirius).to(u.deg)
for name, sep in zip(names, separations):
    note(f"{name}: <strong>{sep:.2f}</strong> from Sirius")

heading("Convert to Galactic coordinates")
note(
    "The same positions in the Galactic frame, where the plane of "
    "the Milky Way lies along b = 0°."
)
galactic = catalog.galactic
for name, coord in zip(names, galactic):
    display(HTML(
        f"<code>{name:<18}</code> "
        f"l = {coord.l.deg:7.3f}°, b = {coord.b.deg:+7.3f}°"
    ), append=True)

# Plot the catalog on an Aitoff projection in Galactic coordinates.
fig = plt.figure(figsize=(9, 4.5))
ax = fig.add_subplot(111, projection="aitoff")

# Aitoff expects longitudes in radians, wrapped to [-pi, pi].
l_rad = galactic.l.wrap_at(180 * u.deg).radian
b_rad = galactic.b.radian

ax.scatter(l_rad, b_rad, s=60, color="crimson", zorder=3)
for name, l, b in zip(names, l_rad, b_rad):
    ax.text(l, b + 0.05, name, ha="center", fontsize=9)

ax.grid(True)
ax.set_title("Famous objects in Galactic coordinates", pad=20)
fig.tight_layout()
display(fig, append=True)
