# ---------------------------------------------------------------------
# Persistent collections: Deque (like collections.deque) and Index
# (like dict). Both survive process restarts and are safe to share
# across processes.
# ---------------------------------------------------------------------

heading("A persistent work queue with Deque")
note(
    "<code>diskcache.Deque</code> is a drop-in replacement for "
    "<code>collections.deque</code> that's backed by disk. Producers "
    "and consumers in different processes can share the same queue."
)

jobs = dc.Deque(directory="/tmp/job_queue")
jobs.clear()

# Producer side: push some work.
for url in ["/index", "/about", "/pricing", "/contact", "/blog"]:
    jobs.append({"url": url, "attempts": 0})

note(f"Queued <strong>{len(jobs)}</strong> jobs.")

# Consumer side: pop and process from the left (FIFO).
processed = []
while jobs:
    job = jobs.popleft()
    processed.append(job["url"])

note(
    "Processed in order: "
    + ", ".join(f"<code>{u}</code>" for u in processed)
)

heading("A persistent dictionary with Index")
note(
    "<code>diskcache.Index</code> is an ordered, persistent mapping. "
    "Use it whenever you'd reach for a dict but want the contents to "
    "outlive the process."
)

settings = dc.Index("/tmp/user_settings")
settings.clear()

settings["theme"] = "dark"
settings["font_size"] = 14
settings["recent_files"] = ["notes.md", "todo.txt"]

# Mapping protocol: iterate, look up, update, delete.
settings.update({"font_size": 16, "autosave": True})
del settings["recent_files"]

rows = "".join(
    f"<tr><td><code>{k}</code></td><td><code>{v!r}</code></td></tr>"
    for k, v in settings.items()
)
display(HTML(
    "<table border='1' cellpadding='4' style='border-collapse:collapse'>"
    "<tr><th>key</th><th>value</th></tr>" + rows + "</table>"
), append=True)

note(
    "If you reopened <code>Index('/tmp/user_settings')</code> in a "
    "fresh Python process, you'd find these same values waiting for you."
)
