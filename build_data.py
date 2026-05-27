"""
Build the static JSON data files used by the package support detail
page in the PyScript documentation site.

This script is run occasionally, by hand, to refresh the curated data.
A manual step is required by design: the website is advertised as
"curated", so a human reviews the changes (via a git PR) before they
go live.

It runs four steps in order:

1. Apply community-contributed status updates. These arrive via a
   Google Form, published as a CSV. Updates newer than the last run
   override the generated per-package data.

2. Generate per-package JSON from the Pyodide support graph. For each
   package, record which Pyodide (and matching PyScript) releases ship
   it, fetch a PyPI summary, and write `api/package/<name>.json`. A
   file whose versions and examples are unchanged is left alone so we
   never clobber a community contribution.

3. Generate `api/top_100_pypi_packages.json`: the top 100 PyPI
   packages by download count, annotated with Pyodide support status.

4. Record the run time and write the aggregate files: `api/all.json`
   (every package) and `api/examples.json` (packages that have
   examples).

Run with `--help` for options. The script always runs all four steps.
"""

import argparse
import csv
import datetime
import json
import sys
import tomllib
from io import StringIO
from pathlib import Path
from typing import Callable, Iterable

import requests


# Maps each PyScript release to the Pyodide release it bundles. The
# inverse lets us label a Pyodide release with the PyScript release a
# reader would actually pin.
PYSCRIPT_PYODIDE_MAP = {
    "2024.10.1": "0.26.2",
    "2024.10.2": "0.26.3",
    "2024.11.1": "0.26.4",
    "2025.2.1": "0.26.4",
    "2025.2.2": "0.27.2",
    "2025.2.3": "0.27.2",
    "2025.2.4": "0.27.2",
    "2025.3.1": "0.27.3",
    "2025.5.1": "0.27.6",
    "2025.7.1": "0.27.7",
    "2025.7.2": "0.27.7",
    "2025.7.3": "0.27.7",
    "2025.8.1": "0.28.1",
    "2025.10.1": "0.29.0",
    "2025.10.2": "0.29.0",
    "2025.10.3": "0.29.0",
    "2025.11.1": "0.29.0",
    "2026.1.1": "0.29.1",
    "2026.2.1": "0.29.3",
    "2026.3.1": "0.29.3",
}

PYODIDE_PYSCRIPT_MAP = {
    pyodide: pyscript
    for pyscript, pyodide in PYSCRIPT_PYODIDE_MAP.items()
}

# Remote data sources.
COMMUNITY_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vQRcJ_Co69zrL"
    "dxbOi7b5zlO7fuqooypL5ejpVPe59YC1CPXHWA-MpLhJBpGJ44FkM0ewmwMo7"
    "yq27Z/pub?output=csv"
)
PYODIDE_GRAPH_URL = (
    "https://raw.githubusercontent.com/pyscript/polyscript/refs/"
    "heads/main/rollup/pyodide_graph.json"
)
TOP_PYPI_URL = (
    "https://hugovk.github.io/top-pypi-packages/"
    "top-pypi-packages.json"
)

# Local layout.
API_DIR = Path("api")
PACKAGE_DIR = API_DIR / "package"
EXAMPLES_DIR = Path("examples")
LAST_RUN_PATH = API_DIR / "last_run.json"

# The community form's CSV column headers, spelled exactly as the
# form emits them.
COL_TIMESTAMP = "Timestamp"
COL_PACKAGE = "Package name (e.g. pandas, numba, my-cool-lib)"
COL_STATUS = "Suggested status"
COL_NOTES = "Comments about status (Markdown allowed)"

# The form's timestamp format (day/month/year).
FORM_TIMESTAMP_FORMAT = "%d/%m/%Y %H:%M:%S"

# Before any run has happened, treat everything newer than this as
# fresh.
EPOCH = datetime.datetime(
    2025, 1, 1, tzinfo=datetime.timezone.utc,
)

# A fetcher returns parsed JSON for a URL. Injectable so tests can
# supply canned data without hitting the network.
JsonFetcher = Callable[[str], dict]


def fetch_json(url: str) -> dict:
    """Fetch and parse JSON from a URL, raising on HTTP error."""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def fetch_pypi_summary(package_name: str) -> str:
    """Return a package's PyPI summary, or a placeholder.

    A missing package or empty summary yields the placeholder rather
    than raising, because a missing summary should not stop the run.
    """
    response = requests.get(
        f"https://pypi.org/pypi/{package_name}/json",
    )
    if response.status_code != 200:
        return "No summary available."
    info = response.json().get("info", {})
    return info.get("summary") or "No summary available."


def load_examples(package_name: str) -> list[dict]:
    """Load the examples for a package from `examples/<name>/`.

    Each sub-directory holds a `config.toml`, a `code.py`, and an
    optional `setup.py`. An optional `order.json` at the package root
    fixes the display order; sub-directories it doesn't mention are
    appended alphabetically. Returns an empty list when the package
    has no examples directory.
    """
    package_dir = EXAMPLES_DIR / package_name
    if not package_dir.is_dir():
        return []
    available = sorted(
        entry.name for entry in package_dir.iterdir()
        if entry.is_dir() and not entry.name.startswith(".")
    )
    entries = _ordered_example_dirs(package_dir, available)
    examples = []
    for entry in entries:
        examples.append(_load_one_example(package_dir / entry))
    return examples


def _ordered_example_dirs(
    package_dir: Path, available: list[str],
) -> list[str]:
    """Return example sub-directory names in their display order.

    Honours `order.json` if present, appending any unlisted
    directories alphabetically. Raises if `order.json` names a
    directory that doesn't exist.
    """
    order_path = package_dir / "order.json"
    if not order_path.exists():
        return available
    ordered = json.loads(order_path.read_text(encoding="utf-8"))
    missing = [name for name in ordered if name not in available]
    if missing:
        raise ValueError(
            f"order.json for '{package_dir.name}' references "
            f"missing subdirectories: {missing}",
        )
    extras = [name for name in available if name not in ordered]
    return list(ordered) + extras


def _load_one_example(subdir: Path) -> dict:
    """Read one example directory into a dict.

    The title is derived from the directory name. `setup.py` is
    optional and only included when present.
    """
    title = subdir.name.replace("_", " ").title()
    config = tomllib.loads(
        (subdir / "config.toml").read_text(encoding="utf-8"),
    )
    example = {
        "title": title,
        "config": config,
        "code": (subdir / "code.py").read_text(encoding="utf-8"),
    }
    setup_path = subdir / "setup.py"
    if setup_path.exists():
        example["setup"] = setup_path.read_text(encoding="utf-8")
    return example


def load_last_run() -> datetime.datetime:
    """Return the timestamp of the previous run, or the epoch.

    Used to ignore community updates we've already processed.
    """
    if not LAST_RUN_PATH.exists():
        return EPOCH
    data = json.loads(LAST_RUN_PATH.read_text(encoding="utf-8"))
    return datetime.datetime.fromisoformat(data["last_run"])


def normalise_status(raw: str) -> str:
    """Map a free-text status to one of red, green, or amber.

    Anything that isn't clearly red or green is treated as amber,
    matching the original behaviour.
    """
    lowered = raw.lower()
    if "red" in lowered:
        return "red"
    if "green" in lowered:
        return "green"
    return "amber"


def parse_form_timestamp(raw: str) -> datetime.datetime:
    """Parse a community-form timestamp into an aware datetime."""
    return datetime.datetime.strptime(
        raw, FORM_TIMESTAMP_FORMAT,
    ).replace(tzinfo=datetime.timezone.utc)


def parse_release(version: str) -> tuple[int, ...]:
    """Parse a dotted release string into a tuple of ints.

    Used to order Pyodide releases numerically rather than as
    strings (string ordering mis-sorts, e.g. '2025.10.1' against
    '2025.9.1'). Raises ValueError on a version that isn't a dotted
    run of integers, so an unexpected shape surfaces loudly.
    """
    try:
        return tuple(int(part) for part in version.split("."))
    except ValueError as exc:
        raise ValueError(
            f"cannot parse release version {version!r} as a dotted "
            "sequence of integers",
        ) from exc


def latest_release(releases: Iterable[str]) -> str:
    """Return the highest release string, ordered numerically."""
    candidates = [
        release for release in releases
        if release not in {"latest", "stable"}
    ]
    return max(candidates, key=parse_release)


def apply_community_updates(
    rows: Iterable[dict],
    last_run: datetime.datetime,
    summary_fetcher: Callable[[str], str] = fetch_pypi_summary,
) -> list[str]:
    """Apply community rows newer than `last_run` to package files.

    Returns the names of packages that were updated. Each qualifying
    row overrides status and notes, refreshes the examples, and
    stamps the update as a community contribution. A package without
    an existing summary gets one fetched from PyPI.
    """
    updated: list[str] = []
    for row in rows:
        timestamp = parse_form_timestamp(row[COL_TIMESTAMP])
        if timestamp <= last_run:
            continue
        package_name = row[COL_PACKAGE]
        status = normalise_status(row[COL_STATUS])
        notes = row.get(COL_NOTES)
        path = PACKAGE_DIR / f"{package_name}.json"
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
        else:
            data = {"supported_versions": {}, "summary": None}
        if not data.get("summary"):
            data["summary"] = summary_fetcher(package_name)
        data["status"] = status
        if notes:
            data["notes"] = notes
        data["updated_by"] = "Community contribution via Google Forms"
        data["updated_at"] = timestamp.isoformat()
        data["examples"] = load_examples(package_name)
        _write_json(path, data)
        updated.append(package_name)
    return updated


def build_pyodide_packages(graph: dict) -> dict[str, dict]:
    """Turn the Pyodide support graph into per-package version maps.

    The graph maps each Pyodide release to the packages (and their
    versions) it ships. We invert that into, per package, a map of
    release to package/PyScript version.
    """
    packages: dict[str, dict] = {}
    for release, package_list in graph.items():
        if release in {"latest", "stable"}:
            continue
        for package_name, version in package_list.items():
            packages.setdefault(package_name, {})[release] = {
                "package_version": version,
                "pyscript_version": PYODIDE_PYSCRIPT_MAP.get(
                    release, "unknown",
                ),
            }
    return packages


def write_pyodide_package_files(
    packages: dict[str, dict],
    newest_release: str,
    summary_fetcher: Callable[[str], str] = fetch_pypi_summary,
) -> None:
    """Write a per-package JSON file for each Pyodide package.

    A file whose versions and examples are both unchanged is left
    untouched so community contributions survive. When versions
    change, the boilerplate notes are regenerated; when only the
    examples change, existing notes are kept.
    """
    for raw_name, versions in packages.items():
        # Package names are case-insensitive; normalise to lower.
        package_name = raw_name.lower()
        path = PACKAGE_DIR / f"{package_name}.json"
        examples = load_examples(package_name)
        decision = _classify_change(path, versions, examples)
        if decision == "unchanged":
            continue
        notes = _decide_notes(path, decision)
        if not notes:
            notes = _build_notes(
                package_name=package_name,
                versions=versions,
                has_latest=newest_release in versions,
            )
        output = {
            "status": "green",
            "notes": notes,
            "pyodide_versions": versions,
            "updated_by": "automated script",
            "updated_at": _now_iso(),
            "summary": summary_fetcher(package_name),
            "examples": examples,
        }
        _write_json(path, output)


def _classify_change(
    path: Path, versions: dict, examples: list[dict],
) -> str:
    """Say whether a package file is unchanged, or what changed.

    Returns one of: 'new' (no file yet), 'unchanged', 'versions'
    (version map differs), or 'examples' (only examples differ).
    """
    if not path.exists():
        return "new"
    existing = json.loads(path.read_text(encoding="utf-8"))
    versions_same = existing.get("pyodide_versions", {}) == versions
    examples_same = existing.get("examples", []) == examples
    if versions_same and examples_same:
        return "unchanged"
    if not versions_same:
        return "versions"
    return "examples"


def _decide_notes(path: Path, decision: str) -> str:
    """Return the notes to start from, given the kind of change.

    For a version change we discard the old notes so the boilerplate
    is regenerated. For an examples-only change (or a brand-new file)
    we keep whatever notes already exist.
    """
    if decision == "versions":
        return ""
    if decision == "new":
        return ""
    existing = json.loads(path.read_text(encoding="utf-8"))
    return existing.get("notes", "")


def _build_notes(
    package_name: str, versions: dict, has_latest: bool,
) -> str:
    """Compose the boilerplate notes Markdown for a package.

    Leads with a supported / not-in-latest header, explains how to
    add the package to a PyScript config, then lists the supported
    Pyodide releases newest-first.
    """
    if has_latest:
        header = (
            f"Great news! The package `{package_name}` is "
            "[officially supported](https://pyodide.org/en/stable/"
            "usage/packages-in-pyodide.html) in the latest Pyodide "
            "release used by PyScript.\n\n"
        )
    else:
        header = (
            f"\u26a0\ufe0f The package `{package_name}` has been "
            "supported in previous versions of Pyodide, but is not "
            "supported in the latest Pyodide release (used by "
            "default in PyScript). Supported versions of Pyodide "
            "and PyScript are listed below, and details of how to "
            "pin PyScript to use a specific version of Pyodide can "
            "be [found here](https://docs.pyscript.net/2025.11.1/"
            "user-guide/configuration/#interpreter).\n\n"
        )
    body = (
        "To use it in PyScript simply add it to the `packages` "
        "section of your TOML configuration like this:\n\n"
        "```\n"
        f'packages = ["{package_name}" ]\n'
        "```\n\n"
        "Or if you're using a JSON configuration, like this:\n\n"
        "```\n"
        "{\n"
        f'    packages: ["{package_name}"]\n'
        " }\n"
        "```\n\n"
        "Read more about using packages in PyScript [in our "
        "documentation](https://docs.pyscript.net/latest/"
        "user-guide/configuration/#packages).\n\n"
        "Specifically, the following versions of the package are "
        "available for the following Pyodide releases:\n\n"
        "Pyodide version: package name (version) (PyScript "
        "Version)\n"
    )
    lines = [header + body]
    for release in sorted(versions.keys(), reverse=True):
        entry = versions[release]
        line = (
            f"\n* {release}: {package_name} "
            f"({entry['package_version']})"
        )
        pyscript_version = entry["pyscript_version"]
        if pyscript_version != "unknown":
            line += (
                f" ([PyScript {pyscript_version}]"
                f"(https://pyscript.net/releases/"
                f"{pyscript_version}/))"
            )
        lines.append(line)
    return "".join(lines)


def generate_top_100(
    top_pypi_data: dict,
    summary_fetcher: Callable[[str], str] = fetch_pypi_summary,
) -> dict:
    """Build the top-100 summary, annotated with support status.

    For each of the top 100 packages by download count, look up the
    Pyodide support status from the per-package file if we have one,
    else default to amber and fetch a PyPI summary.
    """
    summary = {
        "last_updated": top_pypi_data.get("last_update", "unknown"),
        "packages": [],
    }
    for entry in top_pypi_data.get("rows", [])[:100]:
        package_name = entry.get("project")
        path = PACKAGE_DIR / f"{package_name}.json"
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            status = data.get("status", "amber")
            desc = data.get("summary", "No summary available.")
        else:
            status = "amber"
            desc = summary_fetcher(package_name)
        summary["packages"].append({
            "package_name": package_name,
            "downloads": entry.get("download_count", 0),
            "status": status,
            "summary": desc,
        })
    return summary


def write_aggregates() -> None:
    """Write last_run.json, all.json, and examples.json.

    `all.json` is every per-package file keyed by name; `examples.json`
    lists the packages that ship at least one example.
    """
    LAST_RUN_PATH.write_text(
        json.dumps({"last_run": _now_iso()}), encoding="utf-8",
    )
    all_packages = {}
    for path in sorted(PACKAGE_DIR.glob("*.json")):
        all_packages[path.stem] = json.loads(
            path.read_text(encoding="utf-8"),
        )
    _write_json(API_DIR / "all.json", all_packages)
    with_examples = [
        name for name, data in all_packages.items()
        if data.get("examples")
    ]
    _write_json(API_DIR / "examples.json", with_examples)


def _write_json(path: Path, data) -> None:
    """Write `data` as indented JSON, creating parent dirs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=4), encoding="utf-8",
    )


def _now_iso() -> str:
    """Return the current UTC time as an ISO 8601 string."""
    return datetime.datetime.now(
        tz=datetime.timezone.utc,
    ).isoformat()


def run(fetcher: JsonFetcher = fetch_json) -> None:
    """Run all four build steps in order.

    `fetcher` is injectable so the orchestration can be exercised
    without network access in tests.
    """
    print("Step 1: applying community contributed updates...")
    last_run = load_last_run()
    csv_text = _fetch_text(COMMUNITY_CSV_URL)
    rows = list(csv.DictReader(StringIO(csv_text)))
    updated = apply_community_updates(rows, last_run)
    print(f"  applied {len(updated)} community update(s).")

    print("Step 2: generating per-package files from Pyodide data...")
    graph = fetcher(PYODIDE_GRAPH_URL)
    packages = build_pyodide_packages(graph)
    newest = latest_release(graph.keys())
    print(f"  latest Pyodide release: {newest}")
    write_pyodide_package_files(packages, newest)
    print(f"  processed {len(packages)} package(s).")

    print("Step 3: generating top_100_pypi_packages.json...")
    top_pypi_data = fetcher(TOP_PYPI_URL)
    summary = generate_top_100(top_pypi_data)
    _write_json(
        API_DIR / "top_100_pypi_packages.json", summary,
    )
    print(f"  wrote {len(summary['packages'])} package(s).")

    print("Step 4: writing aggregate files...")
    write_aggregates()
    print("  wrote all.json and examples.json.")


def _fetch_text(url: str) -> str:
    """Fetch text from a URL, raising on HTTP error."""
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    """Parse the command-line interface."""
    parser = argparse.ArgumentParser(
        description=(
            "Build the static JSON data files for the PyScript "
            "package support pages. Runs all four steps in order."
        ),
    )
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] | None = None) -> int:
    """Entry point. Returns a process exit code."""
    parse_args(argv if argv is not None else sys.argv[1:])
    run()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())