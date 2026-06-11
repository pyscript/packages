# ---------------------------------------------------------------------
# Polygon shapefiles, holes, and GeoJSON via __geo_interface__.
# ---------------------------------------------------------------------

import shapefile
import io
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch

heading("Tiny parks dataset")
note(
    "Polygons in shapefiles must be closed (the last point repeats "
    "the first). Crucially, the shapefile format has no flag to "
    "distinguish an outer ring from a hole — the only signal is "
    "winding order: outer rings clockwise, holes counterclockwise. "
    "Get this wrong and tools that consume the file (including "
    "PyShp's own GeoJSON conversion) will misread your geometry."
)

shp_buf, shx_buf, dbf_buf = io.BytesIO(), io.BytesIO(), io.BytesIO()

# A square park with a square pond cut out, plus a triangular plaza.
# Outer rings are clockwise; holes are counterclockwise.
park_outer = [(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]  # clockwise
pond_hole  = [(3, 3), (3, 7), (7, 7), (7, 3), (3, 3)]      # counterclockwise
plaza      = [(15, 2), (17, 8), (20, 2), (15, 2)]          # clockwise

with shapefile.Writer(shp=shp_buf, shx=shx_buf, dbf=dbf_buf) as writer:
    writer.field("name",     "C", size=30)
    writer.field("area_sqm", "N", decimal=1)

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

heading("Plotting polygons with real holes", level=3)
note(
    "GeoJSON's nested-ring structure encodes holes semantically, but "
    "matplotlib needs you to translate that into a compound "
    "<code>Path</code>: outer ring plus inner rings as sub-paths in a "
    "single <code>PathPatch</code>. This renders holes as genuinely "
    "transparent — unlike the common shortcut of overpainting with a "
    "white fill, which breaks the moment you have a non-white "
    "background or layered features."
)

# Plot the polygons using their GeoJSON coordinates.
fig, ax = plt.subplots(figsize=(7, 4))
colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

for i, feature in enumerate(geojson["features"]):
    geom = feature["geometry"]
    name = feature["properties"]["name"]
    color = colors[i % len(colors)]
    # GeoJSON nests rings as [[outer, hole, ...]] for Polygons,
    # and one level deeper for MultiPolygons.
    polygons = (
        geom["coordinates"]
        if geom["type"] == "MultiPolygon"
        else [geom["coordinates"]]
    )
    for rings in polygons:
        # Build a compound path: outer ring + holes as sub-paths.
        # Matplotlib renders the holes as genuinely transparent when
        # the path alternates winding between outer and inner rings.
        vertices = []
        codes = []
        for ring in rings:
            vertices.extend(ring)
            codes.append(Path.MOVETO)
            codes.extend([Path.LINETO] * (len(ring) - 2))
            codes.append(Path.CLOSEPOLY)
        path = Path(vertices, codes)
        patch = PathPatch(path, facecolor=color, alpha=0.4, label=name)
        ax.add_patch(patch)

ax.set_aspect("equal")
ax.autoscale_view()
ax.set_title("Parks polygons (with a pond-shaped hole)")
ax.legend(loc="upper right")
fig.tight_layout()
display(fig, append=True)

reader.close()