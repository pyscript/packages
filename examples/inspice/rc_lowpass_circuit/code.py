"""
A first look at InSpice: describing an electronic circuit in Python.

InSpice (a fork of PySpice) lets you build SPICE netlists from Python
objects, then hand them off to a simulator like Ngspice or Xyce.
In this first example we'll just build a circuit and inspect the
netlist InSpice generates for us.

See https://github.com/Innovoltive/InSpice for documentation.
"""
from IPython.core.display import display, HTML

# A classic RC low-pass filter:
#
#     Vin o---[ R1 ]---+---o Vout
#                      |
#                    [ C1 ]
#                      |
#                     GND
#
# The cutoff frequency is f_c = 1 / (2 * pi * R * C).

heading("1. Describing an RC low-pass filter")
note(
    "We give the circuit a name, then add components by calling "
    "methods on it. The single-letter method picks the SPICE "
    "device type: R for resistor, C for capacitor, V for voltage "
    "source. Nodes are just strings -- here 'input', 'output', "
    "and the built-in ground reference."
)

circuit = Circuit("RC low-pass filter")

# A 1 V AC source between the 'input' node and ground.
circuit.SinusoidalVoltageSource(
    "input", "input", circuit.gnd,
    amplitude=1 @ u_V, frequency=1 @ u_kHz,
)
# Resistor R1 between 'input' and 'output'.
circuit.R(1, "input", "output", 1 @ u_kOhm)
# Capacitor C1 between 'output' and ground.
circuit.C(1, "output", circuit.gnd, 1 @ u_uF)

note("InSpice rendered our circuit as the following SPICE netlist:")
display(HTML(f"<pre>{circuit}</pre>"), append=True)

# Component values are first-class Python objects with units.
r1 = circuit["R1"]
c1 = circuit["C1"]
note(
    f"R1 = {r1.resistance}, C1 = {c1.capacitance}. "
    "The <code>@</code> operator attaches a unit, and the "
    "resulting quantity behaves like a number in arithmetic."
)

# Compute the theoretical cutoff frequency from the component values.
r_value = float(r1.resistance)       # ohms
c_value = float(c1.capacitance)      # farads
f_cutoff = 1.0 / (2.0 * np.pi * r_value * c_value)

note(
    f"Theoretical cutoff frequency: "
    f"<strong>{f_cutoff:,.1f} Hz</strong> "
    f"({f_cutoff / 1000:.2f} kHz)."
)

# Plot the analytic magnitude response |H(f)| = 1 / sqrt(1 + (f/f_c)^2).
frequencies = np.logspace(1, 6, 400)
magnitude_db = 20 * np.log10(
    1.0 / np.sqrt(1.0 + (frequencies / f_cutoff) ** 2)
)

fig, ax = plt.subplots(figsize=(8, 4))
ax.semilogx(frequencies, magnitude_db, color="steelblue", linewidth=2)
ax.axvline(f_cutoff, color="darkorange", linestyle="--",
           label=f"f_c = {f_cutoff:,.0f} Hz")
ax.axhline(-3, color="gray", linestyle=":", label="-3 dB")
ax.set_title("RC low-pass filter: analytic frequency response")
ax.set_xlabel("Frequency (Hz)")
ax.set_ylabel("Gain (dB)")
ax.grid(True, which="both", alpha=0.3)
ax.legend()
fig.tight_layout()
display(fig, append=True)
