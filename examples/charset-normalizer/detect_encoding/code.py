"""
Detecting the encoding of mystery bytes.

charset-normalizer takes a byte sequence whose encoding is unknown
and figures out the most plausible way to decode it into readable
text. We do not try to recover the *original* encoding (often there
is no single right answer); we want clean, readable Unicode out.

Project docs: https://charset-normalizer.readthedocs.io/
"""
from IPython.core.display import display, HTML

# Package imports for the example.
from charset_normalizer import from_bytes


# Imagine these bytes arrived from an old subtitle file, an email
# attachment, or a scraped web page, and nobody told us how they
# were encoded. Each line below is the same French sentence, encoded
# differently.
mystery_samples = {
    "subtitle.srt (windows)": (
        "Bonjour, je suis à la recherche d'une aide sur les étoiles."
    ).encode("cp1252"),
    "notes.txt (mac roman)": (
        "Café résumé naïveté façade jalapeño"
    ).encode("mac_roman"),
    "weibo.txt (chinese)": (
        "你好世界，今天天气很好。"
    ).encode("gb2312"),
    "novel.txt (russian)": (
        "Здравствуй, мир! Сегодня хорошая погода."
    ).encode("koi8_r"),
}

heading("Best-guess decoding for each mystery file")
note(
    "<code>from_bytes(...)</code> returns a ranked list of candidates. "
    "<code>.best()</code> gives the most likely match, which behaves "
    "like a string and exposes details about how it was decoded."
)

for filename, raw_bytes in mystery_samples.items():
    results = from_bytes(raw_bytes)
    best = results.best()

    heading(filename, level=3)
    note(
        f"Detected encoding: <strong>{best.encoding}</strong> &mdash; "
        f"language: <strong>{best.language}</strong> &mdash; "
        f"chaos: {best.chaos:.3f}, coherence: {best.coherence:.3f}"
    )
    # A CharsetMatch decodes lazily; str(best) gives the Unicode text.
    note(f"Decoded text: <em>{str(best)}</em>")
