# ---------------------------------------------------------------------
# Corner detection and geometric transforms.
# ---------------------------------------------------------------------

import numpy as np
import matplotlib.pyplot as plt
import skimage
from skimage import data, feature, transform, color, exposure


heading("Corners and geometric transforms")
note(
    "We'll find corner-like features with the Harris detector, then "
    "apply an affine warp to the image and see how the geometry "
    "shifts. Useful building blocks for registration and stitching."
)

# Use the checkerboard sample: corners are extremely well-defined.
board = data.checkerboard().astype(float)

# Harris response highlights corner-like pixels; `corner_peaks` picks
# the local maxima above a threshold.
harris_response = feature.corner_harris(board)
corners = feature.corner_peaks(
    harris_response, min_distance=5, threshold_rel=0.02,
)
note(f"Harris detected <strong>{len(corners)}</strong> corner peaks.")

# Build an affine transform: rotate, scale, translate.
affine = transform.AffineTransform(
    scale=(0.85, 0.85),
    rotation=np.deg2rad(15),
    translation=(20, -10),
)
warped = transform.warp(board, affine.inverse, mode="constant", cval=0.5)

# Map detected corner coordinates through the same transform to confirm
# they line up with corners in the warped image.
warped_corners = affine(corners[:, [1, 0]])  # (row, col) -> (x, y)

fig, axes = plt.subplots(1, 2, figsize=(9, 4.5))
axes[0].imshow(board, cmap="gray")
axes[0].scatter(corners[:, 1], corners[:, 0], s=30,
                facecolors="none", edgecolors="red")
axes[0].set_title(f"Original + {len(corners)} Harris corners")

axes[1].imshow(warped, cmap="gray")
axes[1].scatter(warped_corners[:, 0], warped_corners[:, 1], s=30,
                facecolors="none", edgecolors="lime")
axes[1].set_title("Affine-warped (rotate, scale, shift)")
for ax in axes:
    ax.axis("off")
fig.tight_layout()
display(fig, append=True)

# Bonus: equalize a low-contrast image to show histogram-based tooling.
heading("Contrast stretching with exposure")
moon = data.moon()
equalized = exposure.equalize_hist(moon)

fig2, axes2 = plt.subplots(2, 2, figsize=(9, 6))
axes2[0, 0].imshow(moon, cmap="gray")
axes2[0, 0].set_title("Original moon")
axes2[0, 0].axis("off")
axes2[0, 1].imshow(equalized, cmap="gray")
axes2[0, 1].set_title("Histogram-equalized")
axes2[0, 1].axis("off")
axes2[1, 0].hist(moon.ravel(), bins=64, color="steelblue")
axes2[1, 0].set_title("Original histogram")
axes2[1, 1].hist(equalized.ravel(), bins=64, color="darkorange")
axes2[1, 1].set_title("Equalized histogram")
fig2.tight_layout()
display(fig2, append=True)
