# ---------------------------------------------------------------------
# Use xyzservices URLs to actually fetch and assemble a small basemap.
# ---------------------------------------------------------------------

heading("Stitching a basemap from XYZ tiles")
note(
    "We'll pick a token-free provider, ask xyzservices for tile "
    "URLs over a small grid, fetch each 256x256 PNG, and paste "
    "them into one image. This is the same idea libraries like "
    "<code>contextily</code> use under the hood."
)

# A clean, light basemap that doesn't need an API key.
provider = xyz.CartoDB.Positron
note(f"Using provider: <b>{provider.name}</b>")

# Pick a 3x3 grid of tiles at zoom 4 covering western Europe-ish.
zoom = 4
x_range = range(7, 10)
y_range = range(5, 8)

tile_size = 256
mosaic = Image.new(
    "RGB",
    (tile_size * len(x_range), tile_size * len(y_range)),
    "white",
)

# build_url is the right way to materialize a URL: it substitutes
# {x}/{y}/{z} plus any provider-specific bits like {r} or {s}.
fetched = 0
for ix, x in enumerate(x_range):
    for iy, y in enumerate(y_range):
        url = provider.build_url(x=x, y=y, z=zoom)
        response = requests.get(
            url,
            headers={"User-Agent": "xyzservices-pyscript-example"},
            timeout=10,
        )
        response.raise_for_status()
        tile = Image.open(io.BytesIO(response.content)).convert("RGB")
        mosaic.paste(tile, (ix * tile_size, iy * tile_size))
        fetched += 1

note(f"Fetched and stitched <strong>{fetched}</strong> tiles.")

fig, ax = plt.subplots(figsize=(6, 6))
ax.imshow(np.asarray(mosaic))
ax.set_xticks([])
ax.set_yticks([])
ax.set_title(f"{provider.name} @ z={zoom}")
fig.tight_layout()
display(fig, append=True)

# Always show the attribution -- it's required by most providers.
note(f"Tiles &copy; {provider.html_attribution}")
