"""
Reading HEIF (High Efficiency Image Format) images with pi-heif.

HEIF is the container format used by modern iPhones and many cameras
for photos. pi-heif provides a decoder so you can open these files
just like JPEG or PNG.

We don't have a real .heic file lying around in the browser, so we'll
build a plain Pillow image as a stand-in and walk through the API
you'd use on a real photo.

Docs: https://pillow-heif.readthedocs.io/
"""
from IPython.core.display import display, HTML
# Example-specific imports below.
import io
from PIL import Image, ImageDraw
import pi_heif
from pi_heif import register_heif_opener


# Register pi-heif as a Pillow plugin. After this call, Image.open
# transparently understands .heic and .heif files.
register_heif_opener()

heading("Opening a HEIF image with Pillow")
note(
    "Once <code>register_heif_opener()</code> has been called, "
    "Pillow's <code>Image.open</code> handles HEIF files exactly like "
    "any other format. On a real photo you'd simply write "
    "<code>Image.open('photo.heic')</code>; here we build a Pillow "
    "image directly as a stand-in for the decoded result."
)

# Stand-in for a decoded HEIF photo. In real code this would be the
# return value of Image.open("photo.heic").
demo = Image.new("RGB", (240, 160), "lightsteelblue")
draw = ImageDraw.Draw(demo)
draw.rectangle((20, 20, 220, 140), outline="navy", width=3)
draw.text((40, 70), "HEIF demo image", fill="navy")

note(f"Pillow image mode: <code>{demo.mode}</code>, size: {demo.size}")
display(demo, append=True)

# Ask Pillow which extensions now map to the HEIF/HEIC formats. This
# is the most reliable way to answer "will Pillow open my file?",
# because it reflects what register_heif_opener() actually wired up.
# (Avoid reaching into pi_heif.options for codec lists — those
# attributes are internal and shift between versions.)
heif_exts = sorted(
    ext for ext, fmt in Image.registered_extensions().items()
    if fmt in ("HEIF", "HEIC")
)
note(f"File extensions Pillow now routes to pi-heif: <code>{heif_exts}</code>")