# ---------------------------------------------------------------------
# Fitting a model to noisy spectral data with astropy.modeling.
# ---------------------------------------------------------------------

heading("Fitting an emission line")
note(
    "Astropy's `modeling` framework lets you compose analytic models "
    "(Gaussians, polynomials, ...) and fit them to data. Here we "
    "simulate a noisy emission line on a sloping continuum, then "
    "recover both components by fitting their sum."
)

# Synthetic spectrum: a Gaussian emission line on a linear continuum.
wavelengths = np.linspace(6520, 6600, 300)  # angstroms, around H-alpha

true_continuum = models.Linear1D(slope=-0.005, intercept=4.0)
true_line = models.Gaussian1D(amplitude=3.5, mean=6562.8, stddev=2.1)
true_spectrum = true_continuum + true_line

clean_flux = true_spectrum(wavelengths)
observed_flux = clean_flux + rng.normal(0, 0.15, size=wavelengths.size)

# Build an initial-guess compound model and fit it. The starting
# parameters don't need to be exact -- just in the right ballpark.
initial_model = (
    models.Linear1D(slope=0.0, intercept=4.0)
    + models.Gaussian1D(amplitude=2.0, mean=6560.0, stddev=3.0)
)
fitter = fitting.LevMarLSQFitter()
fitted_model = fitter(initial_model, wavelengths, observed_flux)

# Pull out the fitted Gaussian sub-model for a tidy report.
fitted_continuum = fitted_model[0]
fitted_line = fitted_model[1]

note("Recovered parameters (true values in parentheses):")
display(HTML(
    f"<ul>"
    f"<li>Line center: <strong>{fitted_line.mean.value:.2f} Å</strong> "
    f"(true 6562.80)</li>"
    f"<li>Line amplitude: "
    f"<strong>{fitted_line.amplitude.value:.2f}</strong> "
    f"(true 3.50)</li>"
    f"<li>Line width (σ): "
    f"<strong>{fitted_line.stddev.value:.2f} Å</strong> (true 2.10)</li>"
    f"<li>Continuum slope: "
    f"<strong>{fitted_continuum.slope.value:+.4f}</strong> "
    f"(true -0.0050)</li>"
    f"</ul>"
), append=True)

# Line FWHM with units, derived from the fitted standard deviation.
fwhm = 2 * np.sqrt(2 * np.log(2)) * fitted_line.stddev.value * u.angstrom
note(f"Fitted FWHM: <strong>{fwhm:.2f}</strong>.")

# Plot the data, the fitted model, and its components.
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(wavelengths, observed_flux, ".", color="lightgray",
        label="Observed", markersize=4)
ax.plot(wavelengths, fitted_model(wavelengths),
        color="crimson", linewidth=2, label="Fitted model")
ax.plot(wavelengths, fitted_continuum(wavelengths),
        color="steelblue", linestyle="--", label="Fitted continuum")
ax.axvline(fitted_line.mean.value, color="darkorange",
           linestyle=":", label="Fitted line center")

ax.set_xlabel("Wavelength (Å)")
ax.set_ylabel("Flux (arbitrary units)")
ax.set_title("Gaussian + linear continuum fit near H-α")
ax.legend(loc="upper right")
fig.tight_layout()
display(fig, append=True)
