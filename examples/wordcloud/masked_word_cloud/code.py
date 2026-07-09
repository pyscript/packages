# ---------------------------------------------------------------------
# Confine the layout to a shape using a mask array.
# ---------------------------------------------------------------------


import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS

heading("A heart-shaped word cloud")
note(
    "A 'mask' is a NumPy array the same size as the output. Pixels "
    "that are 255 (white) are off-limits; everything else is fair game "
    "for placing words. Build any silhouette you like."
)

# Build a heart-shaped mask analytically. White (255) is background;
# black (0) is where words may go.
height, width = 400, 500
y_coords, x_coords = np.ogrid[:height, :width]

# Normalize coordinates to a centered, scaled space.
x_norm = (x_coords - width / 2) / (width / 2.5)
y_norm = -(y_coords - height / 2) / (height / 2.5)

# Classic heart curve: (x^2 + y^2 - 1)^3 - x^2 * y^3 <= 0
heart = (x_norm**2 + y_norm**2 - 1)**3 - (x_norm**2) * (y_norm**3)
mask = np.where(heart <= 0, 0, 255).astype(np.uint8)

# Words for a wedding-toast theme. Repetition determines size.
toast = (
    "love love love love laughter laughter laughter joy joy joy "
    "kindness kindness kindness adventure adventure together together "
    "together forever forever family friends friends home home home "
    "trust trust patience growth growth dreams dreams dreams memories "
    "memories laughter sunshine warmth warmth warmth dancing music "
    "celebration celebration toast toast cheers cheers cheers"
)

cloud = WordCloud(
    background_color="white",
    mask=mask,
    contour_width=2,
    contour_color="crimson",
    colormap="RdPu",
    stopwords=set(STOPWORDS),
    random_state=1,
).generate(toast)

fig, ax = plt.subplots(figsize=(8, 6.4))
ax.imshow(cloud, interpolation="bilinear")
ax.axis("off")
fig.tight_layout()
display(fig, append=True)

note(
    "Try swapping the mask for any black-and-white image (e.g. via "
    "PIL.Image and np.array) to fit your cloud into logos, animals, "
    "or country outlines. The colormap argument accepts any matplotlib "
    "colormap name."
)
