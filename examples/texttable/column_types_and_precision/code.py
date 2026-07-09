# ---------------------------------------------------------------------
# Column data types and number formatting.
# ---------------------------------------------------------------------

heading("Telescope readings: choosing how each column is formatted")
note(
    "set_cols_dtype lets you tell each column how to format its "
    "values: 't' text, 'i' int, 'f' decimal float, 'e' exponential, "
    "'a' automatic, 'b' boolean. set_precision controls the number "
    "of digits shown for floats."
)

readings = Texttable()
# Drop everything except a horizontal line under the header for a
# clean, report-style look.
readings.set_deco(Texttable.HEADER)
readings.set_cols_dtype(["t", "f", "e", "i", "b"])
readings.set_cols_align(["l", "r", "r", "r", "c"])
readings.set_precision(4)
readings.add_rows([
    ["target",   "magnitude", "flux (W/m^2)",      "exposure_s", "usable"],
    ["Vega",     0.03,        2.5e-8,              30,           True],
    ["Sirius",  -1.46,        1.18e-7,             15,           True],
    ["Betelgeuse", 0.42,      9.4e-9,              45,           False],
    ["Proxima Centauri", 11.13, 1.2e-12,           600,          True],
])

show_table(readings)

note(
    "Notice how 'magnitude' is rendered as a fixed-point decimal "
    "with four digits of precision, while 'flux' uses the same "
    "precision in exponential notation."
)
