"""
Generate per-package LLM prompts for creating PyScript examples.

Reads `api/all.json`, finds packages that are confirmed to work in
Pyodide and don't yet have examples, fetches each package's PyPI
metadata and (optionally) one supporting documentation page, then
writes a self-contained prompt plus reference attachments into
`prompts/<package>/`.

The prompts are designed to be sent to an LLM in a separate step
(see `apply_llm_response.py`). This script never calls an LLM
itself; it only assembles inputs.

Run with `--help` for usage. Typical flow:

    python generate_examples.py            # full pass, resumable
    python generate_examples.py --package Pillow --force  # one package
    python generate_examples.py --limit 5  # development run
"""

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin, urlparse

import requests


# Where things live, relative to the script's directory.
SCRIPT_DIR = Path(__file__).resolve().parent
ALL_JSON_PATH = SCRIPT_DIR / "api" / "all.json"
EXAMPLES_DIR = SCRIPT_DIR / "examples"
PROMPTS_DIR = SCRIPT_DIR / "prompts"
SHARED_DIR_NAME = "_shared"

# PyPI JSON API; gives us summary, project_urls and the long description.
PYPI_JSON_URL = "https://pypi.org/pypi/{name}/json"

# Cap each fetched document so prompts stay a sensible size.
MAX_DOC_BYTES = 200_000

# Be polite to PyPI and any doc hosts we hit.
REQUEST_TIMEOUT = 20
REQUEST_DELAY = 0.5
USER_AGENT = (
    "PyScript-example-generator/1.0 "
    "(+https://pyscript.net) requests"
)

# Keys in `project_urls` we'll consider for the optional extra page,
# in priority order. Matched case-insensitively as substrings.
DOC_URL_KEY_PRIORITIES = (
    "documentation",
    "docs",
    "tutorial",
    "quickstart",
    "getting started",
    "user guide",
    "guide",
    "homepage",
    "home",
)

# Keywords used when picking a tutorial-shaped link from a docs
# landing page. Deliberately distinct from DOC_URL_KEY_PRIORITIES:
# "documentation" and "docs" are useless here because every link on
# a docs site is documentation. The list below leads with the most
# specific onboarding terms and degrades to broader ones.
TUTORIAL_LINK_KEYWORDS = (
    "getting started",
    "getting-started",
    "quickstart",
    "quick start",
    "quick-start",
    "first steps",
    "first-steps",
    "tutorial",
    "introduction",
    "user guide",
    "user-guide",
    "guide",
    "examples",
)

# Hosts we skip for the extra page because the README already covers them.
SKIP_DOC_HOSTS = ("github.com", "gitlab.com", "bitbucket.org")

# Hostname patterns that strongly indicate a project's docs site. The
# signal we trust is the hostname, not arbitrary path components, to
# avoid false positives like a repo's `/docs/` directory on GitHub.
DOCS_HOST_PATTERNS = (
    "readthedocs.io",
    "readthedocs.org",
    "rtfd.io",
)
DOCS_HOST_PREFIXES = (
    "docs.",
    "documentation.",
    "doc.",
)

# Minimum useful README size. Below this we assume the README is a
# stub or placeholder and warrants the docs-fallback path.
MIN_README_LENGTH = 500

# A README qualifies as a changelog when its version-shaped headings
# dominate. We require at least this many such headings before we'd
# call it a changelog, to avoid mis-flagging short prose READMEs that
# happen to mention a release once.
MIN_VERSION_HEADINGS = 3


@dataclass
class DocStrategy:
    """Record of how we gathered documentation for a package.

    Captures the path taken so the prompt can be honest with the LLM
    about what context it's getting, and so a human reviewer can
    inspect `doc_strategy.json` and understand why a low-context
    package was flagged.
    """

    readme_used: bool = False
    readme_is_changelog: bool = False
    readme_too_short: bool = False
    docs_landing_url: str | None = None
    docs_landing_used: bool = False
    tutorial_url: str | None = None
    tutorial_used: bool = False
    extra_url: str | None = None
    extra_used: bool = False
    notes: list[str] = field(default_factory=list)

    @property
    def low_context(self) -> bool:
        """True when we couldn't attach any substantive docs."""
        return not (
            self.readme_used
            or self.tutorial_used
            or self.extra_used
            or self.docs_landing_used
        )


@dataclass
class PackageContext:
    """Everything we know about a single package, ready to render a prompt."""

    name: str
    summary: str
    pypi_url: str
    homepage: str | None
    source_url: str | None
    project_urls: dict[str, str]
    readme: str
    readme_content_type: str
    pyodide_versions: dict[str, dict[str, str]]
    extra_doc_url: str | None
    extra_doc_text: str | None
    doc_strategy: DocStrategy = field(default_factory=DocStrategy)


def load_all_json(path: Path) -> dict:
    """Read the master package index produced by the upstream tooling."""
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def packages_needing_examples(
    all_data: dict,
    examples_dir: Path,
) -> list[str]:
    """Pick green-status packages that don't yet have examples.

    Both inline examples in `all.json` and on-disk example directories
    are treated as authoritative, so either one is enough to skip a
    package.
    """
    out = []
    for name, entry in all_data.items():
        if entry.get("status") != "green":
            continue
        if entry.get("examples"):
            continue
        if (examples_dir / name).is_dir():
            continue
        out.append(name)
    out.sort(key=str.lower)
    return out


def fetch_pypi_metadata(
    name: str,
    cache_path: Path,
    session: requests.Session,
) -> dict:
    """Return the PyPI JSON payload for a package, caching to disk.

    Re-runs are common during development and PyPI shouldn't be
    hammered. Only the `info` block is retained; PyPI's full payload
    includes a `releases` history that can run to many megabytes for
    popular packages and we never read it.
    """
    if cache_path.exists():
        with cache_path.open(encoding="utf-8") as fh:
            return json.load(fh)
    url = PYPI_JSON_URL.format(name=name)
    response = session.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    payload = response.json()
    trimmed = {"info": payload.get("info", {}) or {}}
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with cache_path.open("w", encoding="utf-8") as fh:
        json.dump(trimmed, fh, indent=2)
    time.sleep(REQUEST_DELAY)
    return trimmed


def choose_extra_doc_url(
    project_urls: dict[str, str],
) -> str | None:
    """Pick a single useful documentation URL, or None.

    Code-host URLs are skipped because the PyPI README already covers
    that ground.
    """
    if not project_urls:
        return None
    lowered = {k.lower(): v for k, v in project_urls.items()}
    for keyword in DOC_URL_KEY_PRIORITIES:
        for key, url in lowered.items():
            if keyword in key and not _is_skipped_host(url):
                return url
    return None


def _is_skipped_host(url: str) -> bool:
    """True if the URL points at a code-hosting service we'd rather skip."""
    lowered = url.lower()
    return any(host in lowered for host in SKIP_DOC_HOSTS)


def looks_like_docs_host(url: str) -> bool:
    """True if the URL's hostname looks like a documentation site.

    We trust the hostname (`readthedocs.io`, `docs.*`, `documentation.*`)
    and deliberately ignore path-based hints like `/docs/`, which
    produce too many false positives on code-host URLs.
    """
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if not host:
        return False
    if any(pattern in host for pattern in DOCS_HOST_PATTERNS):
        return True
    if any(host.startswith(prefix) for prefix in DOCS_HOST_PREFIXES):
        return True
    return False


def find_docs_host_url(project_urls: dict[str, str]) -> str | None:
    """Return the first project URL whose hostname looks like docs."""
    for url in project_urls.values():
        if looks_like_docs_host(url):
            return url
    return None


def looks_like_changelog(text: str) -> bool:
    """True if a README looks like a changelog rather than real docs.

    A genuine changelog opens in one of two ways: with a version-
    shaped heading (`1.2.3`, `v1.0.0`), or with a titular heading
    like "Changelog" or "Release notes". A normal README that
    happens to include a release log at the end starts with prose
    section headings (`Installation`, `Usage`, `About`) instead. We
    require the first heading to match one of those patterns *and*
    version-shaped headings to dominate the rest, before we'll call
    a README a changelog.
    """
    headings = _collect_headings(text)
    if len(headings) < MIN_VERSION_HEADINGS:
        return False
    first = headings[0].strip().lower()
    if not (
        _looks_version_like(headings[0])
        or first in CHANGELOG_TITLE_HEADINGS
    ):
        return False
    version_like = sum(
        1 for h in headings if _looks_version_like(h)
    )
    if version_like < MIN_VERSION_HEADINGS:
        return False
    return version_like > len(headings) / 2


# Headings that, when they open a README, strongly suggest the whole
# document is a changelog. Lowercased for case-insensitive matching.
CHANGELOG_TITLE_HEADINGS = frozenset({
    "changelog",
    "change log",
    "changes",
    "release notes",
    "history",
    "revision history",
})


def _collect_headings(text: str) -> list[str]:
    """Extract heading text from a Markdown or reStructuredText README.

    Catches both ATX (`## title`) and Setext (`title\\n====`) styles,
    which between them cover almost all PyPI long descriptions.
    """
    headings: list[str] = []
    for match in re.finditer(
        r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", text, re.MULTILINE,
    ):
        headings.append(match.group(1).strip())
    setext = re.finditer(
        r"^([^\n]+?)\n[=\-~^]{3,}\s*$", text, re.MULTILINE,
    )
    for match in setext:
        title = match.group(1).strip()
        if title:
            headings.append(title)
    return headings


# A version heading typically contains digits separated by dots,
# possibly with a leading `v`, optional pre-release tags, and may be
# followed by a date or a parenthesised note.
_VERSION_HEADING_RE = re.compile(
    r"""^
    \s*
    v?\d+(?:\.\d+){1,3}      # 1.2, 1.2.3, 1.2.3.4
    (?:[-.][a-z0-9]+)*        # alpha/beta/rc1/dev
    \b
    """,
    re.IGNORECASE | re.VERBOSE,
)


def _looks_version_like(heading: str) -> bool:
    """True if a heading looks like a version number or release entry."""
    return bool(_VERSION_HEADING_RE.match(heading))


def extract_links(html: str, base_url: str) -> list[tuple[str, str]]:
    """Pull (url, text) pairs out of an HTML page, resolved against base.

    Returns absolute URLs only. Anchors with empty text are kept (the
    URL itself is sometimes the only signal). Crude regex parsing is
    fine for our purposes; we only need a passable list of candidate
    links.
    """
    links: list[tuple[str, str]] = []
    for match in re.finditer(
        r'<a\b[^>]*\bhref\s*=\s*["\']([^"\']+)["\'][^>]*>(.*?)</a>',
        html, re.IGNORECASE | re.DOTALL,
    ):
        href = match.group(1).strip()
        text = re.sub(r"<[^>]+>", " ", match.group(2))
        text = re.sub(r"\s+", " ", text).strip()
        absolute = urljoin(base_url, href)
        links.append((absolute, text))
    return links


def find_tutorial_link(
    links: list[tuple[str, str]],
    base_url: str,
) -> str | None:
    """Pick the best tutorial-shaped link from a docs landing page.

    Uses TUTORIAL_LINK_KEYWORDS rather than DOC_URL_KEY_PRIORITIES
    because the priorities differ: in `project_urls` we want a
    "Documentation" link first, but on a docs landing page that
    keyword matches the page's own title and beats more useful
    targets like "Tutorial" or "Getting started". Matches are
    restricted to the same host as the landing page, and we look in
    both link text and the URL's path so a `getting-started.html`
    link is found even when its anchor text is just "Read me".
    """
    base_host = (urlparse(base_url).hostname or "").lower()
    if not base_host:
        return None
    for keyword in TUTORIAL_LINK_KEYWORDS:
        for url, text in links:
            parsed = urlparse(url)
            if (parsed.hostname or "").lower() != base_host:
                continue
            haystack = f"{text.lower()} {parsed.path.lower()}"
            if keyword in haystack:
                return url
    return None


def gather_docs(
    project_urls: dict[str, str],
    readme: str,
    package_dir: Path,
    session: requests.Session,
) -> tuple[str | None, str | None, str | None, DocStrategy]:
    """Decide and fetch what documentation context to attach.

    Returns `(readme_to_use, extra_url, extra_text, strategy)`. The
    returned README is the raw text if it's substantive, or None if
    we judged it a changelog or too short. `extra_url` and
    `extra_text` describe the supporting page we managed to fetch
    (a tutorial, a docs landing page, or a project_urls fallback).
    """
    strategy = DocStrategy()
    readme_to_use: str | None = None
    if readme and len(readme) >= MIN_README_LENGTH:
        if looks_like_changelog(readme):
            strategy.readme_is_changelog = True
            strategy.notes.append(
                "README parsed as changelog; falling back to docs.",
            )
        else:
            readme_to_use = readme
            strategy.readme_used = True
    else:
        strategy.readme_too_short = True
        if readme:
            strategy.notes.append(
                "README is below the useful-length threshold.",
            )
        else:
            strategy.notes.append("No README provided on PyPI.")
    extra_url, extra_text = _gather_supporting_doc(
        project_urls=project_urls,
        package_dir=package_dir,
        session=session,
        strategy=strategy,
    )
    return readme_to_use, extra_url, extra_text, strategy


def _gather_supporting_doc(
    project_urls: dict[str, str],
    package_dir: Path,
    session: requests.Session,
    strategy: DocStrategy,
) -> tuple[str | None, str | None]:
    """Find and fetch a supporting documentation page.

    More context is better. We always try the docs-host path first,
    regardless of the state of the README, because a tutorial page
    complements a README rather than replacing it. If no docs-shaped
    host is available, or the docs-host walk produced nothing usable,
    we fall back to the existing project_urls heuristic so directly-
    provided tutorial URLs are still picked up.
    """
    docs_host_url = find_docs_host_url(project_urls)
    if docs_host_url:
        url, text = _try_tutorial_then_landing(
            docs_host_url=docs_host_url,
            package_dir=package_dir,
            session=session,
            strategy=strategy,
        )
        if url and text:
            return url, text
    fallback_urls = {
        k: v for k, v in project_urls.items() if v != docs_host_url
    }
    fallback_url = choose_extra_doc_url(fallback_urls)
    if not fallback_url:
        return None, None
    text = _fetch_doc_safely(
        fallback_url, package_dir / "doc.txt", session, strategy,
    )
    if not text:
        return None, None
    strategy.extra_url = fallback_url
    strategy.extra_used = True
    return fallback_url, text


def _try_tutorial_then_landing(
    docs_host_url: str,
    package_dir: Path,
    session: requests.Session,
    strategy: DocStrategy,
) -> tuple[str | None, str | None]:
    """Fetch a docs landing page and try to follow a tutorial link.

    Resolves any tutorial link against the page's *final* URL after
    redirects, not the URL we requested, so Sphinx-style relative
    hrefs on a redirected ReadTheDocs root resolve correctly.

    Falls back to returning the landing page itself if no tutorial
    link is found or the tutorial fetch fails.
    """
    landing = _fetch_landing_page(
        docs_host_url,
        package_dir / "doc_landing.html",
        session,
        strategy,
    )
    if landing is None:
        return None, None
    landing_html, landing_final_url = landing
    strategy.docs_landing_url = landing_final_url
    links = extract_links(landing_html, landing_final_url)
    tutorial_url = find_tutorial_link(links, landing_final_url)
    if tutorial_url:
        tutorial_text = _fetch_doc_safely(
            tutorial_url, package_dir / "doc.txt", session, strategy,
        )
        if tutorial_text:
            strategy.tutorial_url = tutorial_url
            strategy.tutorial_used = True
            return tutorial_url, tutorial_text
    landing_text = html_to_text(landing_html)
    landing_path = package_dir / "doc.txt"
    landing_path.write_text(landing_text, encoding="utf-8")
    strategy.docs_landing_used = True
    strategy.notes.append(
        "No tutorial link found; using docs landing page.",
    )
    return landing_final_url, landing_text


def _fetch_doc_safely(
    url: str,
    cache_path: Path,
    session: requests.Session,
    strategy: DocStrategy,
) -> str | None:
    """Wrap fetch_doc_page with error capture into the doc strategy."""
    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8")
    try:
        return fetch_doc_page(url, cache_path, session)
    except requests.RequestException as exc:
        strategy.notes.append(f"Fetch failed for {url}: {exc}")
        return None


def _fetch_landing_page(
    url: str,
    cache_path: Path,
    session: requests.Session,
    strategy: DocStrategy,
) -> tuple[str, str] | None:
    """Fetch a docs landing page as raw HTML, returning text and final URL.

    Returns `(html, final_url)` where `final_url` is the URL of the
    response after any redirects. Falls back to the cached `.url`
    sidecar file on cache reuse, and to the requested URL when no
    sidecar exists (which only happens for caches written by older
    versions of this script).
    """
    sidecar = cache_path.with_suffix(cache_path.suffix + ".url")
    if cache_path.exists():
        html = cache_path.read_text(encoding="utf-8")
        if sidecar.exists():
            final_url = sidecar.read_text(encoding="utf-8").strip()
        else:
            final_url = url
        return html, final_url
    try:
        return _fetch_html_raw(url, cache_path, session)
    except requests.RequestException as exc:
        strategy.notes.append(f"Fetch failed for {url}: {exc}")
        return None


def _fetch_html_raw(
    url: str,
    cache_path: Path,
    session: requests.Session,
) -> tuple[str | None, str]:
    """Fetch a URL and cache the raw HTML for link extraction.

    Returns `(text, final_url)`. `final_url` is the URL of the
    response after any redirects, which matters for resolving
    relative hrefs: ReadTheDocs serves the bare project root via a
    redirect to a versioned path like `/en/stable/`, and Sphinx-
    generated pages contain hrefs that are relative to that
    versioned path. Using the requested URL as the urljoin base
    produces broken links.

    The final URL is persisted alongside the cached HTML in a
    sibling `.url` file so cache reuse on a later run still has it.
    """
    headers = {"Accept": "text/html, */*"}
    response = session.get(
        url, timeout=REQUEST_TIMEOUT, headers=headers,
    )
    response.raise_for_status()
    raw = response.content[:MAX_DOC_BYTES]
    text = raw.decode("utf-8", errors="replace")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(text, encoding="utf-8")
    final_url = response.url or url
    cache_path.with_suffix(cache_path.suffix + ".url").write_text(
        final_url, encoding="utf-8",
    )
    time.sleep(REQUEST_DELAY)
    return text, final_url


def fetch_doc_page(
    url: str,
    cache_path: Path,
    session: requests.Session,
) -> str | None:
    """Download a doc page, cap its size, and cache the result.

    Returns plain text. HTML responses are reduced to their visible
    text via `html_to_text`.
    """
    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8")
    headers = {"Accept": "text/html, text/plain, text/markdown, */*"}
    response = session.get(url, timeout=REQUEST_TIMEOUT, headers=headers)
    response.raise_for_status()
    raw = response.content
    truncated = len(raw) > MAX_DOC_BYTES
    raw = raw[:MAX_DOC_BYTES]
    text = raw.decode("utf-8", errors="replace")
    content_type = response.headers.get("content-type", "")
    if "html" in content_type.lower():
        text = html_to_text(text)
    if truncated:
        text = text + "\n\n... [truncated]\n"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(text, encoding="utf-8")
    time.sleep(REQUEST_DELAY)
    return text


def html_to_text(html: str) -> str:
    """Strip HTML to a passable plain-text rendering.

    Intentionally crude. We drop script and style blocks, strip tags,
    and decode a handful of common entities. Anything more
    sophisticated would need a real parser.
    """
    html = re.sub(
        r"<script\b[^>]*>.*?</script>", " ", html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    html = re.sub(
        r"<style\b[^>]*>.*?</style>", " ", html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"&quot;", '"', text)
    text = re.sub(r"&#39;", "'", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    return text.strip()


def truncate_text(text: str, limit: int = MAX_DOC_BYTES) -> str:
    """Truncate by character count, marking the cut so callers can see it."""
    if len(text) <= limit:
        return text
    return text[:limit] + "\n\n... [truncated]\n"


def build_context(
    name: str,
    pypi_payload: dict,
    readme_to_use: str | None,
    extra_doc_url: str | None,
    extra_doc_text: str | None,
    pyodide_versions: dict[str, dict[str, str]],
    doc_strategy: DocStrategy | None = None,
) -> PackageContext:
    """Assemble a PackageContext from raw PyPI metadata and gathered docs.

    `readme_to_use` is the README we'll attach to the prompt, or None
    if it was judged a changelog or otherwise unhelpful. `doc_strategy`
    is carried through so the prompt rendering can be honest about
    what context was found.
    """
    info = pypi_payload.get("info", {}) or {}
    project_urls = info.get("project_urls") or {}
    homepage = info.get("home_page") or project_urls.get("Homepage")
    source = (
        project_urls.get("Source")
        or project_urls.get("Source Code")
        or project_urls.get("Repository")
    )
    return PackageContext(
        name=name,
        summary=info.get("summary") or "",
        pypi_url=f"https://pypi.org/project/{name}/",
        homepage=homepage,
        source_url=source,
        project_urls=project_urls,
        readme=truncate_text(readme_to_use) if readme_to_use else "",
        readme_content_type=info.get("description_content_type")
        or "text/plain",
        pyodide_versions=pyodide_versions,
        extra_doc_url=extra_doc_url,
        extra_doc_text=extra_doc_text,
        doc_strategy=doc_strategy or DocStrategy(),
    )


def render_prompt(ctx: PackageContext) -> str:
    """Compose the per-package prompt text.

    The shared system prompt and reference example are written once
    into `_shared/`; this prompt references them by relative path so
    the operator (or a wrapper script) can attach them when the LLM
    call is made.
    """
    parts: list[str] = []
    parts.append(f"# Generate PyScript examples for `{ctx.name}`\n")
    parts.append(
        "Read the shared instructions and the reference example "
        "attached to this prompt before generating output:\n\n"
        "- `_shared/system_prompt.md`: hard rules and output schema.\n"
        "- `_shared/setup_template.py`: the IPython shim used by the "
        "first example's `setup.py`.\n"
        "- `_shared/reference_example/`: a worked example for the "
        "`pandas` package, in the exact format you must produce.\n",
    )
    parts.append("\n## Package summary\n")
    parts.append(f"- PyPI distribution name: `{ctx.name}`\n")
    parts.append(f"- Summary: {ctx.summary or '(none provided)'}\n")
    parts.append(f"- PyPI page: {ctx.pypi_url}\n")
    if ctx.homepage:
        parts.append(f"- Homepage: {ctx.homepage}\n")
    if ctx.source_url:
        parts.append(f"- Source: {ctx.source_url}\n")
    if ctx.project_urls:
        parts.append("- Project URLs:\n")
        for key, url in ctx.project_urls.items():
            parts.append(f"    - {key}: {url}\n")
    if ctx.pyodide_versions:
        parts.append("- Pyodide availability:\n")
        for pyodide_v, info in sorted(ctx.pyodide_versions.items()):
            pkg_v = info.get("package_version", "?")
            parts.append(
                f"    - Pyodide {pyodide_v}: "
                f"{ctx.name} {pkg_v}\n",
            )
    if ctx.readme.strip():
        parts.append(
            "\n## PyPI README\n\n"
            f"Content type: `{ctx.readme_content_type}`.\n\n"
            "```\n"
            f"{ctx.readme.strip()}\n"
            "```\n",
        )
    if ctx.extra_doc_url and ctx.extra_doc_text:
        section_title = _doc_section_title(ctx.doc_strategy)
        parts.append(
            f"\n## {section_title}\n\n"
            f"Source: {ctx.extra_doc_url}\n\n"
            "```\n"
            f"{ctx.extra_doc_text.strip()}\n"
            "```\n",
        )
    if ctx.doc_strategy.low_context:
        parts.append(_low_context_addendum(ctx))
    parts.append("\n## Your task\n")
    parts.append(
        "Following the rules in `_shared/system_prompt.md` exactly, "
        "produce one or more PyScript examples for this package. "
        "Reply with a single JSON document matching the schema "
        "given in the system prompt and nothing else.\n",
    )
    return "".join(parts)


def _doc_section_title(strategy: DocStrategy) -> str:
    """Pick a section title that reflects what we actually fetched."""
    if strategy.tutorial_used:
        return "Tutorial / getting started"
    if strategy.docs_landing_used:
        return "Documentation landing page"
    return "Supporting documentation"


def _low_context_addendum(ctx: PackageContext) -> str:
    """Return prose to append when no useful docs were found.

    Tells the LLM honestly that we couldn't gather context, asks it
    to draw on its own knowledge of the package and any browsing
    tools available, and requires it to flag the example so a human
    reviewer notices.
    """
    return (
        "\n## No usable documentation found\n\n"
        "We were unable to gather usable documentation for this "
        "package. The README on PyPI was missing, too short, or "
        "appeared to be a changelog rather than real documentation, "
        "and we could not locate a tutorial or getting-started page "
        "from the project's URLs.\n\n"
        "Please draw on your own knowledge of "
        f"`{ctx.name}` (and any browsing tools available to you) to "
        "produce a sensible example that demonstrates the package's "
        "core idiomatic usage. If you genuinely don't recognise the "
        "package and have no way to look it up, produce a single "
        "minimal example that imports it and prints a short note "
        "saying that human review is needed.\n\n"
        "In the docstring at the top of the first example's "
        "`code.py`, include a single line that reads exactly:\n\n"
        "    NOTE: generated without project documentation; "
        "please review.\n\n"
        "This lets a human reviewer know to look at this example "
        "more carefully than usual.\n"
    )


def write_shared_assets(
    prompts_dir: Path,
    examples_dir: Path,
    force: bool = False,
) -> None:
    """Lay down the assets every prompt references. Idempotent."""
    shared = prompts_dir / SHARED_DIR_NAME
    shared.mkdir(parents=True, exist_ok=True)
    system_prompt_path = shared / "system_prompt.md"
    if force or not system_prompt_path.exists():
        system_prompt_path.write_text(SYSTEM_PROMPT, encoding="utf-8")
    setup_template_path = shared / "setup_template.py"
    if force or not setup_template_path.exists():
        setup_template_path.write_text(
            SETUP_TEMPLATE_PY, encoding="utf-8",
        )
    reference_src = examples_dir / "pandas"
    reference_dst = shared / "reference_example"
    if reference_src.is_dir():
        if force and reference_dst.exists():
            _rmtree(reference_dst)
        if not reference_dst.exists():
            _copytree(reference_src, reference_dst)


def _copytree(src: Path, dst: Path) -> None:
    """Minimal recursive copy, to avoid pulling in shutil for one call."""
    dst.mkdir(parents=True, exist_ok=True)
    for child in src.iterdir():
        target = dst / child.name
        if child.is_dir():
            _copytree(child, target)
        else:
            target.write_bytes(child.read_bytes())


def _rmtree(path: Path) -> None:
    """Minimal recursive delete, matching `_copytree`."""
    for child in path.iterdir():
        if child.is_dir():
            _rmtree(child)
        else:
            child.unlink()
    path.rmdir()


def process_package(
    name: str,
    entry: dict,
    prompts_dir: Path,
    session: requests.Session,
    force: bool = False,
) -> tuple[str, str]:
    """Generate the prompt and attachments for one package.

    Returns a `(status, message)` tuple where status is 'done',
    'skipped', or 'failed'. Failures are also recorded as a `.failed`
    marker file so a later pass can find and retry them.
    """
    package_dir = prompts_dir / name
    prompt_path = package_dir / "prompt.md"
    failed_path = package_dir / ".failed"
    if prompt_path.exists() and not force:
        return ("skipped", "prompt already exists")
    package_dir.mkdir(parents=True, exist_ok=True)
    if failed_path.exists():
        failed_path.unlink()
    try:
        pypi_payload = fetch_pypi_metadata(
            name, package_dir / "pypi.json", session,
        )
    except requests.HTTPError as exc:
        return _record_failure(
            failed_path,
            f"PyPI fetch failed: {exc}",
        )
    except requests.RequestException as exc:
        return _record_failure(
            failed_path,
            f"PyPI network error: {exc}",
        )
    info = pypi_payload.get("info", {}) or {}
    project_urls = info.get("project_urls") or {}
    raw_readme = info.get("description") or ""
    readme_path = package_dir / "readme.md"
    readme_path.write_text(raw_readme, encoding="utf-8")
    warning_path = package_dir / ".warning"
    if warning_path.exists():
        warning_path.unlink()
    readme_to_use, extra_url, extra_text, strategy = gather_docs(
        project_urls=project_urls,
        readme=raw_readme,
        package_dir=package_dir,
        session=session,
    )
    (package_dir / "doc_strategy.json").write_text(
        json.dumps(_strategy_to_dict(strategy), indent=2),
        encoding="utf-8",
    )
    ctx = build_context(
        name=name,
        pypi_payload=pypi_payload,
        readme_to_use=readme_to_use,
        extra_doc_url=extra_url,
        extra_doc_text=extra_text,
        pyodide_versions=entry.get("pyodide_versions") or {},
        doc_strategy=strategy,
    )
    prompt_path.write_text(render_prompt(ctx), encoding="utf-8")
    if strategy.low_context:
        warning_path.write_text(
            "low context: no usable README, tutorial, or docs page "
            "was found; the prompt asks the LLM to draw on its own "
            "knowledge of the package.\n",
            encoding="utf-8",
        )
        return ("warning", "prompt written (low context)")
    return ("done", "prompt written")


def _strategy_to_dict(strategy: DocStrategy) -> dict:
    """Serialize a DocStrategy as a small, inspectable JSON object."""
    return {
        "readme_used": strategy.readme_used,
        "readme_is_changelog": strategy.readme_is_changelog,
        "readme_too_short": strategy.readme_too_short,
        "docs_landing_url": strategy.docs_landing_url,
        "docs_landing_used": strategy.docs_landing_used,
        "tutorial_url": strategy.tutorial_url,
        "tutorial_used": strategy.tutorial_used,
        "extra_url": strategy.extra_url,
        "extra_used": strategy.extra_used,
        "low_context": strategy.low_context,
        "notes": list(strategy.notes),
    }


def _record_failure(failed_path: Path, message: str) -> tuple[str, str]:
    """Persist a failure marker so a later pass can find and retry it."""
    failed_path.write_text(message + "\n", encoding="utf-8")
    return ("failed", message)


def write_manifest(
    prompts_dir: Path,
    results: list[tuple[str, str, str]],
) -> None:
    """Summarize the run for downstream tooling and humans."""
    manifest = {
        "packages": [
            {"name": name, "status": status, "message": message}
            for name, status, message in results
        ],
    }
    (prompts_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8",
    )


def make_session() -> requests.Session:
    """Build a `requests.Session` with a courteous User-Agent header."""
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    return session


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    """Parse the command-line interface for one-off and batch use."""
    parser = argparse.ArgumentParser(
        description=(
            "Generate per-package LLM prompts for PyScript examples."
        ),
    )
    parser.add_argument(
        "--package",
        action="append",
        default=None,
        help=(
            "Process only this package (may be given more than once). "
            "Default: process all green packages without examples."
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Stop after processing this many packages.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Re-generate prompts even if they already exist on disk."
        ),
    )
    parser.add_argument(
        "--all-json",
        type=Path,
        default=ALL_JSON_PATH,
        help=f"Path to all.json (default: {ALL_JSON_PATH}).",
    )
    parser.add_argument(
        "--examples-dir",
        type=Path,
        default=EXAMPLES_DIR,
        help=f"Existing examples dir (default: {EXAMPLES_DIR}).",
    )
    parser.add_argument(
        "--prompts-dir",
        type=Path,
        default=PROMPTS_DIR,
        help=f"Output directory (default: {PROMPTS_DIR}).",
    )
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] | None = None) -> int:
    """Entry point. Returns a process exit code."""
    args = parse_args(argv if argv is not None else sys.argv[1:])
    all_data = load_all_json(args.all_json)
    if args.package:
        targets = []
        for name in args.package:
            if name not in all_data:
                print(
                    f"Unknown package: {name}", file=sys.stderr,
                )
                return 2
            targets.append(name)
    else:
        targets = packages_needing_examples(
            all_data, args.examples_dir,
        )
    if args.limit is not None:
        targets = targets[: args.limit]
    args.prompts_dir.mkdir(parents=True, exist_ok=True)
    write_shared_assets(
        args.prompts_dir, args.examples_dir, force=args.force,
    )
    session = make_session()
    results: list[tuple[str, str, str]] = []
    for index, name in enumerate(targets, start=1):
        status, message = process_package(
            name=name,
            entry=all_data[name],
            prompts_dir=args.prompts_dir,
            session=session,
            force=args.force,
        )
        print(
            f"[{index}/{len(targets)}] {name}: {status} -- {message}",
        )
        results.append((name, status, message))
    write_manifest(args.prompts_dir, results)
    failed = sum(1 for _, status, _ in results if status == "failed")
    warnings = sum(
        1 for _, status, _ in results if status == "warning"
    )
    if warnings:
        print(
            f"{warnings} package(s) flagged as low-context; "
            "see .warning markers and doc_strategy.json files.",
        )
    return 1 if failed else 0


# ---------------------------------------------------------------------
# Bundled prompt templates. Kept as module-level constants so they
# travel with the script and can be overridden by writing into
# `prompts/_shared/` ahead of a run.
# ---------------------------------------------------------------------


SYSTEM_PROMPT = """\
# System prompt: PyScript example generator

You are generating short, illustrative usage examples for a single
Python package, to run in PyScript via Pyodide. The examples will be
shown in a user-facing PyScript IDE. Each example must also work,
unmodified, when copied into successive cells of a Jupyter notebook.
Use `#` comments and docstrings to explain the code, but avoid any prose
outside of these comments and docstrings. When naming things, prefer
clarity, meaningfulness, and descriptiveness over cleverness or brevity.

You should assume the user has no prior knowledge of the package, and has
some Python experience. Your examples should be concise and
focus on the most important aspects and idioms of the package without
straying into unnecessary complexity of explanation of Python itself.

Your tone should be friendly and approachable, like a helpful mentor
writing a tutorial for a colleague. Avoid being overly formal or verbose.
Use clear, simple language and focus on practical usage. Comments and
docstrings should be in US English. Use the same style and conventions
as the reference example provided. Follow the patterns in that example
closely, especially for setup.py and how you use the display function
to show output.

Most importantly, the examples should take the reader on a journey from
a simple onboarding example to slightly more involved usage, without
repeating the same ground. Each example should introduce a new technique
or pattern without re-importing or re-defining things that the first
example established. The first example's setup.py should include the
full IPython shim and all imports, while later examples' setup.py should
only set up the same names without the shim. If helpful, include URLs
to the package's documentation or source code in comments, but don't
mention any limitations of the PyScript environment or the fact that
these examples are generated by an LLM.

## Required output

Reply with a single TOML document and nothing else (no Markdown
fences around the whole document, no preamble, no commentary).
TOML's literal multi-line strings (delimited by `'''`) pass content
through verbatim with no escaping required, which is why we use this
format: your `code.py` and `setup.py` go in as raw Python source,
including triple-quoted docstrings, backslashes, and quotes.

The format:

```toml
package = "<distribution name as given>"

[[example]]
dir_name = "<snake_case_ascii>"
title = "<human-readable title>"
config = '''
<verbatim contents of config.toml>
'''
setup = '''
<verbatim contents of setup.py>
'''
code = '''
<verbatim contents of code.py>
'''

[[example]]
dir_name = "<snake_case_ascii>"
title = "<human-readable title>"
config = '''
...
'''
setup = '''
...
'''
code = '''
...
'''

(... and so on for each example)
```

Rules for the format:

- The order of `[[example]]` blocks defines the display order of the
  examples. The first one is the onboarding example.
- Use TOML's literal multi-line string syntax (three single quotes)
  for the `config`, `setup`, and `code` fields. NOT three double
  quotes -- TOML's basic multi-line strings (`\"\"\"...\"\"\"`) require
  escaping, which we want to avoid.
- Inside the `'''...'''` blocks: do NOT escape anything. Triple-quoted
  Python strings, raw newlines, backslashes, and double-quotes all go
  through as-is.
- For triple-quoted strings INSIDE your Python code (docstrings,
  multi-line strings), use `\"\"\"` -- never `'''`. The `'''` characters
  are reserved as the TOML string delimiters; using them inside your
  Python source would prematurely terminate the TOML string.
- `dir_name` must be lowercase ASCII, words separated by single
  underscores, no leading digits, no trailing underscores.

Before you reply: confirm to yourself that the document parses as
TOML and that the `setup` and `code` strings each parse as valid
Python. If either fails, fix the source and check again. Do not
reply with output that has not passed both checks.

A complete worked example for a fictional package called `widget`:

```toml
package = "widget"

[[example]]
dir_name = "hello_widget"
title = "Hello, Widget"
config = '''
packages = ["widget"]
'''
setup = '''
\"\"\"Shim setup for the first example. Includes the full IPython shim.\"\"\"
import sys
import types
import js
from pyscript import window, HTML, display as _display

js.alert = window.alert


def display(*args, **kwargs):
    return _display(
        *args, **kwargs, target=__pyscript_display_target__,
    )


# (... the rest of the IPython shim, exactly as in the reference ...)


from widget import Widget


def heading(text, level=2):
    display(HTML(f"<h{level}>{text}</h{level}>"), append=True)


def note(text):
    display(HTML(f"<p>{text}</p>"), append=True)
'''
code = '''
\"\"\"A first look at the widget package.\"\"\"
from IPython.core.display import display, HTML

w = Widget("hello")
heading("A widget says hello")
note(f"Widget greeting: {w.greet()}")
'''
```

## How many examples

Produce 1 to 3 examples. Use your judgment based on the package's
surface area:

- A tiny utility (think: a string transformer) gets one short
  example. Don't pad.
- A package with several distinct idiomatic patterns gets two or
  three examples that progress from simple onboarding to slightly
  more involved usage.

By the end of the last example, the reader should have a good sense of
how to use the package and be primed to explore further.

## The notebook-cell rule (very important)

Picture the examples as successive cells in a single Jupyter
notebook:

- Cell 1 (the first example) is the top of the notebook. Its
  `code.py` MUST `import` the package(s) it uses, and it MUST include
  `from IPython.core.display import display, HTML`. It may use
  `display(...)` and `HTML(...)` and any helpers it defines.
- Cells 2+ inherit the namespace from cell 1. Their `code.py` MUST
  NOT re-import anything that cell 1 imported, and MUST NOT
  re-define helpers like `heading`, `note`, or `display`. They use
  those names directly, as a notebook cell would.

PyScript runs each example in a fresh execution context, so we
compensate using `setup.py`:

- The first example's `setup.py` MUST be the full IPython shim plus
  all package imports the example uses, plus `heading`, `note`, the
  `display` override, and `rng` if you use NumPy randomness. Use the
  contents of `_shared/setup_template.py` as the starting point and
  append ONLY the example's package imports and any new
  package-specific helpers (such as `rng = np.random.default_rng(0)`,
  or a domain-specific helper your example needs). The template
  already defines `display`, `heading`, and `note` -- do NOT redefine
  them; doing so silently overrides the template's versions and is a
  recurring source of bugs.
- The setup.py for examples 2 and onwards MUST set up the same names
  that cell 1 established, but WITHOUT the IPython shim. The package
  imports, `display` override, `heading`, `note`, and any RNG go
  directly in this lighter setup. See `_shared/reference_example/`
  cells 2 and 3 for the pattern.

CRITICAL: examples 2+ MUST NOT import from `IPython` anywhere -- not
in `setup.py`, not in `code.py`. The IPython shim is only registered
in the first example's `setup.py`. In examples 2+, `display` and
`HTML` are defined directly: `display` is a thin wrapper around
`pyscript.display` (see the reference example's later cells), and
`HTML` is imported from `pyscript` (`from pyscript import HTML`).
Any line containing `from IPython` or `import IPython` in examples
2+ is a bug and will break the example at runtime.

## Example content rules

- The first example must actually `import` the target package and use
  it. The package name on PyPI may differ from the import name (for
  example, `Pillow` is imported as `PIL`). Use the correct import
  name. Subsequent examples must also use the target package (every
  example demonstrates the package, not its dependencies) but they
  must NOT re-import it in `code.py`; the import goes in their
  `setup.py` and the example uses the package as if it were a later
  cell of the same notebook. Subsequent examples may also introduce
  a second package if it's a common companion to the first (for
  example, `matplotlib` for plotting or `numpy` for arrays), but
  don't introduce a new package in each example just for the sake
  of it.
- Every `config.toml` must list the PyPI distribution name (the one
  given in the prompt) plus any other Pyodide-supported packages the
  example uses (commonly `matplotlib` for plots, `numpy` for
  arrays).
- Use meaningful synthetic data with a small story (an inventory, daily
  readings, a tiny corpus). Avoid `[1, 2, 3]` filler.
- Use US English in docstrings and comments.
- Display output via `display(...)` and `HTML(...)` (the helpers
  `heading(text)` and `note(text)` are available; prefer them over
  raw HTML for section breaks and explanatory prose).
- For plots: `import matplotlib.pyplot as plt`, build a `fig`, call
  `display(fig, append=True)`. Don't call `plt.show()`.
- Keep each `code.py` under roughly 80 lines. Lines should fit
  comfortably under 100 characters.
- Only the first example carries a module-level docstring at the
  top of `code.py`. Later examples open with a section comment
  (see the reference example).
- Do not use packages that aren't in the example's `config.toml`.
- Do not use network access, or anything that would fail in a 
  sandboxed browser environment.

## Picking what to demonstrate

The README and supporting documentation supplied with this prompt
may contain lots of unnecessary information: changelogs, installation
instructions, environment-specific notes, and so on. Your job is to
sift through it and find the core idiomatic patterns that a user
would need to know to get started and be productive with this package.
If you already have knowledge of the package, feel free
to use this knowledge to enhance the examples in a way that
complements our aim of understandability and approachability for new
users. However, do not hallucinate features or usage patterns that
are not actually present in the package or its documentation. If
you want to draw on your own knowledge of the package, make sure it's
accurate and grounded in the actual package and its docs.

Use the README and any supporting documentation supplied with this
prompt to identify the package's core idiomatic patterns. Lead with
the most common, simplest use case that illustrates the package's
purpose and valuable use-case. Focus on real world human intent in
your examples to give context and then illustrate with technical
examples that build from the intent. Try to make names and data
meaningful and memorable, to help the reader build a mental model
of the package's capabilities and how it might fit into their work.

If you add a second or third example, each should introduce a new
technique without re-treading ground from the first.

If the package's "happy path" depends on a feature that won't work
in Pyodide (access to the user's local file system, sockets, native
subprocess, threads, GPU, GUI), pick an alternative path that does
work, and don't mention the limitation in the example itself.
"""


SETUP_TEMPLATE_PY = '''\
"""
Shim IPython's display API onto PyScript so example code written in a
Jupyter/IPython idiom runs unmodified in the browser.

After this module executes, both of the following imports work in
example code and resolve to the PyScript equivalents:

    from IPython.core.display import display, HTML
    from IPython.display import display, HTML
"""

import sys
import types
import js
from pyscript import window, HTML, display as _display

# Make the standard JavaScript alert function available as js.alert
# because this code is run in a web worker (where alert is not
# available).
js.alert = window.alert


def display(*args, **kwargs):
    """Wrap pyscript.display so output lands in the example target."""
    return _display(
        *args, **kwargs, target=__pyscript_display_target__,
    )


# Build a minimal IPython package tree and register it in sys.modules
# so the canonical import paths resolve to PyScript's display API.
ipython = types.ModuleType("IPython")
core = types.ModuleType("IPython.core")
core_display = types.ModuleType("IPython.core.display")
core_display.display = display
core_display.HTML = HTML
ipython.core = core
core.display = core_display
# Some libraries probe for IPython via
# `sys.modules.get("IPython").get_ipython()`. Returning None keeps
# them happy without us having to fake a shell.
ipython.get_ipython = lambda: None
ipython.display = core_display
sys.modules["IPython"] = ipython
sys.modules["IPython.core"] = core
sys.modules["IPython.core.display"] = core_display
sys.modules["IPython.display"] = core_display


def heading(text, level=2):
    """Emit an HTML heading so sections are visually separated."""
    display(HTML(f"<h{level}>{text}</h{level}>"), append=True)


def note(text):
    """Emit a short paragraph of explanatory prose."""
    display(HTML(f"<p>{text}</p>"), append=True)


# Append your example's package imports below this line. Do NOT
# redefine `display`, `heading`, or `note`; they are already in
# scope from the template above. If your example uses NumPy
# randomness, also append something like:
#     rng = np.random.default_rng(0)
'''


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())