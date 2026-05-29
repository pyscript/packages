# ---------------------------------------------------------------------
# pi-heif exposes the buffer protocol, so a decoded HEIF image can be
# turned directly into a NumPy array. This is the idiomatic way to feed
# HEIF photos into OpenCV, scikit-image, or any other array-based
# pipeline.
# ---------------------------------------------------------------------

heading("From HeifFile to NumPy array")
note(
    "<code>pi_heif.open_heif(...)</code> returns a <code>HeifFile</code> "
    "whose first image is exposed via the buffer protocol. Wrapping it "
    "in <code>np.asarray</code> gives you a (height, width, channels) "
    "array with no extra copy. We'll simulate this by creating an array "
    "directly and inspecting it as if it had come from HEIF decoding."
)

# Synthetic 200x300 RGB image: a horizontal gradient with a circle.
height, width = 200, 300
yy, xx = np.mgrid[0:height, 0:width]
red = (xx * 255 / width).astype(np.uint8)
green = (yy * 255 / height).astype(np.uint8)
blue = np.full_like(red, 80)

# Add a brighter disc in the middle to give the eye something to track.
cy, cx = height // 2, width // 2
disc = (yy - cy) ** 2 + (xx - cx) ** 2 < 50 ** 2
red[disc] = 255
green[disc] = 240
blue[disc] = 200

decoded = np.dstack([red, green, blue])

note(
    f"Array shape: <code>{decoded.shape}</code>, "
    f"dtype: <code>{decoded.dtype}</code>. "
    "This is exactly the layout you would get from "
    "<code>np.asarray(pi_heif.open_heif('photo.heic'))</code>."
)

# Show channel statistics, the kind of summary you'd compute right
# after decoding.
channel_names = ["R", "G", "B"]
fig, axes = plt.subplots(1, 2, figsize=(10, 4))

axes[0].imshow(decoded)
axes[0].set_title("Decoded image")
axes[0].axis("off")

for i, name in enumerate(channel_names):
    axes[1].hist(
        decoded[..., i].ravel(),
        bins=32,
        alpha=0.5,
        label=name,
        color=name.lower().replace("r", "red").replace("g", "green").replace("b", "blue"),
    )
axes[1].set_title("Per-channel histogram")
axes[1].set_xlabel("Pixel value")
axes[1].set_ylabel("Count")
axes[1].legend()
fig.tight_layout()
display(fig, append=True)

# The HeifFile object also carries useful metadata. Show the kinds of
# attributes you can read from it.
note("Typical attributes available on a <code>HeifFile</code>:")
display(HTML(
    "<ul>"
    "<li><code>heif_file.size</code> &mdash; (width, height) tuple</li>"
    "<li><code>heif_file.mode</code> &mdash; e.g. 'RGB', 'RGBA', 'BGR;16'</li>"
    "<li><code>heif_file.has_alpha</code> &mdash; bool</li>"
    "<li><code>heif_file.bit_depth</code> &mdash; 8, 10, or 12</li>"
    "<li><code>heif_file.info['exif']</code> &mdash; raw EXIF bytes if present</li>"
    "</ul>"
), append=True)
