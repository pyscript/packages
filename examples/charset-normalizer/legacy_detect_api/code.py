# ---------------------------------------------------------------------
# The chardet-compatible detect() function, plus a binary check.
# ---------------------------------------------------------------------

heading("A chardet-compatible shortcut: detect()")
note(
    "If you already have code written for <code>chardet</code>, you "
    "can swap in <code>charset_normalizer.detect</code> with the same "
    "signature. It returns a small dict with the encoding, a "
    "confidence score, and the detected language."
)

samples = {
    "Greek (iso-8859-7)":
        "Καλημέρα κόσμε".encode("iso8859_7"),
    "Japanese (shift_jis)":
        "こんにちは世界、今日はいい天気ですね。".encode("shift_jis"),
    "UTF-8 with BOM":
        "\ufeffHello, world!".encode("utf_8_sig"),
}

for label, raw in samples.items():
    info = detect(raw)
    heading(label, level=3)
    note(
        f"<code>encoding</code>: <strong>{info['encoding']}</strong>, "
        f"<code>confidence</code>: {info['confidence']:.2f}, "
        f"<code>language</code>: {info.get('language') or '&mdash;'}"
    )
    # We can use the reported encoding to decode the bytes.
    note(f"Decoded: <em>{raw.decode(info['encoding'])}</em>")

# ---------------------------------------------------------------------
# Telling text from binary data.
# ---------------------------------------------------------------------

heading("Bonus: detecting binary payloads")
note(
    "<code>is_binary(...)</code> answers a different question: is "
    "this blob text at all? Useful before trying to decode something "
    "that may be an image, an archive, or random noise."
)

text_blob = "The quick brown fox jumps over the lazy dog.".encode("utf_8")
# A tiny synthetic 'binary' blob: a PNG-like header plus random-looking bytes.
binary_blob = bytes(
    [0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]
    + [(i * 37) % 256 for i in range(64)]
)

for label, blob in [("UTF-8 sentence", text_blob), ("PNG-like bytes", binary_blob)]:
    note(
        f"<strong>{label}</strong>: "
        f"is_binary = <code>{is_binary(blob)}</code>"
    )
