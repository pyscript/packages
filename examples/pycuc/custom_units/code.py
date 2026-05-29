# ---------------------------------------------------------------------
# Defining your own units with add_custom_unit()
# ---------------------------------------------------------------------

heading("Teaching PyCUC a new unit")
note(
    "Suppose your team measures heat capacity in J/mol.K and kJ/mol.K, "
    "and you'd like PyCUC to handle that family. add_custom_unit(name, "
    "factor) registers each unit relative to a chosen reference value "
    "of 1."
)

# Start from a measured heat capacity in J/(mol.K).
heat_capacity = pycuc.create_cuc(75.3, "J/mol.K")

# Register the family. The factor is "how many of the reference unit
# (J/mol.K, factor 1) make up one of this unit". So 1 kJ/mol.K is
# 1000 J/mol.K.
heat_capacity.add_custom_unit("J/mol.K", 1)
heat_capacity.add_custom_unit("kJ/mol.K", 1000)
heat_capacity.add_custom_unit("cal/mol.K", 4.184)

note("The same value, expressed across our newly defined units:")
for unit in ["J/mol.K", "kJ/mol.K", "cal/mol.K"]:
    note(f"&nbsp;&nbsp;<strong>{heat_capacity.convert(unit):.4f}</strong> {unit}")

heading("Inspecting the custom registry")
note(
    "check_reference('custom') returns the units you have added on "
    "this converter object, alongside their conversion factors."
)
display(heat_capacity.check_reference("custom"), append=True)

heading("Mixing built-in and custom units")
note(
    "Built-in references stay available on the same object. Here we "
    "ask the same converter about pressure units, which PyCUC ships "
    "with out of the box."
)
display(heat_capacity.check_reference("pressure"), append=True)
