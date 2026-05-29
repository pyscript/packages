# ---------------------------------------------------------------------
# Structured access: info() dict and split version parts.
# ---------------------------------------------------------------------

heading("Structured distribution info")
note(
    "<code>distro.info()</code> bundles everything into a single "
    "dictionary, which is handy when you want to log or serialize "
    "the OS context (e.g. as part of a bug report or telemetry)."
)

info = distro.info()
display(info, append=True)

heading("Splitting the version into parts")
note(
    "Version strings are awkward to compare as text. "
    "<code>version_parts()</code> returns a "
    "<code>(major, minor, build_number)</code> tuple, and you can "
    "also ask for each piece individually."
)

major, minor, build = distro.version_parts(best=True)
rows = [
    ("major", major),
    ("minor", minor),
    ("build_number", build),
    ("major() helper", distro.major_version(best=True)),
    ("minor() helper", distro.minor_version(best=True)),
    ("build_number() helper", distro.build_number(best=True)),
]
table = "<table border='1' cellpadding='4'><tr><th>Field</th><th>Value</th></tr>"
for label, value in rows:
    table += f"<tr><td>{label}</td><td><code>{value!r}</code></code></tr>"
table += "</table>"
display(HTML(table), append=True)

note(
    "Passing <code>best=True</code> asks distro to consult every "
    "available data source and return the most precise version it "
    "can find, instead of stopping at the first match."
)
