"""
A first look at OpenCV (cv2): build a synthetic image, draw on it,
and convert between color spaces.

OpenCV stores images as NumPy arrays. Color images are typically in
BGR order (blue, green, red), which differs from matplotlib's RGB.
We'll use cv2.cvtColor to translate between the two when displaying.

Docs: https://docs.opencv.org/4.x/
"""
from IPython.core.display import display, HTML

import numpy as np
import cv2
import matplotlib.pyplot as plt

rng = np.random.default_rng(7)


heading("Drawing on a blank canvas")
note(
    "We start with a black 200x300 BGR image (a NumPy array of "
    "zeros) and draw a few primitives on it: a rectangle, a "
    "filled circle, a line, and some text."
)

# Create a blank BGR image: height=200, width=300, 3 channels.
canvas = np.zeros((200, 300, 3), dtype=np.uint8)

# Colors are (B, G, R) tuples in OpenCV.
cv2.rectangle(canvas, (20, 20), (140, 120), (0, 200, 255), thickness=3)
cv2.circle(canvas, (220, 70), 40, (0, 255, 0), thickness=-1)  # filled
cv2.line(canvas, (20, 160), (280, 160), (255, 100, 100), thickness=2)
cv2.putText(
    canvas, "hello, cv2",
    org=(40, 190),
    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
    fontScale=0.7,
    color=(255, 255, 255),
    thickness=2,
    lineType=cv2.LINE_AA,
)

note(f"Canvas shape: {canvas.shape}, dtype: {canvas.dtype}")

# Convert BGR -> RGB so matplotlib displays the colors correctly.
canvas_rgb = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)

fig, ax = plt.subplots(figsize=(6, 4))
ax.imshow(canvas_rgb)
ax.set_title("Primitives drawn with cv2")
ax.axis("off")
fig.tight_layout()
display(fig, append=True)


heading("Color spaces: BGR, RGB, and grayscale")
note(
    "Real images come in many color spaces. Here we build a small "
    "BGR test image with three colored stripes, then view it as "
    "RGB (wrong) and after converting BGR->RGB (correct), and as "
    "grayscale."
)

stripes = np.zeros((120, 300, 3), dtype=np.uint8)
stripes[:, :100] = (255, 0, 0)     # blue stripe in BGR
stripes[:, 100:200] = (0, 255, 0)  # green stripe
stripes[:, 200:] = (0, 0, 255)     # red stripe

stripes_rgb = cv2.cvtColor(stripes, cv2.COLOR_BGR2RGB)
stripes_gray = cv2.cvtColor(stripes, cv2.COLOR_BGR2GRAY)

fig, axes = plt.subplots(1, 3, figsize=(10, 3))
axes[0].imshow(stripes)  # matplotlib assumes RGB, so colors look swapped
axes[0].set_title("BGR shown as RGB (wrong)")
axes[1].imshow(stripes_rgb)
axes[1].set_title("After BGR->RGB (correct)")
axes[2].imshow(stripes_gray, cmap="gray")
axes[2].set_title("Grayscale")
for ax in axes:
    ax.axis("off")
fig.tight_layout()
display(fig, append=True)
