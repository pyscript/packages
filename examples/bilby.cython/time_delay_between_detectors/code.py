# ---------------------------------------------------------------------
# Use time_delay_geocentric to triangulate sources between two sites.
# ---------------------------------------------------------------------

heading("Time delays between LIGO Hanford and LIGO Livingston")
note(
    "A gravitational wave from a given sky direction arrives at the "
    "two LIGO sites at slightly different times — up to about ±10 ms "
    "for the H-L baseline. bilby.cython's <code>time_delay_geocentric"
    "</code> takes the two detector positions (in Earth-centered "
    "Cartesian coordinates, in meters) and returns the delay."
)

# Approximate Earth-centered positions of the two LIGO sites, in meters.
hanford_position = np.array([-2.1614e6, -3.8347e6, 4.6004e6])
livingston_position = np.array([-7.4276e4, -5.4961e6, 3.2243e6])

gps_time = 1126259642.413

# Sweep right ascension at two declinations and record the H–L delay.
ra_values = np.linspace(0, 2 * np.pi, 361)
declinations = {"equator (dec = 0)": 0.0, "high north (dec = +60°)": np.pi / 3}

fig, ax = plt.subplots(figsize=(9, 4))
for label, dec in declinations.items():
    delays_ms = np.array([
        geometry.time_delay_geocentric(
            detector1=hanford_position,
            detector2=livingston_position,
            ra=ra,
            dec=dec,
            time=gps_time,
        )
        for ra in ra_values
    ]) * 1000.0
    ax.plot(np.degrees(ra_values), delays_ms, label=label)

ax.axhline(0, color="gray", linewidth=0.8)
ax.set_xlabel("Right ascension (degrees)")
ax.set_ylabel("Hanford − Livingston arrival delay (ms)")
ax.set_title("H–L time delay vs. sky position")
ax.legend()
fig.tight_layout()
display(fig, append=True)

heading("Localizing GW150914 from its measured delay")
note(
    "GW150914 arrived at Livingston about 6.9 ms before Hanford. "
    "We can find every sky direction consistent with that delay by "
    "scanning the sky and keeping points whose predicted delay "
    "matches, within tolerance — this gives the familiar ring on "
    "the sky from a two-detector network."
)

measured_delay_s = -0.0069  # H minus L, seconds
tolerance_s = 2e-4

n_ra, n_dec = 360, 180
ra_grid = np.linspace(0, 2 * np.pi, n_ra)
dec_grid = np.linspace(-np.pi / 2, np.pi / 2, n_dec)

delay_map = np.empty((n_dec, n_ra))
for i, dec in enumerate(dec_grid):
    for j, ra in enumerate(ra_grid):
        delay_map[i, j] = geometry.time_delay_geocentric(
            detector1=hanford_position,
            detector2=livingston_position,
            ra=ra, dec=dec, time=gps_time,
        )

consistent = np.abs(delay_map - measured_delay_s) < tolerance_s
note(
    f"Sky pixels consistent with a {measured_delay_s * 1000:+.1f} ms "
    f"delay: <strong>{consistent.sum()}</strong> out of "
    f"{consistent.size}."
)

fig, ax = plt.subplots(figsize=(9, 4))
extent = [0, 360, -90, 90]
ax.imshow(
    delay_map * 1000.0, origin="lower", extent=extent,
    aspect="auto", cmap="RdBu", vmin=-11, vmax=11,
)
ax.contour(
    np.degrees(ra_grid), np.degrees(dec_grid), consistent.astype(float),
    levels=[0.5], colors="black", linewidths=1.5,
)
ax.set_xlabel("Right ascension (degrees)")
ax.set_ylabel("Declination (degrees)")
ax.set_title("H–L delay (ms); ring = directions matching GW150914")
fig.tight_layout()
display(fig, append=True)
