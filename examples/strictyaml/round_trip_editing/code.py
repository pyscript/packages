# ---------------------------------------------------------------------
# Editing a YAML document while keeping comments and formatting intact.
# ---------------------------------------------------------------------

heading("Round-tripping a config file")
note(
    "A common task: load a config, change a value or two, then write "
    "it back out without losing the human-friendly comments. "
    "strictyaml preserves comments and key ordering on round-trip."
)

server_yaml = """
# Production server settings
host: example.com
port: 8080
# Toggle to false during scheduled maintenance
enabled: true
admins:
  - alice@example.com
  - bob@example.com
"""

server_schema = Map({
    "host": Str(),
    "port": Int(),
    "enabled": Bool(),
    "admins": Seq(Str()),
})

config = load(server_yaml, server_schema)

note("Loaded config (typed):")
display(config.data, append=True)

# Mutate a couple of values and append to a sequence.
config["port"] = 9090
config["enabled"] = False
config["admins"].data.append("carol@example.com")

# strictyaml accepts native Python values when the schema knows the type;
# for sequences, the cleanest approach is to rebuild from a list:
config["admins"] = ["alice@example.com", "bob@example.com", "carol@example.com"]

heading("After editing — comments survive!")
display(HTML(f"<pre>{config.as_yaml()}</pre>"), append=True)

heading("Bonus: line numbers for free")
note(
    "Every parsed node remembers where it came from, which is "
    "handy when reporting issues back to the user."
)
for i, admin in enumerate(config["admins"]):
    note(
        f"<code>admins[{i}]</code> = "
        f"<strong>{admin.data}</strong> (line {admin.start_line})"
    )
