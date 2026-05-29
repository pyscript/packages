# Generate a batch of memorable codenames for a fleet of objects --
# servers, experiments, build artifacts, support tickets, anything
# you'd otherwise label with an opaque UUID.

heading("Codenames for a fleet of servers")
note(
    "We mint a 2-word internal nickname and a longer 4-word public "
    "slug for each of ten servers. The short nickname is friendly "
    "to type; the long slug is unique enough to use as an ID."
)

fleet_size = 10
servers = []
for server_number in range(1, fleet_size + 1):
    nickname = generate_slug(2)
    public_slug = generate_slug(4)
    servers.append((server_number, nickname, public_slug))

# Render as an HTML table so the pairing is easy to scan.
rows = "".join(
    f"<tr><td>{n:02d}</td><td><code>{nick}</code></td>"
    f"<td><code>{slug}</code></td></tr>"
    for n, nick, slug in servers
)
table = (
    "<table style='border-collapse:collapse'>"
    "<thead><tr>"
    "<th style='text-align:left;padding:4px 12px'>#</th>"
    "<th style='text-align:left;padding:4px 12px'>Nickname</th>"
    "<th style='text-align:left;padding:4px 12px'>Public slug</th>"
    "</tr></thead>"
    f"<tbody>{rows}</tbody></table>"
)
display(HTML(table), append=True)

# A quick sanity check: are the long slugs actually unique in this batch?
unique_slugs = {slug for _, _, slug in servers}
note(
    f"Unique 4-word slugs in this batch: "
    f"<strong>{len(unique_slugs)} / {fleet_size}</strong>."
)
