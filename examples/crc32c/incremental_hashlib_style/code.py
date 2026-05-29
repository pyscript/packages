# ---------------------------------------------------------------------
# CRC32CHash: a hashlib-compatible interface
# ---------------------------------------------------------------------

heading("CRC32CHash: a familiar hashlib-style interface")
note(
    "If you've used <code>hashlib.sha256()</code>, "
    "<code>crc32c.CRC32CHash</code> will feel right at home: "
    "create an object, <code>update()</code> it with chunks, then "
    "ask for the <code>digest()</code>, <code>hexdigest()</code>, "
    "or the integer <code>checksum</code>."
)

# Imagine streaming a log file in 64-byte slices.
log_lines = [
    b"2026-04-01 09:00:00 INFO  service started\n",
    b"2026-04-01 09:00:12 INFO  user alice signed in\n",
    b"2026-04-01 09:01:45 WARN  retrying upstream call\n",
    b"2026-04-01 09:01:47 INFO  upstream call succeeded\n",
    b"2026-04-01 09:05:30 INFO  user alice signed out\n",
]
full_log = b"".join(log_lines)

hasher = crc32c.CRC32CHash()
chunk_size = 32
for offset in range(0, len(full_log), chunk_size):
    hasher.update(full_log[offset:offset + chunk_size])

note(
    f"Bytes processed: <strong>{len(full_log)}</strong> in "
    f"{(len(full_log) + chunk_size - 1) // chunk_size} chunks."
)

display(HTML(
    "<pre>"
    f"hexdigest():       {hasher.hexdigest()}\n"
    f"digest() (bytes):  {hasher.digest()!r}\n"
    f"checksum (int):    {hasher.checksum}\n"
    f"name:              {hasher.name}\n"
    f"digest_size:       {hasher.digest_size} bytes"
    "</pre>"
), append=True)

# ---------------------------------------------------------------------
# Verifying integrity of a stored payload
# ---------------------------------------------------------------------

heading("Verifying a payload against a stored checksum")
note(
    "A common pattern: store the checksum alongside the data, then "
    "recompute it on read to confirm nothing was corrupted."
)

def make_record(payload: bytes) -> dict:
    """Bundle a payload with its CRC32C checksum."""
    return {"payload": payload, "crc32c": crc32c.crc32c(payload)}


def verify(record: dict) -> bool:
    """Return True if the record's payload still matches its checksum."""
    return crc32c.crc32c(record["payload"]) == record["crc32c"]


good = make_record(b"the quick brown fox jumps over the lazy dog")

# Simulate corruption in transit: flip a byte.
tampered = {
    "payload": good["payload"].replace(b"fox", b"cat"),
    "crc32c": good["crc32c"],
}

display(HTML(
    "<pre>"
    f"good record verified:     {verify(good)}\n"
    f"tampered record verified: {verify(tampered)}"
    "</pre>"
), append=True)

note(
    "CRC32C is excellent at catching accidental corruption but is "
    "<em>not</em> a cryptographic hash. For tamper resistance, reach "
    "for <code>hashlib.sha256</code> or an HMAC instead."
)
