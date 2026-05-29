# ---------------------------------------------------------------------
# Sweep the sky and plot |F+|, |F×| for a single detector.
# ---------------------------------------------------------------------

heading("How sensitive is the detector across the whole sky?")
note(
    "We evaluate the plus and cross antenna pattern factors on a grid "
    "of right ascension and declination, holding polarization angle "
    "and time fixed. The result is the classic four-lobed beam "
    "pattern of an L-shaped interferometer."
)

# Same toy LIGO-Hanford-like detector tensor as before.
x_arm = np.array([-0.2239, 0.7998, 0.5569])
y_arm = np.array([-0.9140, 0.0261, -0.4049])
detector_tensor = 0.5 * (np.outer(x_arm, x_arm) - np.outer(y_arm, y_arm))

n_ra, n_dec = 120, 60
ra_grid = np.linspace(0, 2 * np.pi, n_ra)
dec_grid = np.linspace(-np.pi / 2, np.pi / 2, n_dec)

f_plus_map = np.empty((n_dec, n_ra))
f_cross_map = np.empty((n_dec, n_ra))

psi = 0.0
gps_time = 1126259642.413

# bilby.cython is fast per call, so a simple double loop is fine for
# a 7,200-point grid like this.
for i, dec in enumerate(dec_grid):
    for j, ra in enumerate(ra_grid):
        e_plus = geometry.get_polarization_tensor(
            ra=ra, dec=dec, time=gps_time, psi=psi, mode="plus",
        )
        e_cross = geometry.get_polarization_tensor(
            ra=ra, dec=dec, time=gps_time, psi=psi, mode="cross",
        )
        f_plus_map[i, j] = geometry.three_by_three_matrix_contraction(
            detector_tensor, e_plus,
        )
        f_cross_map[i, j] = geometry.three_by_three_matrix_contraction(
            detector_tensor, e_cross,
        )

# The "sensitivity" envelope is sqrt(F+^2 + Fx^2).
sensitivity = np.sqrt(f_plus_map**2 + f_cross_map**2)

note(
    f"Peak |F+| = {np.abs(f_plus_map).max():.3f}, "
    f"peak |F×| = {np.abs(f_cross_map).max():.3f}, "
    f"peak combined sensitivity = {sensitivity.max():.3f}."
)

fig, axes = plt.subplots(1, 3, figsize=(12, 3.6))
extent = [0, 2 * np.pi, -np.pi / 2, np.pi / 2]
panels = [
    ("|F+|", np.abs(f_plus_map), "viridis"),
    ("|F×|", np.abs(f_cross_map), "viridis"),
    ("sqrt(F+² + F×²)", sensitivity, "magma"),
]
for ax, (label, data, cmap) in zip(axes, panels):
    image = ax.imshow(
        data, origin="lower", extent=extent, aspect="auto", cmap=cmap,
    )
    ax.set_title(label)
    ax.set_xlabel("Right ascension (rad)")
    ax.set_ylabel("Declination (rad)")
    fig.colorbar(image, ax=ax, shrink=0.85)
fig.suptitle("Antenna pattern of an L-shaped detector")
fig.tight_layout()
display(fig, append=True)
