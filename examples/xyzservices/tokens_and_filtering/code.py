# ---------------------------------------------------------------------
# Filtering the catalog and handling providers that need API tokens.
# ---------------------------------------------------------------------

import xyzservices
import xyzservices.providers as xyz


heading("Which providers are free to use right now?")
note(
    "Some providers (Mapbox, Thunderforest, Stadia, ...) require an "
    "API key. <code>requires_token()</code> tells you whether a "
    "<code>TileProvider</code> still has unfilled placeholders like "
    "<code>&lt;insert your access token here&gt;</code>."
)

# `xyz.flatten()` walks the nested Bunch and yields a flat dict of
# {dotted_name: TileProvider}. Perfect for filtering.
all_providers = xyz.flatten()
note(f"Total tile provider entries: <strong>{len(all_providers)}</strong>")

token_free = {
    name: tp for name, tp in all_providers.items()
    if not tp.requires_token()
}
needs_token = {
    name: tp for name, tp in all_providers.items()
    if tp.requires_token()
}

note(
    f"Free out of the box: <strong>{len(token_free)}</strong>. "
    f"Need an API key: <strong>{len(needs_token)}</strong>."
)

# Show a handful of providers that need a token, so you know what to
# look out for.
sample_locked = list(needs_token.keys())[:6]
display(HTML(
    "<b>Examples requiring a token:</b><ul>"
    + "".join(f"<li>{n}</li>" for n in sample_locked)
    + "</ul>"
), append=True)

heading("Supplying a token", level=3)
note(
    "TileProviders are dict-like, so you fill in placeholders by "
    "assignment. Below we plug a fake token into a copy of the "
    "Stadia AlidadeSmooth provider; in real use you'd paste your "
    "own key."
)

stadia = xyz.Stadia.AlidadeSmooth.copy()
note(f"Before: requires_token() = <b>{stadia.requires_token()}</b>")
stadia["api_key"] = "my-fake-token-1234"
note(f"After:  requires_token() = <b>{stadia.requires_token()}</b>")

# Once the token is set, build_url returns a fully usable URL.
example_url = stadia.build_url(x=8, y=5, z=4)
display(HTML(f"<code>{example_url}</code>"), append=True)

heading("Searching by attribution", level=3)
note("Find every OpenStreetMap-derived provider in the catalog:")

osm_based = sorted(
    name for name, tp in all_providers.items()
    if "OpenStreetMap" in tp.get("attribution", "")
)
note(f"Matches: <strong>{len(osm_based)}</strong>. First ten:")
display(HTML("<ol>" + "".join(f"<li>{n}</li>" for n in osm_based[:10])
             + "</ol>"), append=True)
