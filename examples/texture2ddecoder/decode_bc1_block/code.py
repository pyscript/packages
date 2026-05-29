"""
A first look at texture2ddecoder.

GPU textures are usually stored on disk in compressed block formats
(BC1/DXT1, BC3/DXT5, ETC, ASTC, PVRTC, ...) so they can be uploaded
straight to the GPU. This package decodes those blocks back to plain
BGRA pixels so we can inspect or convert them with Pillow.

In this first example we hand-build a single 8-byte BC1 block, decode
it into a 4x4 BGRA image, and look at the resulting pixels.

Docs: https://github.com/K0lb3/texture2ddecoder
"""
from IPython.core.display import display, HTML

# A BC1 (a.k.a. DXT1) block is exactly 8 bytes and encodes a 4x4 tile:
#   - 2 bytes: color0 (RGB565)
#   - 2 bytes: color1 (RGB565)
#   - 4 bytes: 16 two-bit indices selecting one of four palette colors.
#
# We pick color0 = pure red and color1 = pure blue in RGB565, then make
# every pixel use index 0 (color0). The result should be a 4x4 red tile.
color0 = (0b11111 << 11) | (0b000000 << 5) | 0b00000  # red
color1 = (0b00000 << 11) | (0b000000 << 5) | 0b11111  # blue
indices = 0x00000000  # all 16 pixels point at color0

bc1_block = (
    color0.to_bytes(2, "little")
    + color1.to_bytes(2, "little")
    + indices.to_bytes(4, "little")
)

heading("A single 4x4 BC1 block")
note(
    f"Encoded block size: <strong>{len(bc1_block)} bytes</strong>. "
    "BC1 always packs a 4x4 tile into 8 bytes."
)

# Decode into raw BGRA bytes (4 bytes per pixel, BGRA order).
width, height = 4, 4
decoded = texture2ddecoder.decode_bc1(bc1_block, width, height)
note(
    f"Decoded buffer length: <strong>{len(decoded)} bytes</strong> "
    f"(= {width} x {height} x 4 BGRA channels)."
)

# Pillow speaks RGBA, so we ask it to interpret the raw bytes as BGRA.
tile = Image.frombytes("RGBA", (width, height), decoded, "raw", "BGRA")

# Sample a couple of pixels to confirm the decode.
note(f"Top-left pixel (R, G, B, A): <code>{tile.getpixel((0, 0))}</code>")
note(f"Bottom-right pixel: <code>{tile.getpixel((3, 3))}</code>")

# Show the tile, scaled up so 4x4 is actually visible.
preview = tile.resize((128, 128), Image.NEAREST)
buffer = io.BytesIO()
preview.save(buffer, format="PNG")
data_url = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()
display(HTML(f'<img src="{data_url}" alt="decoded BC1 tile">'), append=True)
