# pyasn1 decouples ASN.1 types from serialization. The same value can
# be encoded with several codecs: BER (basic), CER (canonical, useful
# for streaming), and DER (canonical, used in X.509, PKCS, etc.).

# A SEQUENCE describing a tagged measurement: a sensor OID, a label,
# and an integer reading.
class Measurement(Sequence):
    componentType = NamedTypes(
        NamedType("sensor", ObjectIdentifier()),
        NamedType("label", UTF8String()),
        NamedType("reading", Integer()),
    )


reading = Measurement()
reading["sensor"] = "1.3.6.1.4.1.99999.1"  # made-up enterprise OID
reading["label"] = "kitchen-thermometer"
reading["reading"] = 21

heading("One value, three encodings")
note(
    "Each codec produces standards-compliant bytes. BER is the most "
    "permissive; CER and DER are canonical (a given value has exactly "
    "one valid encoding)."
)

for name, encode in [("BER", ber_encode), ("CER", cer_encode), ("DER", der_encode)]:
    substrate = encode(reading)
    note(f"<strong>{name}</strong> ({len(substrate)} bytes):")
    display(HTML(f"<pre>{hexdump(substrate)}</pre>"), append=True)

heading("A SEQUENCE OF Measurement")
note(
    "ASN.1 SEQUENCE OF is the natural fit for a homogeneous list. "
    "We build three readings, encode the lot to DER, and round-trip "
    "back to inspect the contents."
)


class MeasurementLog(SequenceOf):
    componentType = Measurement()


log = MeasurementLog()
samples = [
    ("1.3.6.1.4.1.99999.1", "kitchen-thermometer", 21),
    ("1.3.6.1.4.1.99999.2", "garage-thermometer", 8),
    ("1.3.6.1.4.1.99999.3", "attic-thermometer", 27),
]
for oid, label, value in samples:
    item = Measurement()
    item["sensor"] = oid
    item["label"] = label
    item["reading"] = value
    log.append(item)

substrate = der_encode(log)
note(f"DER-encoded log is <strong>{len(substrate)}</strong> bytes.")
display(HTML(f"<pre>{hexdump(substrate)}</pre>"), append=True)

decoded_log, _ = der_decode(substrate, asn1Spec=MeasurementLog())
rows = ["<table><tr><th>sensor OID</th><th>label</th><th>reading</th></tr>"]
for item in decoded_log:
    rows.append(
        f"<tr><td><code>{item['sensor']}</code></td>"
        f"<td>{item['label']}</td>"
        f"<td>{int(item['reading'])}</td></tr>"
    )
rows.append("</table>")
display(HTML("".join(rows)), append=True)
