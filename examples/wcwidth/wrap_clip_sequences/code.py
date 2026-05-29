# Working with text that contains terminal escape sequences.
#
# Real terminal output is often littered with ANSI color codes ("SGR"),
# hyperlinks, and cursor movement. wcwidth knows how to measure, wrap,
# clip, and strip these sequences without breaking them.

heading("Measuring text that contains ANSI color codes")
note(
    "<code>wcwidth.width()</code> understands escape sequences and "
    "reports only the cells that will actually be drawn."
)

colored = "\x1b[1;31mERROR\x1b[0m: disk full"
note(f"Raw repr: <code>{repr(colored)}</code>")
note(f"len() says <strong>{len(colored)}</strong> codepoints.")
note(f"wcswidth() says <strong>{wcwidth.wcswidth(colored)}</strong> (-1 means it gave up on control codes).")
note(f"width() says <strong>{wcwidth.width(colored)}</strong> visible cells.")

heading("Stripping escape sequences")
note(
    "<code>strip_sequences()</code> removes all terminal escapes, "
    "leaving plain text."
)
plain = wcwidth.strip_sequences(colored)
note(f"Stripped: <code>{repr(plain)}</code>")

heading("Wrapping text to a column width")
note(
    "<code>wrap()</code> respects grapheme clusters and wide characters, "
    "and propagates SGR styles across line breaks so colors don't leak."
)

paragraph = (
    "\x1b[36mThe quick brown fox jumps over the lazy dog.\x1b[0m "
    "コンニチハ、世界。 cafe\u0301 latte."
)
for line in wcwidth.wrap(paragraph, 20):
    note(f"<code>{repr(line)}</code>")

heading("Clipping by display column")
note(
    "<code>clip(text, start, end)</code> extracts a substring by visible "
    "column positions, splitting wide characters cleanly with a fill."
)

cjk = "中文字幕"  # 4 wide chars = 8 cells
note(f"Original: <code>{cjk}</code> ({wcwidth.wcswidth(cjk)} cells)")
note(f"clip(0, 3): <code>{wcwidth.clip(cjk, 0, 3)}</code> (wide char split, padded with space)")
note(f"clip(1, 5, fillchar='.'): <code>{wcwidth.clip(cjk, 1, 5, fillchar='.')}</code>")

heading("Iterating over grapheme clusters")
note(
    "A user-perceived character ('grapheme') may span several codepoints. "
    "<code>iter_graphemes()</code> yields one cluster at a time."
)

family = "ok\U0001F468\u200D\U0001F469\u200D\U0001F467"  # 'ok' + 👨‍👩‍👧
clusters = list(wcwidth.iter_graphemes(family))
note(f"Input has {len(family)} codepoints but only {len(clusters)} graphemes:")
for g in clusters:
    note(f"&nbsp;&nbsp;<code>{repr(g)}</code> width={wcwidth.wcswidth(g)}")
