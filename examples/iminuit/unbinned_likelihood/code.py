# ---------------------------------------------------------------------
# Unbinned maximum-likelihood fit of a Gaussian, with parameter limits.
# ---------------------------------------------------------------------

heading("Estimating a Gaussian's parameters from samples")
note(
    "Imagine a sensor reports 800 measurements that we expect to be "
    "Gaussian-distributed. UnbinnedNLL fits the probability density "
    "directly to the individual samples &mdash; no histogram needed."
)

# True (unknown to the fitter) population parameters.
true_mu, true_sigma = 2.5, 0.8
samples = rng.normal(true_mu, true_sigma, size=800)


# An unbinned NLL needs a *normalized* probability density function.
def gaussian_pdf(x, mu, sigma):
    return norm.pdf(x, mu, sigma)


cost = UnbinnedNLL(samples, gaussian_pdf)

minuit = Minuit(cost, mu=0.0, sigma=1.0)

# Constrain sigma to be positive: parameter limits are set like a dict.
minuit.limits["sigma"] = (1e-3, None)

minuit.migrad()
minuit.hesse()

note("Best-fit parameters:")
display(minuit.values.to_dict(), append=True)
note("One-sigma errors:")
display(minuit.errors.to_dict(), append=True)
note(
    f"True values were mu = {true_mu}, sigma = {true_sigma}. "
    f"Minimum valid: <strong>{minuit.valid}</strong>."
)

# Overlay the fitted PDF on a histogram of the samples.
fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(samples, bins=40, density=True, color="lightsteelblue",
        edgecolor="white", label="Samples")
x_grid = np.linspace(samples.min(), samples.max(), 200)
ax.plot(x_grid, gaussian_pdf(x_grid, *minuit.values),
        color="darkblue", linewidth=2, label="Fitted Gaussian")
ax.set_xlabel("x")
ax.set_ylabel("density")
ax.set_title("Unbinned maximum-likelihood fit")
ax.legend()
fig.tight_layout()
display(fig, append=True)
