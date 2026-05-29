# ---------------------------------------------------------------------
# Controlling layout: column widths, decoration flags, and characters.
# ---------------------------------------------------------------------

heading("Release notes: wrapping long text into fixed-width columns")
note(
    "set_cols_width forces each column to a fixed width and wraps "
    "text inside it. set_deco picks which lines to draw, and "
    "set_chars swaps the characters used for those lines."
)

notes_table = Texttable()
notes_table.set_cols_align(["c", "l", "l"])
notes_table.set_cols_valign(["m", "t", "t"])
notes_table.set_cols_width([8, 22, 34])
notes_table.header(["Version", "Highlight", "Details"])
notes_table.add_rows([
    ["1.4.0",
     "Async cache",
     "Caches now support awaitable producers and propagate "
     "cancellation cleanly."],
    ["1.5.0",
     "Schema migrations",
     "A new migrate() helper walks pending migrations forward "
     "and writes a checkpoint on success."],
    ["1.6.0",
     "Pluggable transports",
     "Swap the default HTTP transport for any callable that "
     "accepts a Request and returns a Response."],
], header=False)

show_table(notes_table)

heading("Same data, lighter decoration")
note(
    "Combine the BORDER, HEADER, HLINES, and VLINES flags with | "
    "to pick exactly which lines you want. Here we keep just the "
    "outer border and the header rule, and use Unicode box "
    "characters via set_chars."
)

notes_table.set_deco(Texttable.BORDER | Texttable.HEADER)
# [horizontal, vertical, corner, header]
notes_table.set_chars(["\u2500", "\u2502", "\u253c", "\u2550"])
show_table(notes_table)

note(
    "Tip: passing max_width=0 to Texttable() disables wrapping "
    "entirely, which is useful when you'd rather have wide rows "
    "than wrapped cells."
)
