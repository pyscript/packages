# The "native" codec converts pyasn1 objects to plain Python dicts/lists
# and back. This is handy for moving data between an ASN.1-shaped wire
# format and the dict/list world of JSON, configs, and tests.

from pyasn1.type.univ import Integer, Sequence, SequenceOf
from pyasn1.type.char import UTF8String
from pyasn1.type.namedtype import NamedTypes, NamedType, OptionalNamedType
from pyasn1.codec.der.encoder import encode as der_encode
from pyasn1.codec.der.decoder import decode as der_decode
from pyasn1.codec.native.encoder import encode as to_python
from pyasn1.codec.native.decoder import decode as from_python


def hexdump(data):
    return " ".join(f"{b:02X}" for b in data)


class Address(Sequence):
    componentType = NamedTypes(
        NamedType("street", UTF8String()),
        NamedType("city", UTF8String()),
        OptionalNamedType("postcode", UTF8String()),
    )


class Contact(Sequence):
    componentType = NamedTypes(
        NamedType("name", UTF8String()),
        NamedType("age", Integer()),
        NamedType("address", Address()),
    )


class ContactBook(SequenceOf):
    componentType = Contact()


heading("From Python dicts into pyasn1")
note(
    "Start with ordinary Python data, then hand it to the native "
    "decoder along with a schema. pyasn1 builds the corresponding "
    "ASN.1 object tree."
)

people = [
    {
        "name": "Ada Lovelace",
        "age": 36,
        "address": {"street": "1 Analytical Way", "city": "London"},
    },
    {
        "name": "Grace Hopper",
        "age": 85,
        "address": {
            "street": "42 Compiler Ave",
            "city": "Arlington",
            "postcode": "22202",
        },
    },
]

book = from_python(people, asn1Spec=ContactBook())
display(HTML(f"<pre>{str(book)}</pre>"), append=True)

heading("Round-tripping through DER")
note(
    "Encode to DER for the wire, decode back, then flatten to native "
    "Python with the native encoder. Optional fields that were absent "
    "stay absent in the output."
)

wire = der_encode(book)
note(f"DER payload is <strong>{len(wire)}</strong> bytes.")
display(HTML(f"<pre>{hexdump(wire)}</pre>"), append=True)

restored, _ = der_decode(wire, asn1Spec=ContactBook())
as_python = to_python(restored)

# Render the recovered Python structure as an HTML table.
rows = ["<table><tr><th>name</th><th>age</th><th>city</th><th>postcode</th></tr>"]
for entry in as_python:
    addr = entry["address"]
    rows.append(
        f"<tr><td>{entry['name']}</td>"
        f"<td>{entry['age']}</td>"
        f"<td>{addr['city']}</td>"
        f"<td>{addr.get('postcode', '—')}</td></tr>"
    )
rows.append("</table>")
display(HTML("".join(rows)), append=True)

note(
    "Tip: pair this with <code>pyasn1-modules</code> to work with "
    "real-world ASN.1 schemas like X.509 certificates, PKCS, and SNMP."
)
