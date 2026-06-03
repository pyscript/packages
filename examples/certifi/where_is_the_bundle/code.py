"""
A first look at certifi.

certifi packages Mozilla's curated set of root Certificate Authority
(CA) certificates as a single PEM file. Libraries that verify TLS
connections (requests, urllib3, httpx, ...) read this file to decide
which server certificates to trust.

The two things you almost always want to know:

1. Where is the bundle on disk?  ->  certifi.where()
2. What's actually inside it?    ->  certifi.contents()

Docs: https://github.com/certifi/python-certifi
"""
from IPython.core.display import display, HTML

import certifi


heading("1. The path to the trusted CA bundle")
note(
    "Most TLS-aware libraries accept a path to a PEM file via a "
    "<code>verify=</code> or <code>cafile=</code> argument. "
    "<code>certifi.where()</code> returns exactly that path."
)

bundle_path = certifi.where()
display(HTML(f"<pre>certifi.where() -> {bundle_path}</pre>"), append=True)

heading("2. A peek at the bundle file")
note(
    "The bundle is a plain text PEM file: one or more "
    "<code>-----BEGIN CERTIFICATE-----</code> blocks concatenated "
    "together. Here are the first few lines."
)

with open(bundle_path, "r", encoding="ascii") as f:
    preview = "".join(f.readline() for _ in range(8))

display(HTML(f"<pre>{preview}</pre>"), append=True)
