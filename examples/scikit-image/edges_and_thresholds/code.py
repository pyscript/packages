"""
A first look at scikit-image: load a sample image, convert to grayscale,
and detect edges.

scikit-image ships with several standard sample images in `skimage.data`
which are perfect for experimenting without needing any files. See:
https://scikit-image.org/docs/stable/api/skimage.data.html
"""
from IPython.core.display import display, HTML

# Package imports for this example.
import numpy as np
import matplotlib.pyplot as plt
import skimage
from skimage import data, filters, color


heading("Meet scikit-image")
note(
    f"Using scikit-image version <strong>{skimage.__version__}</strong>. "
    "We'll start with the classic 'astronaut' sample image, "
    "look at its shape, and run a couple of basic operations."
)

# Load a built-in sample image. It's a NumPy array of shape (H, W, 3).
astronaut = data.astronaut()
note(
    f"Image shape: <code>{astronaut.shape}</code>, "
    f"dtype: <code>{astronaut.dtype}</code>. "
    "That's height x width x RGB channels."
)

# Convert to grayscale, then run two classic edge detectors.
gray = color.rgb2gray(astronaut)
edges_sobel = filters.sobel(gray)
threshold = filters.threshold_otsu(gray)
binary = gray > threshold

# Show the four images side by side.
fig, axes = plt.subplots(1, 4, figsize=(11, 3))
panels = [
    (astronaut, "Original (RGB)", None),
    (gray, "Grayscale", "gray"),
    (edges_sobel, "Sobel edges", "magma"),
    (binary, f"Otsu threshold > {threshold:.2f}", "gray"),
]
for ax, (img, title, cmap) in zip(axes, panels):
    ax.imshow(img, cmap=cmap)
    ax.set_title(title, fontsize=10)
    ax.axis("off")
fig.tight_layout()
display(fig, append=True)
