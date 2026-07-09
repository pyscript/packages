"""
A first look at iniconfig: parsing a small INI file in memory.

iniconfig is a tiny, dependency-free parser that preserves the order
of sections and entries, supports `#` comments, and reports proper
line numbers on errors. See https://github.com/pytest-dev/iniconfig
for the source.

Normally you'd call `IniConfig("path/to/file.ini")`, which reads the
file from disk. We can also pass the source text directly using the
`data` argument, which is handy when the content lives in memory --
as it does here in the browser.
"""
from IPython.core.display import display, HTML

import iniconfig

heading("A made-up app config")
note(
    "Imagine the INI text below lives in <code>app.ini</code> on "
    "disk. We'll parse it and pull values out by section and key."
)

ini_source = """
# content of app.ini
[server]            # web server settings
host = localhost
port = 8080

[database]
url = sqlite:///app.db
pool_size = 5

[features]
# comma-separated flags, parsed below
enabled = search,export,dark_mode
"""

# Pass the source via `data=`; the first arg is just a label used in
# error messages.
config = iniconfig.IniConfig("app.ini", data=ini_source)

# Index a section like a dict, then index a key like a dict.
note(f"Server host: <code>{config['server']['host']}</code>")
note(f"Server port: <code>{config['server']['port']}</code>")
note(f"Database URL: <code>{config['database']['url']}</code>")

# `get` lets you supply a default and a converter function; perfect
# for splitting CSV-style values or coercing to int.
enabled = config.get(
    "features", "enabled", default=[], convert=lambda x: x.split(","),
)
pool = config.get("database", "pool_size", default=1, convert=int)

note(f"Enabled features: <code>{enabled}</code>")
note(f"Pool size (as int): <code>{pool}</code> (type: {type(pool).__name__})")

# `get` with a missing key returns the default rather than raising.
missing = config.get("server", "timeout", default=30, convert=int)
note(f"Missing key falls back to default: <code>{missing}</code>")
