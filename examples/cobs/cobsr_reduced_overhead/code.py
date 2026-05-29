# ---------------------------------------------------------------------
# COBS/R: a small variant that often saves the +1 overhead byte.
# ---------------------------------------------------------------------
#
# Plain COBS always adds at least 1 byte. COBS/R ("Reduced") notices
# when the final data byte is large enough to stand in for the
# trailing length code, and elides the extra byte. For short messages
# made of mostly non-zero bytes -- typical of small telemetry frames
# -- this is a meaningful saving.

heading("Comparing COBS and COBS/R on the same input")

# Last byte (0x26) is larger than the trailing length code (0x04) that
# plain COBS would emit, so COBS/R can drop the length byte entirely.
sample = bytes([0x2F, 0xA2, 0x00, 0x92, 0x73, 0x26])

hex_view(sample, label="input")
hex_view(cobs.encode(sample), label="cobs.encode")
hex_view(cobsr.encode(sample), label="cobsr.encode")

note(
    "Both encodings round-trip losslessly; COBS/R just happens to be "
    "one byte shorter for inputs whose last byte exceeds the final "
    "length code."
)
assert cobs.decode(cobs.encode(sample)) == sample
assert cobsr.decode(cobsr.encode(sample)) == sample

heading("How often does COBS/R actually save a byte?")
note(
    "We'll encode a batch of short, mostly-non-zero messages with "
    "both encoders and tally the size difference."
)

messages = [
    b"OK",
    b"PING",
    b"id=7",
    b"v=3.14",
    b"hello!",
    b"\x10\x20\x30",
    b"temp=22C",
    b"go\x00stop",
    b"x" * 20,
    b"\xff\xfe\xfd\xfc",
]

cobs_total = sum(len(cobs.encode(m)) for m in messages)
cobsr_total = sum(len(cobsr.encode(m)) for m in messages)
raw_total = sum(len(m) for m in messages)

note(
    f"Raw payload total: <strong>{raw_total}</strong> bytes<br>"
    f"COBS encoded total: <strong>{cobs_total}</strong> bytes "
    f"(+{cobs_total - raw_total})<br>"
    f"COBS/R encoded total: <strong>{cobsr_total}</strong> bytes "
    f"(+{cobsr_total - raw_total})"
)

# Per-message breakdown so the saving is easy to see.
rows = ["<table style='border-collapse:collapse'>"
        "<tr><th>message</th><th>raw</th><th>cobs</th>"
        "<th>cobsr</th><th>saved</th></tr>"]
for message in messages:
    raw_len = len(message)
    c_len = len(cobs.encode(message))
    r_len = len(cobsr.encode(message))
    rows.append(
        f"<tr><td><code>{message!r}</code></td>"
        f"<td>{raw_len}</td><td>{c_len}</td>"
        f"<td>{r_len}</td><td>{c_len - r_len}</td></tr>"
    )
rows.append("</table>")
display(HTML("".join(rows)), append=True)
