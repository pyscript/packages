"""
A first taste of autograd: differentiating plain Python+NumPy code.

Autograd's core idea: write a regular Python function using
`autograd.numpy` (a drop-in for NumPy), then call `grad(f)` to get a
new function that returns the gradient of `f`. No symbolic math, no
graph construction up front.

Docs: https://github.com/HIPS/autograd/blob/master/docs/tutorial.md
"""
from IPython.core.display import display, HTML


# ---------------------------------------------------------------------
# A scalar function and its derivative.
# ---------------------------------------------------------------------

heading("1. From function to gradient in one line")
note(
    "We define a smooth scalar function (a hyperbolic tangent), "
    "then ask autograd for its derivative. Notice that we never "
    "wrote the derivative formula by hand."
)


def tanh(x):
    """A textbook tanh, written with autograd's NumPy."""
    return (1.0 - np.exp(-2 * x)) / (1.0 + np.exp(-2 * x))


# `grad` returns a NEW function. Calling it gives back the derivative
# value at the point you pass in.
d_tanh = grad(tanh)

note(
    f"tanh(1.0) = {tanh(1.0):.6f}<br>"
    f"d/dx tanh at x=1.0 (autograd) = {d_tanh(1.0):.6f}<br>"
    f"finite-difference check     = "
    f"{(tanh(1.0001) - tanh(0.9999)) / 0.0002:.6f}"
)

# ---------------------------------------------------------------------
# Plot tanh and several of its derivatives.
# ---------------------------------------------------------------------

heading("2. Higher-order derivatives, vectorized")
note(
    "Use <code>elementwise_grad</code> when you want a derivative "
    "that broadcasts across an array of inputs (handy for plotting). "
    "It's safe to nest: differentiate the derivative, and so on."
)

x = np.linspace(-5, 5, 400)

# elementwise_grad makes the derivative function operate per-element
# across an input array, instead of expecting a scalar.
d1 = elementwise_grad(tanh)
d2 = elementwise_grad(d1)
d3 = elementwise_grad(d2)

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(x, tanh(x), label="tanh(x)", linewidth=2)
ax.plot(x, d1(x), label="1st derivative")
ax.plot(x, d2(x), label="2nd derivative")
ax.plot(x, d3(x), label="3rd derivative")
ax.axhline(0, color="black", linewidth=0.5)
ax.set_title("tanh and its first three derivatives")
ax.legend(loc="upper right")
fig.tight_layout()
display(fig, append=True)
