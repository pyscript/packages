# ---------------------------------------------------------------------
# A realistic editing workflow: build a source shapefile, then stream
# through it filtering by attribute and bounding box, writing only the
# matching features (and only the fields we care about) to a new file.
# ---------------------------------------------------------------------

heading("Source data: weather stations across a region")
note(
    "We'll synthesize a polyline shapefile of fictional river "
    "segments tagged by basin and length, then produce a derived "
    "shapefile containing only the long segments in one basin."
)

# Build the source shapefile in memory.
src_shp, src_shx, src_dbf = io.BytesIO(), io.BytesIO(), io.BytesIO()

rivers = [
    ("Otter Brook",  "North", 4.2,  [(0, 0), (1, 2), (2, 5)]),
    ("Heron Creek",  "North", 1.1,  [(2, 5), (3, 5)]),
    ("Pine River",   "North", 8.7,  [(3, 5), (5, 6), (8, 8), (10, 9)]),
    ("Willow Run",   "South", 2.5,  [(0, -1), (2, -2), (4, -2)]),
    ("Birch Stream", "South", 6.0,  [(4, -2), (7, -3), (10, -4)]),
    ("Cedar Wash",   "South", 0.9,  [(7, -3), (8, -3)]),
]

with shapefile.Writer(shp=src_shp, shx=src_shx, dbf=src_dbf) as writer:
    writer.field("name",     "C", size=40)
    writer.field("basin",    "C", size=10)
    writer.field("length_km", "N", decimal=1)
    writer.field("notes",    "C", size=80)   # a field we'll later drop

    for name, basin, length, coords in rivers:
        writer.line([coords])
        writer.record(name, basin, length, "auto-generated sample")

heading("Streaming filter and rewrite", level=3)
note(
    "We open the source with a Reader, request only the fields we "
    "need via <code>iterShapeRecords(fields=...)</code>, and use a "
    "<code>bbox</code> argument so the Reader's spatial index "
    "skips features whose bounding boxes can't possibly match."
)

for buf in (src_shp, src_shx, src_dbf):
    buf.seek(0)

dst_shp, dst_shx, dst_dbf = io.BytesIO(), io.BytesIO(), io.BytesIO()

# Region of interest: a bounding box covering the eastern half.
region_bbox = [3, -5, 11, 10]
keep_fields = ["name", "basin", "length_km"]

reader = shapefile.Reader(shp=src_shp, shx=src_shx, dbf=src_dbf)
writer = shapefile.Writer(shp=dst_shp, shx=dst_shx, dbf=dst_dbf)

# Copy only the fields we want to keep (skip the leading DeletionFlag).
for field in reader.fields[1:]:
    if field.name in keep_fields:
        writer.field(*field)

kept = []
for shape_record in reader.iterShapeRecords(
    bbox=region_bbox, fields=keep_fields,
):
    record = shape_record.record
    if record["basin"] == "North" and record["length_km"] >= 4.0:
        writer.shape(shape_record.shape)
        writer.record(*[record[name] for name in keep_fields])
        kept.append(record["name"])

writer.close()
reader.close()

note(f"Kept {len(kept)} feature(s): " + ", ".join(kept))

# Read the new shapefile back and visualize the result.
for buf in (dst_shp, dst_shx, dst_dbf):
    buf.seek(0)

result = shapefile.Reader(shp=dst_shp, shx=dst_shx, dbf=dst_dbf)

note(
    f"Output shapefile: <code>{result.shapeTypeName}</code>, "
    f"{len(result)} feature(s), "
    f"{len(result.fields) - 1} field(s) "
    "(notice the <code>notes</code> field was dropped)."
)

fig, ax = plt.subplots(figsize=(7, 4))

# Draw the original rivers in light gray for context.
src_shp.seek(0); src_shx.seek(0); src_dbf.seek(0)
context = shapefile.Reader(shp=src_shp, shx=src_shx, dbf=src_dbf)
for shape in context.iterShapes():
    xs, ys = zip(*shape.points)
    ax.plot(xs, ys, color="lightgray", linewidth=1)
context.close()

# Overlay the surviving features in bold.
for shape_record in result.iterShapeRecords():
    xs, ys = zip(*shape_record.shape.points)
    ax.plot(xs, ys, linewidth=2.5,
            label=shape_record.record["name"])

# Show the query bounding box.
x0, y0, x1, y1 = region_bbox
ax.plot([x0, x1, x1, x0, x0], [y0, y0, y1, y1, y0],
        linestyle="--", color="darkorange", label="query bbox")

ax.set_aspect("equal")
ax.set_title("Long rivers in the North basin, within the query box")
ax.legend(loc="lower right", fontsize=8)
fig.tight_layout()
display(fig, append=True)

result.close()
