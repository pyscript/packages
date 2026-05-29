# ---------------------------------------------------------------------
# Counting and sampling certificates inside the bundle.
# ---------------------------------------------------------------------

heading("How many certificates are in the bundle?")
note(
    "<code>certifi.contents()</code> returns the entire PEM file as a "
    "string. Each trusted root is delimited by "
    "<code>-----BEGIN CERTIFICATE-----</code> / "
    "<code>-----END CERTIFICATE-----</code> markers, so a quick count "
    "of the begin markers tells us how many roots Mozilla currently "
    "trusts."
)

pem_text = certifi.contents()
begin_marker = "-----BEGIN CERTIFICATE-----"
certificate_count = pem_text.count(begin_marker)

display(
    HTML(
        f"<p>Bundle size: <strong>{len(pem_text):,}</strong> characters, "
        f"containing <strong>{certificate_count}</strong> "
        f"trusted root certificates.</p>"
    ),
    append=True,
)

heading("Reading the human-readable headers")
note(
    "Mozilla's bundle prefixes each PEM block with a friendly comment "
    "header naming the certificate authority. We can split the file "
    "on the begin marker and pull out the first non-empty line of each "
    "preamble to get a quick directory of trusted CAs."
)

# Split into preamble + PEM block pairs. The first chunk is just the
# top-of-file preamble; skip it.
chunks = pem_text.split(begin_marker)[1:]

ca_names = []
for chunk in chunks:
    # The CA name appears in the preamble *before* this BEGIN marker,
    # which is the tail of the previous chunk. Reconstruct that by
    # walking the original split differently.
    pass

# Simpler approach: iterate over the lines and capture the last
# non-empty comment line preceding each BEGIN marker.
last_label = None
labels = []
for line in pem_text.splitlines():
    stripped = line.strip()
    if not stripped:
        continue
    if stripped == begin_marker:
        labels.append(last_label or "(unlabeled)")
    elif not stripped.startswith("-----"):
        last_label = stripped

note(f"First 10 trusted CAs (out of {len(labels)}):")
sample_html = "<ol>" + "".join(
    f"<li>{name}</li>" for name in labels[:10]
) + "</ol>"
display(HTML(sample_html), append=True)

heading("Using the bundle with another library")
note(
    "When you make HTTPS calls with libraries like <code>requests</code>, "
    "you can pass <code>verify=certifi.where()</code> to ensure they "
    "validate against this exact bundle. For example: "
    "<code>requests.get(url, verify=certifi.where())</code>."
)
