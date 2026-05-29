# ---------------------------------------------------------------------
# Polygon shapefiles, holes, and GeoJSON via __geo_interface__.
# ---------------------------------------------------------------------

heading("Tiny parks dataset")
note(
    "Polygons in shapefiles must be closed (the last point repeats "
    "the first), and holes are signalled by reversing the winding "
    "order: outer rings clockwise, holes counterclockwise. PyShp "
    "auto-closes rings if you forget the last point."
)

shp_buf, shx_buf, dbf_buf = io.BytesIO(), io.BytesIO(), io.BytesIO()

# A square park with a square pond cut out, plus a triangular plaza.
park_outer = [(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)]
pond_hole  = [(3, 3), (7, 3), (7, 7), (3, 7), (3, 3)]   # counterclockwise
plaza      = [(15, 2), (20, 2), (17, 8), (15, 2)]

with shapefile.Writer(shp=shp_buf, shx=shx_buf, dbf=dbf_buf) as writer:
    writer.field("name",       "C", size=30)
    writer.field("area_sqm",   "N", decimal=1)

    # A single polygon feature with an outer ring and a hole.
    writer.poly([park_outer, pond_hole])
    writer.record("Riverside Park", 84.0)

    # A separate polygon feature with no holes.
    writer.poly([plaza])
    writer.record("Civic Plaza", 15.0)

for buf in (shp_buf, shx_buf, dbf_buf):
    buf.seek(0)

reader = shapefile.Reader(shp=shp_buf, shx=shx_buf, dbf=dbf_buf)

heading("Inspecting parts and points", level=3)
for shape_record in reader.iterShapeRecords():
    shape = shape_record.shape
    name = shape_record.record["name"]
    note(
        f"<strong>{name}</strong>: shape type "
        f"<code>{shape.shapeTypeName}</code>, "
        f"{len(shape.points)} points across "
        f"{len(shape.parts)} ring(s) "
        f"(part start indices: {list(shape.parts)})."
    )

heading("GeoJSON for free", level=3)
note(
    "Every Shape, Record, and Reader implements "
    "<code>__geo_interface__</code>, so converting to GeoJSON is "
    "a one-liner that any geospatial tool can consume."
)
geojson = reader.__geo_interface__
display(HTML(
    f"<pre>type: {geojson['type']}\\n"
    f"features: {len(geojson['features'])}\\n"
    f"first geometry type: {geojson['features'][0]['geometry']['type']}"
    "</pre>"
), append=True)

# Plot the polygons using their GeoJSON coordinates.
fig, ax = plt.subplots(figsize=(7, 4))
for feature in geojson["features"]:
    geom = feature["geometry"]
    name = feature["properties"]["name"]
    # GeoJSON nests rings as [[outer, hole, ...]] for Polygons,
    # and one level deeper for MultiPolygons.
    polygons = (
        geom["coordinates"]
        if geom["type"] == "MultiPolygon"
        else [geom["coordinates"]]
    )
    for rings in polygons:
        outer = rings[0]
        xs, ys = zip(*outer)
        ax.fill(xs, ys, alpha=0.4, label=name)
        for hole in rings[1:]:
            hx, hy = zip(*hole)
            ax.fill(hx, hy, color="white")

ax.set_aspect("equal")
ax.set_title("Parks polygons (with a pond-shaped hole)")
ax.legend(loc="upper right")
fig.tight_layout()
display(fig, append=True)

reader.close()
