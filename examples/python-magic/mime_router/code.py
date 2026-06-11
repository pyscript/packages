# ---------------------------------------------------------------------
# Building a tiny content-aware upload router with python-magic.
# ---------------------------------------------------------------------
#
# A common real-world use of python-magic: an "upload handler" that
# decides what to do with a file based on its true type, regardless
# of what the user named it. This protects against mislabeled or
# disguised files (think: a script renamed to look like an image).

import magic


heading("A MIME-based upload router")
note(
    "Each incoming upload is a tuple of (claimed filename, bytes). "
    "We detect the real MIME type and dispatch to the appropriate "
    "handler. A mismatch between the filename's extension and the "
    "detected type is flagged as suspicious."
)

# Pretend these came in over the wire from a web form.
incoming_uploads = [
    ("vacation.jpg", b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01"
                     b"\x00\x01\x00\x00" + b"\x00" * 200),
    ("budget.pdf", b"%PDF-1.5\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<<>>\nendobj\n"
                   + b"\x00" * 100),
    ("backup.zip", b"PK\x03\x04\x14\x00\x00\x00\x08\x00" + b"\x00" * 200),
    # Sneaky: claims to be a PNG but is actually plain text.
    ("avatar.png", b"#!/bin/sh\necho 'definitely not an image'\n" * 20),
    ("readme.txt", b"Welcome to the project!\n\nThis is a friendly readme.\n" * 10),
]


# Map MIME prefixes to handler descriptions. In a real app these would
# be functions; here we just describe what would happen.
def route(mime_type):
    """Return a (handler_name, action) pair for a detected MIME type."""
    if mime_type.startswith("image/"):
        return ("ImageProcessor", "resize and store in /uploads/images")
    if mime_type == "application/pdf":
        return ("DocumentIndexer", "extract text and add to search index")
    if mime_type.startswith("text/"):
        return ("TextStore", "save to /uploads/text")
    if mime_type in {"application/zip", "application/x-zip-compressed"}:
        return ("ArchiveScanner", "scan contents before unpacking")
    return ("QuarantineBin", "unknown type, hold for review")


# Map common extensions to expected MIME prefixes for sanity-checking.
expected_prefix = {
    ".jpg": "image/", ".jpeg": "image/", ".png": "image/",
    ".pdf": "application/pdf",
    ".zip": "application/zip",
    ".txt": "text/",
}

rows = [
    "<tr><th>Filename</th><th>Detected MIME</th>"
    "<th>Handler</th><th>Status</th></tr>"
]
for filename, data in incoming_uploads:
    mime_type = magic.from_buffer(data, mime=True)
    handler, action = route(mime_type)

    # Cross-check the extension against the detected type.
    extension = "." + filename.rsplit(".", 1)[-1].lower()
    expected = expected_prefix.get(extension, "")
    if expected and not mime_type.startswith(expected):
        status = "⚠️ extension/content mismatch"
    else:
        status = "✓ ok"

    rows.append(
        f"<tr><td><code>{filename}</code></td>"
        f"<td><code>{mime_type}</code></td>"
        f"<td>{handler} &mdash; <em>{action}</em></td>"
        f"<td>{status}</td></tr>"
    )

display(HTML("<table>" + "".join(rows) + "</table>"), append=True)

note(
    "Notice how <code>avatar.png</code> is correctly identified as a "
    "shell script (<code>text/x-shellscript</code> or similar) and "
    "flagged. This is exactly the kind of check a libmagic-based router "
    "buys you for free."
)
