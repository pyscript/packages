# A small "ship's log": a list of plain English entries we want to
# rewrite in Pirate-ish, side by side, as a little table.

heading("The captain's log, before and after")
note(
    "We feed each log entry through arrr.translate and show the "
    "original alongside its piratical counterpart. Reload the page "
    "to see different interjections from the crew."
)

log_entries = [
    "Today we set sail at dawn from the harbour.",
    "The cook prepared a fine stew for dinner.",
    "We spotted another ship on the horizon.",
    "My friend tells me the weather will turn soon.",
    "Hello to all the family back home.",
]

# Build a simple HTML table of English -> Pirate-ish.
rows = ["<tr><th>English</th><th>Pirate-ish</th></tr>"]
for entry in log_entries:
    pirate = translate(entry)
    rows.append(
        f"<tr><td>{entry}</td><td><em>{pirate}</em></td></tr>"
    )

table_html = (
    "<table border='1' cellpadding='6' "
    "style='border-collapse: collapse'>"
    + "".join(rows)
    + "</table>"
)
display(HTML(table_html), append=True)

# A handy one-liner: translate any longer passage in a single call.
heading("A longer passage, translated in one go")

passage = (
    "My name is Alex and I am a friend of the captain. "
    "We are looking for treasure and adventure on the high seas. "
    "Please tell my family that I am safe and having a wonderful time."
)
note("Original:")
display(HTML(f"<blockquote>{passage}</blockquote>"), append=True)
note("Pirate-ish:")
display(HTML(f"<blockquote>{translate(passage)}</blockquote>"), append=True)
