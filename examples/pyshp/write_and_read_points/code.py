"""
A first look at PyShp: write a small Point shapefile entirely in
memory, then read it back to verify the geometry and attributes.

PyShp is the pure-Python reader/writer for the ESRI Shapefile format.
The PyPI distribution is named `pyshp`, but the import name is
`shapefile`. Docs and source: https://github.com/GeospatialPython/pyshp
"""
from IPython.core.display import display, HTML
# pyshp is imported as the `shapefile` module.
import shapefile
import io


heading("A handful of lighthouses")
note(
    "A shapefile is really three files working together: "
    "<code>.shp</code> (geometry), <code>.shx</code> (index), "
    "and <code>.dbf</code> (attribute table). PyShp can read and "
    "write each one to a file-like object, which is exactly what "
    "we want in the browser."
)

# Three buffers stand in for the three files on disk.
shp_buffer = io.BytesIO()
shx_buffer = io.BytesIO()
dbf_buffer = io.BytesIO()

# A small dataset: famous lighthouses with their (lon, lat) coordinates.
lighthouses = [
    ("Eddystone",       -4.2636, 50.1922, 1882),
    ("Fastnet",         -9.6033, 51.3833, 1904),
    ("Cape Hatteras",  -75.5290, 35.2503, 1870),
    ("Tower of Hercules", -8.4063, 43.3863,  100),
]

# Build the shapefile by streaming records into the Writer.
with shapefile.Writer(
    shp=shp_buffer, shx=shx_buffer, dbf=dbf_buffer,
) as writer:
    # Define the attribute schema before adding any records.
    writer.field("name",     "C", size=40)   # text
    writer.field("year",     "N", decimal=0) # integer year built

    for name, lon, lat, year in lighthouses:
        writer.point(lon, lat)
        writer.record(name, year)

note(f"Wrote {len(lighthouses)} point features to in-memory buffers.")

# Reading is symmetric: hand the buffers to a Reader.
for buf in (shp_buffer, shx_buffer, dbf_buffer):
    buf.seek(0)

reader = shapefile.Reader(
    shp=shp_buffer, shx=shx_buffer, dbf=dbf_buffer,
)

heading("What did we just write?", level=3)
note(
    f"Shape type: <code>{reader.shapeTypeName}</code>. "
    f"Feature count: <strong>{len(reader)}</strong>. "
    f"Bounding box: <code>{tuple(round(c, 3) for c in reader.bbox)}</code>."
)

heading("Iterating shape/record pairs", level=3)
rows = []
for shape_record in reader.iterShapeRecords():
    (lon, lat) = shape_record.shape.points[0]
    name = shape_record.record["name"]
    year = shape_record.record["year"]
    rows.append(f"<tr><td>{name}</td><td>{year}</td>"
                f"<td>{lon:.3f}, {lat:.3f}</td></tr>")

table = (
    "<table><thead><tr><th>Name</th><th>Built</th>"
    "<th>Lon, Lat</th></tr></thead><tbody>"
    + "".join(rows) + "</tbody></table>"
)
display(HTML(table), append=True)

reader.close()
