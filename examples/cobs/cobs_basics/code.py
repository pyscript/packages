"""
Consistent Overhead Byte Stuffing (COBS) basics.

COBS lets you safely transmit arbitrary bytes -- including 0x00 --
over a stream where 0x00 is reserved as a packet delimiter. After
encoding, the payload is guaranteed to contain no zero bytes, so a
single 0x00 between packets unambiguously marks the boundary.

This first example shows the round-trip: encode a message, observe
the absence of zero bytes, then decode it.
"""
from IPython.core.display import display, HTML

# A message that contains zero bytes in the middle. Without byte
# stuffing, a receiver scanning for 0x00 delimiters would chop this
# packet in half.
message = b"sensor\x00reading\x00=42"

heading("1. Encoding a message with embedded zero bytes")
note("Original payload (note the two 0x00 bytes inside the data):")
hex_view(message, label="message")

encoded = cobs.encode(message)
note(
    "After cobs.encode(...), the result contains no 0x00 bytes, "
    "so 0x00 is now safe to use as a frame delimiter on the wire."
)
hex_view(encoded, label="encoded")

note(f"Has any zero byte? <strong>{0 in encoded}</strong>. "
     f"Overhead: <strong>{len(encoded) - len(message)}</strong> byte(s).")

heading("2. Decoding restores the original bytes exactly")
decoded = cobs.decode(encoded)
hex_view(decoded, label="decoded")
note(f"Round-trip equal to original? <strong>{decoded == message}</strong>")

heading("3. Encoding works on any buffer-like input")
note(
    "encode() accepts bytes, bytearray, memoryview -- anything "
    "that implements the buffer protocol -- and always returns bytes."
)
buffer = bytearray(b"\x01\x02\x00\x03\x00\x00\x04")
hex_view(bytes(buffer), label="input bytearray")
hex_view(cobs.encode(buffer), label="encoded")
