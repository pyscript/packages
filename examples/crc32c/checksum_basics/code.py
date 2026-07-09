"""
A first look at the crc32c package.

CRC32C (Castagnoli) is a 32-bit checksum used by ZFS, Btrfs, iSCSI,
Google Cloud Storage, and many network protocols. It's fast and
great for detecting accidental corruption in data at rest or in
transit. See https://github.com/ICRAR/crc32c for the project.
"""
from IPython.core.display import display, HTML

import crc32c


heading("1. Computing a CRC32C checksum")
note(
    "The core function takes bytes and returns a 32-bit unsigned "
    "integer checksum. It's commonly shown in hexadecimal."
)

message = b"hello world"
checksum = crc32c.crc32c(message)

note(
    f"Message: <code>{message!r}</code><br>"
    f"Checksum (decimal): <code>{checksum}</code><br>"
    f"Checksum (hex): <code>0x{checksum:08x}</code>"
)

heading("2. Streaming: chain calls with the previous value")
note(
    "If your data arrives in chunks, pass the previous checksum as "
    "<code>value</code> to continue from where you left off. The "
    "result matches a single call over the concatenated bytes."
)

chunks = [b"hello", b" ", b"world"]
running = 0
for chunk in chunks:
    running = crc32c.crc32c(chunk, value=running)

one_shot = crc32c.crc32c(b"".join(chunks))

note(
    f"Chunked result:  <code>0x{running:08x}</code><br>"
    f"One-shot result: <code>0x{one_shot:08x}</code><br>"
    f"Match: <strong>{running == one_shot}</strong>"
)

heading("3. Detecting a single-bit flip")
note(
    "Even tiny changes produce a wildly different checksum. Here we "
    "flip one bit of a 256-byte payload and compare."
)

original = bytes(range(256))
corrupted = bytearray(original)
corrupted[42] ^= 0b00000001  # flip the lowest bit of one byte

display(HTML(
    "<pre>"
    f"original  CRC32C: 0x{crc32c.crc32c(original):08x}\n"
    f"corrupted CRC32C: 0x{crc32c.crc32c(bytes(corrupted)):08x}"
    "</pre>"
), append=True)

note(
    f"Hardware-accelerated on this platform: "
    f"<strong>{crc32c.hardware_based}</strong>"
)
