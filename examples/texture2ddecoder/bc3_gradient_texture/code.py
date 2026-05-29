# ---------------------------------------------------------------------
# Example 2: Round-trip a real image through BC3 (DXT5).
# ---------------------------------------------------------------------
#
# texture2ddecoder is a *decoder*, but to demonstrate it on something
# more interesting than a hand-rolled block we encode a small gradient
# image to BC3 using Pillow's built-in DDS writer, then hand the raw
# BC3 byte stream to texture2ddecoder.decode_bc3 to get BGRA pixels
# back. This mirrors the real-world flow: read a .dds / asset bundle,
# pull out the compressed payload, decode it for inspection.

heading("Round-tripping a gradient through BC3")

width, height = 128, 128

# Build a colorful gradient with a circular alpha mask so BC3's
# separate alpha channel actually has work to do.
source = Image.new("RGBA", (width, height))
pixels = []
cx, cy = width / 2, height / 2
max_r = (cx ** 2 + cy ** 2) ** 0.5
for y in range(height):
    for x in range(width):
        r = int(255 * x / (width - 1))
        g = int(255 * y / (height - 1))
        b = int(255 * (1 - x / (width - 1)))
        dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
        a = max(0, min(255, int(255 * (1 - dist / max_r))))
        pixels.append((r, g, b, a))
source.putdata(pixels)

# Encode to DDS/BC3. Pillow writes a 128-byte DDS header, then the
# BC3 payload. BC3 uses 16 bytes per 4x4 block.
dds_buffer = io.BytesIO()
source.save(dds_buffer, format="DDS")
dds_bytes = dds_buffer.getvalue()

bc3_payload = dds_bytes[128:]  # strip the DDS header
expected_size = (width // 4) * (height // 4) * 16
note(
    f"DDS file size: <strong>{len(dds_bytes)}</strong> bytes. "
    f"BC3 payload: <strong>{len(bc3_payload)}</strong> bytes "
    f"(expected {expected_size})."
)

# Decode the BC3 payload back to BGRA.
decoded = texture2ddecoder.decode_bc3(bc3_payload, width, height)
recovered = Image.frombytes("RGBA", (width, height), decoded, "raw", "BGRA")

# Show original and decoded side by side.
def to_data_url(image):
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()

note("Left: original RGBA gradient. Right: after BC3 encode + decode.")
display(HTML(
    f'<div style="display:flex; gap:1em;">'
    f'<img src="{to_data_url(source)}" alt="original">'
    f'<img src="{to_data_url(recovered)}" alt="decoded">'
    f'</div>'
), append=True)

# Quantify the loss: BC3 is lossy, so pixels won't match exactly.
src_bytes = source.tobytes()
rec_bytes = recovered.tobytes()
total_diff = sum(abs(a - b) for a, b in zip(src_bytes, rec_bytes))
mean_diff = total_diff / len(src_bytes)
note(
    f"Mean absolute per-channel difference: "
    f"<strong>{mean_diff:.2f}</strong> / 255 "
    "-- small, as you'd expect from BC3."
)
