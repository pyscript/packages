# ---------------------------------------------------------------------
# Segmentation: counting and measuring coins in a sample image.
# ---------------------------------------------------------------------

heading("Counting coins with segmentation")
note(
    "The <code>data.coins()</code> sample is a grayscale photo of "
    "scattered coins. We'll threshold it, clean up the mask, label "
    "each connected component, and measure their properties."
)

coins = data.coins()

# Otsu picks a global threshold that separates foreground from background.
threshold = filters.threshold_otsu(coins)
foreground = coins > threshold

# Remove small specks and fill small holes inside coins.
cleaned = morphology.remove_small_objects(foreground, min_size=150)
cleaned = morphology.remove_small_holes(cleaned, area_threshold=150)

# Drop blobs touching the image border, then label remaining ones.
cleared = segmentation.clear_border(cleaned)
labels = measure.label(cleared)

note(f"Detected <strong>{labels.max()}</strong> coins after cleanup.")

# `regionprops_table` gives a dict of arrays we can hand to a plot.
properties = measure.regionprops_table(
    labels,
    intensity_image=coins,
    properties=("label", "area", "eccentricity", "mean_intensity"),
)

# Visualize: original, cleaned mask, and color-coded labels.
fig, axes = plt.subplots(1, 3, figsize=(11, 4))
axes[0].imshow(coins, cmap="gray")
axes[0].set_title("Original")
axes[1].imshow(cleared, cmap="gray")
axes[1].set_title("Cleaned binary mask")
axes[2].imshow(color.label2rgb(labels, image=coins, bg_label=0))
axes[2].set_title(f"{labels.max()} labeled regions")
for ax in axes:
    ax.axis("off")
fig.tight_layout()
display(fig, append=True)

# Plot area vs mean intensity to see how the coins cluster.
fig2, ax = plt.subplots(figsize=(7, 4))
ax.scatter(
    properties["area"],
    properties["mean_intensity"],
    c=properties["eccentricity"],
    cmap="viridis",
    s=60,
    edgecolor="black",
)
ax.set_xlabel("Area (pixels)")
ax.set_ylabel("Mean intensity")
ax.set_title("Per-coin properties (color = eccentricity)")
fig2.tight_layout()
display(fig2, append=True)
