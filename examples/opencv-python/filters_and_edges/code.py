# ---------------------------------------------------------------------
# Smoothing noisy images and finding edges with Canny.
# ---------------------------------------------------------------------

heading("Build a noisy test image")
note(
    "We make a synthetic grayscale scene of overlapping shapes, "
    "then add Gaussian noise. This gives us something to denoise "
    "and find edges in."
)

scene = np.full((200, 300), 40, dtype=np.uint8)
cv2.rectangle(scene, (30, 40), (140, 160), 200, thickness=-1)
cv2.circle(scene, (210, 100), 55, 140, thickness=-1)
cv2.rectangle(scene, (170, 30), (260, 80), 90, thickness=-1)

# Add Gaussian noise and clip back to valid 8-bit range.
noise = rng.normal(0, 25, size=scene.shape)
noisy = np.clip(scene.astype(np.int16) + noise, 0, 255).astype(np.uint8)

note(
    f"Clean image dtype: {scene.dtype}, range "
    f"[{scene.min()}, {scene.max()}]. Noisy range "
    f"[{noisy.min()}, {noisy.max()}]."
)

# ---------------------------------------------------------------------
# Smooth with a Gaussian blur, then run Canny edge detection.
# ---------------------------------------------------------------------

# Gaussian blur: kernel size must be odd. Sigma 0 lets cv2 derive it.
smoothed = cv2.GaussianBlur(noisy, ksize=(5, 5), sigmaX=0)

# Canny works best on a smoothed image. The two thresholds control
# which gradient magnitudes are kept (low) and which definitely start
# an edge (high).
edges_noisy = cv2.Canny(noisy, threshold1=80, threshold2=160)
edges_smooth = cv2.Canny(smoothed, threshold1=80, threshold2=160)

fig, axes = plt.subplots(2, 2, figsize=(9, 6))
axes[0, 0].imshow(noisy, cmap="gray")
axes[0, 0].set_title("Noisy input")
axes[0, 1].imshow(smoothed, cmap="gray")
axes[0, 1].set_title("Gaussian-blurred")
axes[1, 0].imshow(edges_noisy, cmap="gray")
axes[1, 0].set_title("Canny on noisy (lots of false edges)")
axes[1, 1].imshow(edges_smooth, cmap="gray")
axes[1, 1].set_title("Canny on blurred (cleaner edges)")
for ax in axes.flat:
    ax.axis("off")
fig.tight_layout()
display(fig, append=True)

note(
    "Smoothing first removes high-frequency noise so the gradient-"
    "based Canny detector finds the true object boundaries instead "
    "of grain."
)
