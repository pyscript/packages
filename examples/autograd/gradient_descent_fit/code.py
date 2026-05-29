# ---------------------------------------------------------------------
# Using grad to fit a model: classic gradient descent.
# ---------------------------------------------------------------------

heading("Fitting a noisy sine wave with gradient descent")
note(
    "We'll fit the model <code>y = a * sin(b * x + c) + d</code> "
    "to noisy data. Autograd gives us the gradient of the loss "
    "with respect to the four parameters, so we can update them "
    "directly without writing any partial derivatives."
)

# Synthetic data: a sine wave with noise.
true_params = np.array([2.0, 1.3, 0.5, 0.4])
x_data = np.linspace(-3, 3, 80)
noise = rng.normal(0, 0.25, size=x_data.shape)
y_data = (
    true_params[0] * np.sin(true_params[1] * x_data + true_params[2])
    + true_params[3]
    + noise
)


def model(params, x):
    """Sinusoid with offset, parameterized by (a, b, c, d)."""
    a, b, c, d = params
    return a * np.sin(b * x + c) + d


def loss(params):
    """Mean squared error between model prediction and noisy data."""
    residuals = model(params, x_data) - y_data
    return np.mean(residuals ** 2)


# `grad(loss)` returns a function that, given params, yields the
# gradient of the loss w.r.t. each parameter as an array.
loss_grad = grad(loss)

# Vanilla gradient descent. Initialize away from the truth so you can
# watch the loss come down.
params = np.array([1.0, 1.0, 0.0, 0.0])
learning_rate = 0.05
loss_history = []

for step in range(400):
    g = loss_grad(params)
    params = params - learning_rate * g
    loss_history.append(loss(params))

note(
    f"True params:    {np.round(true_params, 3).tolist()}<br>"
    f"Fitted params:  {np.round(params, 3).tolist()}<br>"
    f"Final loss:     {loss_history[-1]:.4f}"
)

# Plot data, fit, and the loss curve side by side.
fig, (ax_fit, ax_loss) = plt.subplots(1, 2, figsize=(10, 4))

ax_fit.scatter(x_data, y_data, s=18, color="gray", label="data")
x_grid = np.linspace(-3, 3, 300)
ax_fit.plot(
    x_grid, model(params, x_grid),
    color="crimson", linewidth=2, label="autograd fit",
)
ax_fit.set_title("Model fit")
ax_fit.legend()

ax_loss.plot(loss_history, color="steelblue")
ax_loss.set_title("Training loss")
ax_loss.set_xlabel("step")
ax_loss.set_ylabel("MSE")
ax_loss.set_yscale("log")

fig.tight_layout()
display(fig, append=True)
