# ---------------------------------------------------------------------
# Two pi-heif features that are easy to miss:
#   1. `convert_hdr_to_8bit=False` keeps 10/12-bit HDR data intact, so
#      you can hand off 16-bit arrays to libraries like OpenCV.
#   2. `bgr_mode=True` returns BGR-ordered channels, which is what
#      OpenCV expects natively.
# We'll demonstrate the option flags and visualise the difference
# between an 8-bit and a simulated 16-bit decode.
# ---------------------------------------------------------------------

heading("HDR decoding options")
note(
    "Calling <code>open_heif</code> with "
    "<code>convert_hdr_to_8bit=False</code> preserves the original "
    "bit depth (10 or 12 bits) as a uint16 array. Combined with "
    "<code>bgr_mode=True</code>, this is the recommended path for "
    "feeding HEIF directly into OpenCV's <code>cv2.imwrite</code>."
)

# A code snippet readers can adapt verbatim.
example_call = """heif_file = pi_heif.open_heif(
    "image.heic",
    convert_hdr_to_8bit=False,  # keep 10/12-bit HDR data
    bgr_mode=True,              # OpenCV-friendly channel order
)
np_array = np.asarray(heif_file)  # uint16 if HDR, uint8 otherwise
print(heif_file.mode, heif_file.bit_depth, np_array.dtype)"""
display(HTML(f"<pre><code>{example_call}</code></pre>"), append=True)

# Simulate the visual difference between an 8-bit decode (clipped
# highlights) and a 16-bit HDR decode (full dynamic range).
height, width = 160, 320
xx = np.linspace(0, 1, width)[None, :].repeat(height, axis=0)

# Underlying scene with values that exceed the 8-bit range.
hdr_scene = (xx ** 0.5) * 65535  # smooth gradient up to 16-bit max

eight_bit = np.clip(hdr_scene / 256, 0, 255).astype(np.uint8)
sixteen_bit = hdr_scene.astype(np.uint16)

# Tone-map the 16-bit version for display, the way an HDR pipeline
# would: a simple gamma curve preserves shadow detail.
tone_mapped = (
    (sixteen_bit / 65535) ** (1 / 2.2) * 255
).astype(np.uint8)

fig, axes = plt.subplots(1, 2, figsize=(10, 3))
axes[0].imshow(np.dstack([eight_bit] * 3))
axes[0].set_title("8-bit decode (convert_hdr_to_8bit=True)")
axes[0].axis("off")

axes[1].imshow(np.dstack([tone_mapped] * 3))
axes[1].set_title("16-bit HDR decode, tone-mapped")
axes[1].axis("off")
fig.tight_layout()
display(fig, append=True)

heading("Thumbnails embedded in HEIF files")
note(
    "Many HEIF files carry one or more pre-baked thumbnails. "
    "pi-heif exposes them via <code>heif_file.thumbnails</code> "
    "(list of sizes) and <code>heif_file.get_thumbnail(size)</code>. "
    "This is much faster than decoding the full image when you only "
    "need a preview."
)

thumbnail_snippet = """heif_file = pi_heif.open_heif("photo.heic")
for size in heif_file.thumbnails:
    thumb = heif_file.get_thumbnail(size)
    Image.frombytes(thumb.mode, thumb.size, thumb.data).save(
        f"thumb_{size}.png"
    )"""
display(HTML(f"<pre><code>{thumbnail_snippet}</code></pre>"), append=True)

note(
    "From here, common next steps are: applying Pillow filters to the "
    "decoded image, saving as PNG/JPEG via Pillow, or piping the "
    "NumPy array into OpenCV or scikit-image. See "
    "<a href='https://pillow-heif.readthedocs.io/'>"
    "pillow-heif.readthedocs.io</a> for the full reference."
)
