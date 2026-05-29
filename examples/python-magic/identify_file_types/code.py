"""
A first look at python-magic.

python-magic is a thin Python wrapper around libmagic, the same engine
behind the Unix `file` command. Given some bytes (or a file path), it
guesses the file type by inspecting the content's signature -- not the
filename or extension.

Docs: https://github.com/ahupp/python-magic
"""
from IPython.core.display import display, HTML

# A small "file cabinet" of byte signatures for common file types.
# Each entry is a realistic header we'd find at the start of a file.
file_samples = {
    "report.pdf": b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<< /Type /Catalog >>\nendobj\n",
    "logo.png": (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00"
    ),
    "photo.jpg": b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00",
    "archive.zip": b"PK\x03\x04\x14\x00\x00\x00\x08\x00" + b"\x00" * 20,
    "notes.txt": b"Dear diary,\nToday I learned about libmagic.\n",
    "song.mp3": b"ID3\x04\x00\x00\x00\x00\x00\x00" + b"\x00" * 64,
}

heading("Guessing file types from raw bytes")
note(
    "We pass the first chunk of each file's bytes to "
    "<code>magic.from_buffer</code> and let libmagic identify it. "
    "Notice that we never look at the filename -- the bytes alone are enough."
)

# Build an HTML table of filename, libmagic description, and MIME type.
rows = ["<tr><th>Filename</th><th>Description</th><th>MIME type</th></tr>"]
for name, data in file_samples.items():
    description = magic.from_buffer(data)
    mime_type = magic.from_buffer(data, mime=True)
    rows.append(
        f"<tr><td><code>{name}</code></td>"
        f"<td>{description}</td>"
        f"<td><code>{mime_type}</code></td></tr>"
    )

display(HTML("<table>" + "".join(rows) + "</table>"), append=True)

note(
    "The recommendation from the docs is to feed at least the first 2048 "
    "bytes for reliable identification. Shorter buffers can confuse the "
    "detection."
)
