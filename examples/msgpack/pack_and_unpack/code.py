"""
A first look at msgpack: a compact, fast binary serialization format
that's a drop-in alternative to JSON for many use cases.

Docs: https://msgpack-python.readthedocs.io/
"""
from IPython.core.display import display, HTML

# A small payload that might fly between two services: a sensor reading
# from a fictional weather station.
reading = {
    "station_id": "WX-204",
    "location": [52.52, 13.405],
    "temperature_c": 18.7,
    "humidity_pct": 64,
    "active": True,
    "tags": ["calibrated", "outdoor"],
}

heading("1. Pack a Python object into bytes")
note(
    "msgpack.packb turns Python data into a compact bytes object. "
    "msgpack.unpackb is the inverse."
)

packed = msgpack.packb(reading)
display(HTML(f"<pre>type: {type(packed).__name__}<br>"
             f"bytes: {packed!r}</pre>"), append=True)

restored = msgpack.unpackb(packed)
note("Round-tripped back to a Python dict:")
display(restored, append=True)

heading("2. Compared with JSON")
note(
    "For the same data, MessagePack is typically smaller than the "
    "equivalent JSON text, and faster to parse. Sizes for our reading:"
)

json_bytes = json.dumps(reading).encode("utf-8")
sizes = {
    "json (utf-8 bytes)": len(json_bytes),
    "msgpack (bytes)": len(packed),
    "msgpack savings": f"{100 * (1 - len(packed) / len(json_bytes)):.1f}%",
}
display(sizes, append=True)

heading("3. Aliases for the json/pickle crowd")
note(
    "msgpack.dumps and msgpack.loads are aliases for packb and unpackb, "
    "so the API feels familiar."
)

same = msgpack.loads(msgpack.dumps(reading))
note(f"Round-trip equal to the original? <strong>{same == reading}</strong>")
