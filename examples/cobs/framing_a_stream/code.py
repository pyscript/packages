# ---------------------------------------------------------------------
# Putting COBS to work: a tiny packet framer.
# ---------------------------------------------------------------------
#
# COBS itself does not add framing -- encode() returns the stuffed
# payload only. The classic pattern is to append a 0x00 byte after
# each encoded packet so the receiver can split a continuous stream
# on zero bytes and decode each chunk independently.

heading("Framing several packets into one stream")

packets = [
    b"TEMP=21.4",
    b"\x00\x00\x00",          # all-zero payload, awkward without COBS
    b"GPS:lat=51.5,lon=-0.1",
    b"",                       # empty payload is fine too
    b"STATUS\x00OK",
]

# Encode each packet and join with 0x00 framing bytes.
stream = b"\x00".join(cobs.encode(p) for p in packets) + b"\x00"

note(f"Sending <strong>{len(packets)}</strong> packets as a single "
     f"<strong>{len(stream)}</strong>-byte stream:")
hex_view(stream, label="wire stream")

heading("Receiver: split on 0x00, decode each chunk")

# Split on the delimiter. The trailing 0x00 produces an empty final
# chunk we discard; an empty chunk in the middle would mean an empty
# packet, which we also skip here.
chunks = stream.split(b"\x00")
recovered = [cobs.decode(c) for c in chunks if c]

note("Recovered packets:")
for index, payload in enumerate(recovered):
    hex_view(payload, label=f"packet {index}")

note(f"All packets recovered correctly? "
     f"<strong>{recovered == [p for p in packets if p]}</strong>")

# Note: empty packets round-trip through encode/decode fine, but our
# simple split-and-filter receiver above drops them. Real framers
# usually treat consecutive 0x00s as either keep-alives or empty
# frames, depending on the protocol.
