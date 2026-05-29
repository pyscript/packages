# ---------------------------------------------------------------------
# Reading raw resources out of the tzdata package.
# ---------------------------------------------------------------------

heading("What's actually inside the tzdata package?")
note(
    "tzdata ships a directory tree of compiled <code>TZif</code> "
    "binaries plus some metadata files. We can read those resources "
    "directly with <code>importlib.resources</code>."
)

# The full list of IANA keys lives in tzdata/zones as a newline-delimited file.
all_zones_text = resources.files("tzdata").joinpath("zones").read_text()
all_zones = [line for line in all_zones_text.splitlines() if line]

note(
    f"The bundled database contains <strong>{len(all_zones)}</strong> "
    f"IANA zone keys."
)

# Show a sample of African zones to give a feel for the naming.
african_zones = sorted(z for z in all_zones if z.startswith("Africa/"))
sample = ", ".join(f"<code>{z}</code>" for z in african_zones[:8])
note(f"First eight African zones: {sample}, ...")


def iana_key_to_resource(key):
    """Translate 'America/Indiana/Indianapolis' to (package, resource)."""
    package_loc, resource_name = key.rsplit("/", 1)
    package = "tzdata.zoneinfo." + package_loc.replace("/", ".")
    return package, resource_name


# Verify the magic bytes at the start of a TZif file.
package_name, resource_name = iana_key_to_resource("Europe/Berlin")
tzif_bytes = (
    resources.files(package_name).joinpath(resource_name).read_bytes()
)
note(
    f"<code>Europe/Berlin</code> lives at "
    f"<code>{package_name}/{resource_name}</code>, is "
    f"<strong>{len(tzif_bytes)}</strong> bytes long, and starts with "
    f"the magic bytes <code>{tzif_bytes[:4]!r}</code> "
    f"(every TZif file begins with <code>b'TZif'</code>)."
)

heading("Picking a zone dynamically")
note(
    "Because zone names are just strings, we can let users (or data) "
    "choose a zone at runtime. Here we pick a few historically "
    "interesting keys and print the current time in each."
)

interesting = [
    "Pacific/Kiritimati",   # UTC+14, the earliest local time on Earth
    "Asia/Kathmandu",       # UTC+05:45, an unusual 45-minute offset
    "Australia/Eucla",      # UTC+08:45
    "America/St_Johns",     # UTC-03:30 (or -02:30 in DST)
    "Antarctica/Troll",     # Switches between UTC and UTC+02
]

now_utc = datetime.now(ZoneInfo("UTC"))
rows = []
for key in interesting:
    local = now_utc.astimezone(ZoneInfo(key))
    rows.append(
        f"<tr><td><code>{key}</code></td>"
        f"<td>{local:%Y-%m-%d %H:%M}</td>"
        f"<td>UTC{local:%z}</td></tr>"
    )
display(HTML(
    "<table><thead><tr><th>Zone</th><th>Local time</th>"
    "<th>Offset</th></tr></thead><tbody>"
    + "".join(rows) + "</tbody></table>"
), append=True)
