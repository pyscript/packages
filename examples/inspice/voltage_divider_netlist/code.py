# ---------------------------------------------------------------------
# Building a resistor ladder and computing node voltages by hand.
# ---------------------------------------------------------------------

heading("2. A four-resistor voltage divider")
note(
    "InSpice circuits compose nicely with ordinary Python: we can "
    "use a loop to chain resistors between numbered nodes. Here we "
    "build a ladder of four 1 kΩ resistors driven by a 12 V supply, "
    "then read the netlist back to confirm the topology."
)

ladder = Circuit("Four-resistor voltage divider")
ladder.V("supply", "n0", ladder.gnd, 12 @ u_V)

# Chain resistors n0 -> n1 -> n2 -> n3 -> ground.
nodes = ["n0", "n1", "n2", "n3", ladder.gnd]
for index in range(4):
    ladder.R(index + 1, nodes[index], nodes[index + 1], 1 @ u_kOhm)

note("Generated SPICE netlist:")
display(HTML(f"<pre>{ladder}</pre>"), append=True)

# Walk the components by iterating over the circuit's elements.
note("Iterating over circuit elements:")
rows = ["<table><tr><th>Name</th><th>Nodes</th><th>Value</th></tr>"]
for element in ladder.elements:
    pins = ", ".join(str(pin) for pin in element.nodes)
    value = getattr(element, "resistance",
                    getattr(element, "dc_value", ""))
    rows.append(
        f"<tr><td>{element.name}</td>"
        f"<td>{pins}</td>"
        f"<td>{value}</td></tr>"
    )
rows.append("</table>")
display(HTML("".join(rows)), append=True)

# For a chain of equal resistors the voltage at each tap is just a
# linear interpolation between the supply and ground.
supply_voltage = 12.0
n_resistors = 4
tap_voltages = [
    supply_voltage * (n_resistors - i) / n_resistors
    for i in range(n_resistors + 1)
]

note(
    "With four equal resistors, each one drops a quarter of the "
    "supply, giving the following expected node voltages:"
)
fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(range(len(tap_voltages)), tap_voltages,
        marker="o", color="crimson", linewidth=2)
for i, v in enumerate(tap_voltages):
    ax.annotate(f"{v:.2f} V", (i, v),
                textcoords="offset points", xytext=(8, 6))
ax.set_xticks(range(len(tap_voltages)))
ax.set_xticklabels([f"n{i}" if i < 4 else "GND"
                    for i in range(len(tap_voltages))])
ax.set_ylabel("Voltage (V)")
ax.set_title("Voltage at each tap of the divider")
ax.grid(True, alpha=0.3)
fig.tight_layout()
display(fig, append=True)
