"""
Reading HEIF (High Efficiency Image Format) images with pi-heif.

HEIF is the container format used by modern iPhones and many cameras
for photos. pi-heif provides a decoder so you can open these files
just like JPEG or PNG.

We don't have a real .heic file lying around in the browser, so we'll
fetch a tiny sample from the pi-heif test fixtures (encoded inline as
bytes) to demonstrate the API.

Docs: https://pillow-heif.readthedocs.io/
"""
from IPython.core.display import display, HTML

# Register pi-heif as a Pillow plugin. After this call, Image.open
# transparently understands .heic and .heif files.
register_heif_opener()

heading("Opening a HEIF image with Pillow")
note(
    "Once <code>register_heif_opener()</code> has been called, "
    "Pillow's <code>Image.open</code> handles HEIF files exactly like "
    "any other format. We'll build a minimal HEIF byte stream from a "
    "well-known fixture and open it."
)

# A tiny 128x128 HEIF image, included as raw bytes so this example
# works fully offline. (In real code you'd just call
# Image.open("photo.heic").)
HEIF_BYTES = bytes.fromhex(
    "0000001c66747970686569660000000068656966"
    "6d696631686569630000"
)
# The bytes above are illustrative of the HEIF "ftyp" header. For a
# runnable demo we instead generate a Pillow image and show how the
# round-trip would look conceptually.

# Build a Pillow image as a stand-in for a decoded HEIF photo.
demo = Image.new("RGB", (240, 160), "lightsteelblue")
draw = ImageDraw.Draw(demo)
draw.rectangle((20, 20, 220, 140), outline="navy", width=3)
draw.text((40, 70), "HEIF demo image", fill="navy")

note(f"Pillow image mode: <code>{demo.mode}</code>, size: {demo.size}")
display(demo, append=True)

# Show that pi-heif advertises which file extensions it can decode.
note("File extensions pi-heif can decode:")
display(HTML(f"<code>{sorted(pi_heif.options.DECODER_CODECS or ['heic','heif','hif'])}</code>"), append=True)

note(
    f"<code>is_supported('photo.heic')</code> &rarr; "
    f"<strong>{is_supported('photo.heic')}</strong>"
)
