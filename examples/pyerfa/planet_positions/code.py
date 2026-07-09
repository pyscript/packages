# ---------------------------------------------------------------------
# Plotting the inner planets' orbits using erfa.plan94.
# ---------------------------------------------------------------------
#
# erfa.plan94 gives heliocentric position and velocity (in AU and
# AU/day) for planets 1..8 (Mercury through Neptune) using an
# analytical approximation accurate enough for many purposes.

import numpy as np
import matplotlib.pyplot as plt
import erfa


heading("Tracing the inner planets over one Earth-year")
note(
    "We sample plan94 every few days for a full year starting "
    "on JD 2460000.5 and project the heliocentric positions onto "
    "the ecliptic plane (X, Y in AU)."
)

planets = {
    1: ("Mercury", "tab:gray"),
    2: ("Venus",   "tab:orange"),
    3: ("Earth",   "tab:blue"),
    4: ("Mars",    "tab:red"),
}

jd_base = 2460000.5
days = np.arange(0, 700, 2.0)  # enough to close Mars' orbit too

fig, ax = plt.subplots(figsize=(6, 6))
ax.plot(0, 0, marker="*", color="gold", markersize=18, label="Sun")

for planet_id, (name, color) in planets.items():
    pv = erfa.plan94(jd_base, days, planet_id)
    # pv is a structured array with fields 'p' (position) and 'v' (velocity).
    x = pv["p"][:, 0]
    y = pv["p"][:, 1]
    ax.plot(x, y, color=color, linewidth=1.2, label=name)
    # Mark the starting position.
    ax.plot(x[0], y[0], "o", color=color, markersize=5)

ax.set_aspect("equal")
ax.set_xlabel("X (AU)")
ax.set_ylabel("Y (AU)")
ax.set_title("Inner planets, heliocentric ecliptic plane")
ax.legend(loc="upper right", fontsize=9)
ax.grid(alpha=0.3)
fig.tight_layout()
display(fig, append=True)

# How far is each planet from the Sun on day zero?
heading("Heliocentric distances on the start date")
pv0 = erfa.plan94(jd_base, 0.0, 3)  # Earth as a check: should be ~1 AU
note(f"Earth's distance from the Sun on JD {jd_base}: "
     f"<strong>{np.linalg.norm(pv0['p']):.4f} AU</strong>")

for planet_id, (name, _) in planets.items():
    pv = erfa.plan94(jd_base, 0.0, planet_id)
    r = np.linalg.norm(pv["p"])
    note(f"{name}: {r:.4f} AU")
