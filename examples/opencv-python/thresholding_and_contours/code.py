# ---------------------------------------------------------------------
# Segment shapes from the background and measure them with contours.
# ---------------------------------------------------------------------

heading("A scattering of coins (well, disks)")
note(
    "We sprinkle a handful of bright disks of varying size onto a "
    "dark background, then use thresholding and findContours to "
    "count them and measure each one's area and centroid."
)

# Synthetic scene: dark background with several light circles.
image = np.full((260, 360, 3), 30, dtype=np.uint8)

disks = [
    (60, 70, 25),
    (140, 90, 35),
    (240, 60, 20),
    (310, 130, 30),
    (90, 180, 40),
    (200, 200, 28),
    (290, 210, 22),
]
for cx, cy, r in disks:
    color = tuple(int(v) for v in rng.integers(180, 255, size=3))
    cv2.circle(image, (cx, cy), r, color, thickness=-1)

# Threshold on grayscale to separate foreground from background.
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)

# Find external contours (one per disk).
contours, _ = cv2.findContours(
    binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE,
)

note(f"Found <strong>{len(contours)}</strong> contours.")

# Annotate a copy of the original image with each contour's bounding
# box, centroid, and area.
annotated = image.copy()
rows = []
for index, contour in enumerate(contours, start=1):
    area = cv2.contourArea(contour)
    x, y, w, h = cv2.boundingRect(contour)

    # Image moments give us the centroid (cx, cy) of the contour.
    moments = cv2.moments(contour)
    if moments["m00"] > 0:
        cx = int(moments["m10"] / moments["m00"])
        cy = int(moments["m01"] / moments["m00"])
    else:
        cx, cy = x + w // 2, y + h // 2

    cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 255, 255), 2)
    cv2.circle(annotated, (cx, cy), 3, (0, 0, 255), -1)
    cv2.putText(
        annotated, str(index), (cx + 6, cy - 6),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA,
    )
    rows.append((index, area, (cx, cy), (w, h)))

# Display the pipeline: original, binary mask, annotated result.
fig, axes = plt.subplots(1, 3, figsize=(12, 4))
axes[0].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
axes[0].set_title("Original")
axes[1].imshow(binary, cmap="gray")
axes[1].set_title("Binary mask (threshold)")
axes[2].imshow(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB))
axes[2].set_title("Contours, bounding boxes, centroids")
for ax in axes:
    ax.axis("off")
fig.tight_layout()
display(fig, append=True)

# Print a small report of the per-disk measurements.
report_rows = "".join(
    f"<tr><td>{i}</td><td>{area:.0f}</td>"
    f"<td>({cx}, {cy})</td><td>{w}x{h}</td></tr>"
    for i, area, (cx, cy), (w, h) in rows
)
display(HTML(
    "<table><thead><tr><th>#</th><th>Area (px)</th>"
    "<th>Centroid</th><th>Bounding box</th></tr></thead>"
    f"<tbody>{report_rows}</tbody></table>"
), append=True)
