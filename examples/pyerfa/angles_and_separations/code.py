# ---------------------------------------------------------------------
# Sexagesimal parsing, angular separations, and great-circle distances.
# ---------------------------------------------------------------------
#
# ERFA includes a rich set of angle utilities. Here we'll parse
# right-ascension and declination strings, then use erfa.seps to
# compute the angular separation between bright stars.

heading("Parsing RA/Dec strings into radians")
note(
    "erfa.tf2a converts a sign + hours/minutes/seconds tuple to "
    "radians (hours form), and erfa.af2a does the same for "
    "degrees/arcminutes/arcseconds."
)

stars = [
    # (name, RA h/m/s, Dec sign/d/m/s)
    ("Sirius",   ( 6,  45,  8.92), ("-", 16, 42, 58.0)),
    ("Canopus",  ( 6, 23, 57.11), ("-", 52, 41, 44.4)),
    ("Vega",     (18, 36, 56.34), ("+", 38, 47,  1.3)),
    ("Betelgeuse", (5, 55, 10.31), ("+",  7, 24, 25.4)),
    ("Rigel",    ( 5, 14, 32.27), ("-",  8, 12,  6.0)),
]

# Build arrays of RA and Dec in radians.
names = [s[0] for s in stars]
ra_rad = np.array([erfa.tf2a("+", h, m, s) for _, (h, m, s), _ in stars])
dec_rad = np.array([erfa.af2a(sign, d, m, s) for _, _, (sign, d, m, s) in stars])

note("Star catalogue (RA, Dec converted to degrees for display):")
rows = ["<tr><th>Name</th><th>RA (deg)</th><th>Dec (deg)</th></tr>"]
for name, ra, dec in zip(names, np.degrees(ra_rad), np.degrees(dec_rad)):
    rows.append(f"<tr><td>{name}</td><td>{ra:.4f}</td><td>{dec:+.4f}</td></tr>")
display(HTML("<table>" + "".join(rows) + "</table>"), append=True)


heading("Pairwise angular separations")
note(
    "erfa.seps takes (lon1, lat1, lon2, lat2) in radians and "
    "returns the great-circle separation in radians. We broadcast "
    "it over all pairs at once."
)

# Broadcast: compare every star against every other star.
sep_rad = erfa.seps(
    ra_rad[:, None], dec_rad[:, None],
    ra_rad[None, :], dec_rad[None, :],
)
sep_deg = np.degrees(sep_rad)

# Render as an HTML table.
header = "<tr><th></th>" + "".join(f"<th>{n}</th>" for n in names) + "</tr>"
body = []
for i, name in enumerate(names):
    cells = "".join(f"<td>{sep_deg[i, j]:6.2f}</td>" for j in range(len(names)))
    body.append(f"<tr><th>{name}</th>{cells}</tr>")
display(HTML("<table>" + header + "".join(body) + "</table>"), append=True)


heading("Closest pair in the catalogue")
# Mask the diagonal (self-separations are zero) and find the minimum.
mask = sep_deg + np.eye(len(names)) * 1e6
i, j = np.unravel_index(np.argmin(mask), mask.shape)
note(
    f"Closest pair: <strong>{names[i]}</strong> and "
    f"<strong>{names[j]}</strong>, separated by "
    f"<strong>{sep_deg[i, j]:.2f}°</strong>."
)
