"""
A first look at propcache.

`propcache.api.cached_property` works just like the standard library's
`functools.cached_property`: the decorated method runs once per
instance, and its result is then stored on the instance and returned
directly on subsequent accesses. propcache is a faster, C-accelerated
implementation aimed at hot code paths.

See https://propcache.readthedocs.io for full documentation.
"""
from IPython.core.display import display, HTML

heading("A weather station with an expensive computation")
note(
    "Imagine each `WeatherStation` reads many raw temperature samples "
    "and we want a daily average. The average never changes for a "
    "given station, so we cache it the first time it's asked for."
)


class WeatherStation:
    """A station whose daily average is computed at most once."""

    def __init__(self, name, samples):
        self.name = name
        self.samples = samples
        self.compute_count = 0

    @cached_property
    def daily_average(self):
        """Pretend this is an expensive aggregation over many samples."""
        self.compute_count += 1
        return sum(self.samples) / len(self.samples)


station = WeatherStation(
    "Reykjavik",
    samples=[1.2, 0.8, -0.4, 2.1, 3.0, 1.7, 0.9, -0.2, 1.5, 2.4],
)

note("First access computes the value:")
display(f"daily_average = {station.daily_average:.2f}")
display(f"compute_count = {station.compute_count}")

note("Subsequent accesses return the cached value without recomputing:")
for _ in range(5):
    _ = station.daily_average
display(f"compute_count after 5 more reads = {station.compute_count}")

note(
    "The cached value lives in the instance's <code>__dict__</code>, "
    "so deleting it forces the next access to recompute."
)
del station.__dict__["daily_average"]
_ = station.daily_average
display(f"compute_count after cache invalidation = {station.compute_count}")
