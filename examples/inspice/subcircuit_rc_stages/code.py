# ---------------------------------------------------------------------
# Defining a reusable RC stage as a SubCircuit and cascading copies.
# ---------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
import InSpice
from InSpice import Circuit, SubCircuit, SubCircuitFactory
from InSpice.Unit import u_V, u_Hz, u_Ohm, u_uF, u_kHz, u_kOhm, u_ms


heading("3. Cascading RC stages with SubCircuit")
note(
    "Real schematics repeat the same pattern many times. InSpice's "
    "<code>SubCircuitFactory</code> lets you define a block once, "
    "give it named external pins, and then drop instances of it "
    "into a parent circuit. Here we make a one-pole RC stage and "
    "cascade three of them to build a third-order filter."
)


class RCStage(SubCircuitFactory):
    """A single RC low-pass stage with input and output pins."""

    NAME = "rc_stage"
    NODES = ("input", "output")

    def __init__(self, resistance=1 @ u_kOhm, capacitance=100 * u_uF(0.001)):
        super().__init__()
        # Resistor between the external 'input' and 'output' pins.
        self.R(1, "input", "output", resistance)
        # Capacitor from 'output' to the subcircuit's local ground.
        self.C(1, "output", self.gnd, capacitance)


cascade = Circuit("Three-stage RC cascade")
cascade.SinusoidalVoltageSource(
    "src", "input", cascade.gnd,
    amplitude=1 @ u_V, frequency=1 @ u_kHz,
)
# Register the subcircuit definition once...
cascade.subcircuit(RCStage(resistance=1 @ u_kOhm,
                           capacitance=100 * u_uF(0.001)))

# ...then instantiate it three times, wiring stage outputs to the
# next stage's input.
cascade.X("stage1", "rc_stage", "input", "n1")
cascade.X("stage2", "rc_stage", "n1", "n2")
cascade.X("stage3", "rc_stage", "n2", "output")

note("The generated netlist shows both the .subckt block and the X-instances:")
display(HTML(f"<pre>{cascade}</pre>"), append=True)

# Each identical RC stage multiplies the transfer function, so the
# cascade has a steeper roll-off than a single stage. We can compare
# the analytic magnitude responses side-by-side.
r_value = 1_000.0           # 1 kOhm
c_value = 0.1e-6            # 0.1 uF
f_cutoff = 1.0 / (2.0 * np.pi * r_value * c_value)

frequencies = np.logspace(1, 7, 400)
single_stage = 1.0 / np.sqrt(1.0 + (frequencies / f_cutoff) ** 2)
three_stage = single_stage ** 3

fig, ax = plt.subplots(figsize=(8, 4))
ax.semilogx(frequencies, 20 * np.log10(single_stage),
            color="steelblue", linewidth=2, label="1 RC stage")
ax.semilogx(frequencies, 20 * np.log10(three_stage),
            color="crimson", linewidth=2, label="3 cascaded stages")
ax.axvline(f_cutoff, color="gray", linestyle="--",
           label=f"f_c = {f_cutoff:,.0f} Hz")
ax.axhline(-3, color="gray", linestyle=":", alpha=0.6)
ax.set_title("Single stage vs. three-stage cascade")
ax.set_xlabel("Frequency (Hz)")
ax.set_ylabel("Gain (dB)")
ax.set_ylim(-120, 5)
ax.grid(True, which="both", alpha=0.3)
ax.legend()
fig.tight_layout()
display(fig, append=True)

note(
    "Notice the cascade rolls off three times faster (about 60 dB "
    "per decade) past the cutoff. With a Ngspice shared library "
    "available, you'd hand <code>cascade</code> to a simulator and "
    "get the actual simulated response -- the same Python object "
    "you built here drives the analysis."
)
