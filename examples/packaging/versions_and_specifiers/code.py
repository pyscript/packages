"""
A first look at the `packaging` library.

`packaging` is the canonical implementation of Python packaging
interoperability standards (PEP 440, PEP 508, PEP 425, and friends).
If you have ever wondered how pip decides whether "1.10.0" is newer
than "1.9.0", or whether "2.0.0rc1" satisfies ">=2,<3", this is the
library doing the work.

Docs: https://packaging.pypa.io/
"""
import pandas as pd
from IPython.core.display import display, HTML

heading("Parsing and comparing versions")
note(
    "PEP 440 says version strings have a precise structure: an "
    "optional epoch, a release segment, and pre/post/dev tags. "
    "<code>Version</code> parses them and compares them correctly, "
    "even when string ordering would get it wrong."
)

raw_versions = [
    "1.0",
    "1.0.0",
    "1.0.1",
    "1.0a1",       # alpha pre-release
    "1.0rc2",      # release candidate
    "1.0.post1",   # post-release
    "1.0.dev3",    # development release
    "2!1.0",       # epoch 2 -- jumps ahead of any non-epoch version
    "1.10",        # newer than 1.9, despite shorter string sort
]

parsed = [Version(v) for v in raw_versions]
ordered = sorted(parsed)

table = pd.DataFrame({
    "version": [str(v) for v in ordered],
    "is_prerelease": [v.is_prerelease for v in ordered],
    "is_postrelease": [v.is_postrelease for v in ordered],
    "release_tuple": [v.release for v in ordered],
})
note("Sorted from oldest to newest by PEP 440 rules:")
display(table, append=True)

# Invalid versions raise a clear exception.
try:
    Version("not-a-version")
except InvalidVersion as exc:
    note(f"<code>Version('not-a-version')</code> raises: <em>{exc}</em>")


heading("Matching versions against a specifier")
note(
    "A <code>SpecifierSet</code> is the comma-separated constraint "
    "you write in a requirements file, like <code>&gt;=1.0,&lt;2</code>. "
    "By default it excludes pre-releases unless you opt in."
)

constraint = SpecifierSet(">=1.0,<2")
candidates = ["0.9", "1.0", "1.0rc2", "1.5", "1.99", "2.0", "2!1.0"]

rows = []
for raw in candidates:
    v = Version(raw)
    rows.append({
        "candidate": raw,
        f"matches '{constraint}'": v in constraint,
        "matches (with prereleases)": constraint.contains(
            v, prereleases=True,
        ),
    })
display(pd.DataFrame(rows), append=True)

note(
    "Notice <code>1.0rc2</code> only matches when pre-releases are "
    "allowed, and the epoch-bumped <code>2!1.0</code> sorts above "
    "<code>2.0</code> so it falls outside the upper bound."
)
