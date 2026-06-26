"""
Read TOML responses produced by the LLM and write them to disk as
PyScript examples.

For each package in `prompts/`, this script looks for a
`response.toml` file alongside `prompt.md`. If found, the response is
parsed, validated, and (if it passes) written to
`examples/<package>/<dir_name>/{config.toml,setup.py,code.py}` plus
`examples/<package>/order.json` and a templated `README.md`.

Hand-edited examples are preserved: if `examples/<package>/` already
exists, the package is skipped unless `--force` is given. A
`README.md` written by hand stays put unless `--force` is set.

When run with `--branch-per-package`, each package becomes a
self-contained commit on its own branch named `examples/<package>`,
ready for a separate review. The working tree returns to `main`
between packages and at the end of the run, so the next step is to
push the branches and open pull requests.

Prerequisite for `--branch-per-package`: this script's own bookkeeping
files (`examples/_apply_manifest.json`) MUST be in the repo's
`.gitignore`, otherwise they will be committed alongside the package
files. Add the line:

    examples/_*.json

to `.gitignore` once, before the first run.

Run with `--help` for usage. Typical flow:

```
python apply_llm_response.py                   # apply all
python apply_llm_response.py --package affine  # one package
python apply_llm_response.py --validate-only   # check, don't write
python apply_llm_response.py --force           # overwrite
python apply_llm_response.py --branch-per-package  # one branch per package
python apply_llm_response.py --branch-per-package --push  # branch + push
```
"""

import argparse
import ast
import json
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


# Where things live, relative to the script's directory.
SCRIPT_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = SCRIPT_DIR / "prompts"
EXAMPLES_DIR = SCRIPT_DIR / "examples"

# Filenames inside a per-package prompt directory.
RESPONSE_FILENAME = "response.toml"
WARNING_FILENAME = ".warning"

# Files we lay down per example directory.
EXAMPLE_FILES = ("config.toml", "setup.py", "code.py")

# A `dir_name` must be lowercase ASCII snake_case: a starting
# letter, then letters/digits/underscores, no leading digit, no
# trailing underscore, no double underscores.
DIR_NAME_RE = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)*$")

# The repo's main branch and the per-package branch prefix. We assume
# `main` is always the integration branch in this repo.
BASE_BRANCH = "main"
BRANCH_PREFIX = "examples/"


@dataclass
class ValidationResult:
    """The outcome of validating one parsed response.

    `errors` blocks the package from being written; `warnings` are
    surfaced in the manifest but do not stop the write.
    """

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """True when the response passed all hard checks."""
        return not self.errors


@dataclass
class ParsedExample:
    """One example pulled out of a response."""

    dir_name: str
    title: str
    config: str
    setup: str
    code: str


@dataclass
class ParsedResponse:
    """A whole response: package name plus its examples in order."""

    package: str
    examples: list[ParsedExample]


def parse_response(text: str) -> ParsedResponse:
    """Parse a TOML response string into a ParsedResponse.

    Raises `tomllib.TOMLDecodeError` if the input is not valid TOML,
    or `KeyError`/`TypeError` if the document is shaped wrong. Higher
    layers turn those into ValidationResult errors.
    """
    data = tomllib.loads(text)
    examples = [
        ParsedExample(
            dir_name=ex["dir_name"],
            title=ex["title"],
            config=ex["config"],
            setup=ex["setup"],
            code=ex["code"],
        )
        for ex in data["example"]
    ]
    return ParsedResponse(package=data["package"], examples=examples)


def validate(
    parsed: ParsedResponse,
    expected_package: str,
) -> ValidationResult:
    """Run the hard and soft checks against a parsed response."""
    result = ValidationResult()
    if parsed.package != expected_package:
        result.errors.append(
            f"package field {parsed.package!r} does not match "
            f"expected {expected_package!r}",
        )
    if not parsed.examples:
        result.errors.append("response contains no examples")
        return result
    if len(parsed.examples) > 3:
        result.errors.append(
            f"response contains {len(parsed.examples)} examples; "
            "the maximum is 3",
        )
    seen_dirs: set[str] = set()
    for index, example in enumerate(parsed.examples):
        _validate_example(
            example=example,
            index=index,
            target_package=expected_package,
            result=result,
            seen_dirs=seen_dirs,
        )
    return result


def _validate_example(
    example: ParsedExample,
    index: int,
    target_package: str,
    result: ValidationResult,
    seen_dirs: set[str],
) -> None:
    """Apply the per-example checks, mutating the shared result.

    Index 0 is the onboarding example with the IPython shim; later
    indices have stricter rules about not re-importing or
    re-establishing the IPython namespace.
    """
    label = f"example {index + 1} ({example.dir_name!r})"
    if not DIR_NAME_RE.match(example.dir_name):
        result.errors.append(
            f"{label}: dir_name does not match required pattern",
        )
    if example.dir_name in seen_dirs:
        result.errors.append(
            f"{label}: duplicate dir_name in response",
        )
    seen_dirs.add(example.dir_name)
    _check_python_parses(example.setup, f"{label} setup.py", result)
    _check_python_parses(example.code, f"{label} code.py", result)
    _check_ipython_rules(example, index, label, result)
    _check_helper_uniqueness(example, label, result)
    _check_target_package_used(example, target_package, label, result)
    _check_config_lists_target(example, target_package, label, result)


def _check_python_parses(
    source: str, label: str, result: ValidationResult,
) -> None:
    """Hard-fail when a Python source string does not parse."""
    try:
        ast.parse(source)
    except SyntaxError as exc:
        result.errors.append(f"{label}: SyntaxError: {exc}")


def _check_ipython_rules(
    example: ParsedExample,
    index: int,
    label: str,
    result: ValidationResult,
) -> None:
    """Enforce the IPython shim rules across cells.

    Cell 1 must import the IPython display API in its `code.py`;
    later cells must not import IPython anywhere because the shim is
    only registered by cell 1's setup.
    """
    if index == 0:
        if "from IPython" not in example.code:
            result.errors.append(
                f"{label}: code.py is missing the required "
                "`from IPython.core.display import display, HTML`",
            )
        return
    for source_label, source in (
        ("setup.py", example.setup),
        ("code.py", example.code),
    ):
        if re.search(r"\b(from|import)\s+IPython\b", source):
            result.errors.append(
                f"{label} {source_label}: contains a forbidden "
                "IPython import; the shim is only set up by the "
                "first example",
            )
    if _has_top_level_imports(example.code):
        result.errors.append(
            f"{label} code.py: contains top-level imports; "
            "examples 2+ must put their imports in setup.py",
        )


def _has_top_level_imports(source: str) -> bool:
    """True if the source's module body has any import statements.

    Imports inside functions, classes, or guarded blocks do not
    count; we use `ast` so a comment like `# import foo` doesn't
    cause a false positive.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    return any(
        isinstance(node, (ast.Import, ast.ImportFrom))
        for node in tree.body
    )


def _check_helper_uniqueness(
    example: ParsedExample,
    label: str,
    result: ValidationResult,
) -> None:
    """Soft-warn on duplicate definitions of `display`/`heading`/`note`.

    These helpers are established by the setup template and must not
    be redefined; doing so silently overrides the template version.
    """
    for helper in ("display", "heading", "note"):
        setup_count = _count_def(example.setup, helper)
        if setup_count > 1:
            result.warnings.append(
                f"{label} setup.py: defines {helper!r} "
                f"{setup_count} times; expected once",
            )
        if _count_def(example.code, helper) > 0:
            result.warnings.append(
                f"{label} code.py: redefines {helper!r}; "
                "should rely on setup.py's version",
            )


def _count_def(source: str, name: str) -> int:
    """Count top-level `def name(...)` occurrences in a source string."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return 0
    return sum(
        1 for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == name
    )


def _check_target_package_used(
    example: ParsedExample,
    target_package: str,
    label: str,
    result: ValidationResult,
) -> None:
    """Soft-warn when the example does not appear to use the package.

    We look for the package name as a word in either source. A
    distribution name like `Pillow` may be imported as `PIL`, so we
    check both possible spellings against the package name as
    lower-cased and against any obvious alias.
    """
    haystack = example.setup + "\n" + example.code
    needle = re.compile(rf"\b{re.escape(target_package)}\b", re.IGNORECASE)
    if not needle.search(haystack):
        result.warnings.append(
            f"{label}: does not appear to reference "
            f"{target_package!r} by name",
        )


def _check_config_lists_target(
    example: ParsedExample,
    target_package: str,
    label: str,
    result: ValidationResult,
) -> None:
    """Soft-warn when `config.toml` does not list the target package."""
    try:
        config_data = tomllib.loads(example.config)
    except tomllib.TOMLDecodeError as exc:
        result.errors.append(
            f"{label} config.toml: not valid TOML: {exc}",
        )
        return
    packages = config_data.get("packages") or []
    if target_package not in packages:
        result.warnings.append(
            f"{label} config.toml: packages list does not "
            f"include {target_package!r}",
        )


def write_package(
    parsed: ParsedResponse,
    examples_dir: Path,
    force: bool = False,
) -> None:
    """Lay down a package's examples on disk.

    Creates `examples/<package>/<dir_name>/{config.toml,setup.py,code.py}`
    for each example, plus `order.json` and (if missing) `README.md`.
    """
    package_dir = examples_dir / parsed.package
    package_dir.mkdir(parents=True, exist_ok=True)
    for example in parsed.examples:
        example_dir = package_dir / example.dir_name
        if example_dir.exists() and force:
            _rmtree(example_dir)
        example_dir.mkdir(parents=True, exist_ok=True)
        (example_dir / "config.toml").write_text(
            _normalize(example.config), encoding="utf-8",
        )
        (example_dir / "setup.py").write_text(
            _normalize(example.setup), encoding="utf-8",
        )
        (example_dir / "code.py").write_text(
            _normalize(example.code), encoding="utf-8",
        )
    _write_order_json(package_dir, parsed)
    _write_readme(package_dir, parsed.package, force=force)


def _normalize(text: str) -> str:
    """Strip a single leading newline and ensure exactly one trailing.

    TOML literal strings often start with a newline immediately after
    the opening `'''`; we don't want that to land on disk. We also
    enforce a single trailing newline so the files look POSIX-tidy.
    """
    if text.startswith("\n"):
        text = text[1:]
    return text.rstrip("\n") + "\n"


def _write_order_json(
    package_dir: Path, parsed: ParsedResponse,
) -> None:
    """Write `order.json` listing the example directories in order."""
    order = [example.dir_name for example in parsed.examples]
    (package_dir / "order.json").write_text(
        json.dumps(order, indent=4) + "\n", encoding="utf-8",
    )


def _write_readme(
    package_dir: Path, package_name: str, force: bool = False,
) -> None:
    """Write a templated README.md, leaving any existing one alone.

    A reviewer might hand-edit the README; we don't clobber that work
    on a normal re-run. With `--force`, the templated version is
    written regardless.
    """
    readme_path = package_dir / "README.md"
    if readme_path.exists() and not force:
        return
    readme_path.write_text(
        README_TEMPLATE.format(package=package_name), encoding="utf-8",
    )


def _rmtree(path: Path) -> None:
    """Minimal recursive delete, mirroring the helper in the generator."""
    for child in path.iterdir():
        if child.is_dir():
            _rmtree(child)
        else:
            child.unlink()
    path.rmdir()


def propagate_warning_marker(
    package_name: str,
    prompts_dir: Path,
    examples_dir: Path,
) -> None:
    """Carry forward a `.warning` marker from prompts/ to examples/.

    A package flagged low-context at prompt time should keep that
    flag at example time, so a reviewer browsing `examples/` knows
    which packages need a closer look without going back to prompts.
    """
    src = prompts_dir / package_name / WARNING_FILENAME
    dst = examples_dir / package_name / WARNING_FILENAME
    if src.exists():
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


@dataclass
class PackageResult:
    """The outcome of processing one package, for the manifest."""

    name: str
    status: str
    message: str
    warnings: list[str] = field(default_factory=list)


def process_package(
    name: str,
    prompts_dir: Path,
    examples_dir: Path,
    force: bool = False,
    validate_only: bool = False,
) -> PackageResult:
    """Apply one package's response, returning a manifest record.

    Possible statuses: 'applied', 'skipped' (already exists),
    'missing_response', 'validation_failed', 'parse_failed'.
    """
    response_path = prompts_dir / name / RESPONSE_FILENAME
    if not response_path.exists():
        return PackageResult(
            name=name,
            status="missing_response",
            message=f"no {RESPONSE_FILENAME} found for {name}",
        )
    package_dir = examples_dir / name
    if package_dir.exists() and not force and not validate_only:
        return PackageResult(
            name=name,
            status="skipped",
            message="examples already exist on disk",
        )
    text = response_path.read_text(encoding="utf-8")
    try:
        parsed = parse_response(text)
    except (
        tomllib.TOMLDecodeError, KeyError, TypeError,
    ) as exc:
        return PackageResult(
            name=name,
            status="parse_failed",
            message=f"could not parse response: {exc}",
        )
    result = validate(parsed, expected_package=name)
    if not result.ok:
        return PackageResult(
            name=name,
            status="validation_failed",
            message=f"{len(result.errors)} error(s)",
            warnings=result.errors + result.warnings,
        )
    if validate_only:
        return PackageResult(
            name=name,
            status="validated",
            message="valid (not written)",
            warnings=result.warnings,
        )
    write_package(parsed, examples_dir, force=force)
    propagate_warning_marker(name, prompts_dir, examples_dir)
    return PackageResult(
        name=name,
        status="applied",
        message=f"wrote {len(parsed.examples)} example(s)",
        warnings=result.warnings,
    )


def discover_packages(prompts_dir: Path) -> list[str]:
    """Return prompt-directory names, sorted, that have a response."""
    if not prompts_dir.is_dir():
        return []
    out = []
    for entry in prompts_dir.iterdir():
        if not entry.is_dir() or entry.name.startswith("_"):
            continue
        if (entry / RESPONSE_FILENAME).exists():
            out.append(entry.name)
    out.sort(key=str.lower)
    return out


def process_package_with_branching(
    name: str,
    prompts_dir: Path,
    examples_dir: Path,
    repo_root: Path,
    force: bool = False,
    push: bool = False,
) -> PackageResult:
    """Apply one package's response onto its own branch.

    Wraps the same parse-and-validate flow as `process_package`,
    but instead of writing into the working tree the writer is
    `commit_package_to_branch`, which leaves the package's files
    on a dedicated branch named `examples/<package>` and returns
    the working tree to main.

    Possible statuses: same as `process_package` plus 'branched'
    (success) and 'branch_failed' (a git step failed).
    """
    response_path = prompts_dir / name / RESPONSE_FILENAME
    if not response_path.exists():
        return PackageResult(
            name=name,
            status="missing_response",
            message=f"no {RESPONSE_FILENAME} found for {name}",
        )
    branch = f"{BRANCH_PREFIX}{name}"
    if _git_branch_exists(repo_root, branch) and not force:
        return PackageResult(
            name=name,
            status="skipped",
            message=f"branch '{branch}' already exists",
        )
    text = response_path.read_text(encoding="utf-8")
    try:
        parsed = parse_response(text)
    except (
        tomllib.TOMLDecodeError, KeyError, TypeError,
    ) as exc:
        return PackageResult(
            name=name,
            status="parse_failed",
            message=f"could not parse response: {exc}",
        )
    result = validate(parsed, expected_package=name)
    if not result.ok:
        return PackageResult(
            name=name,
            status="validation_failed",
            message=f"{len(result.errors)} error(s)",
            warnings=result.errors + result.warnings,
        )
    low_context = is_low_context(prompts_dir, name)
    try:
        commit_package_to_branch(
            parsed=parsed,
            repo_root=repo_root,
            examples_dir=examples_dir,
            low_context=low_context,
            force=force,
        )
    except GitError as exc:
        return PackageResult(
            name=name,
            status="branch_failed",
            message=str(exc),
            warnings=result.warnings,
        )
    if push:
        try:
            push_branch(repo_root, branch)
        except GitError as exc:
            return PackageResult(
                name=name,
                status="branch_failed",
                message=f"push failed: {exc}",
                warnings=result.warnings,
            )
    flag = " (NEEDS REVIEW)" if low_context else ""
    return PackageResult(
        name=name,
        status="branched",
        message=f"branch '{branch}' created{flag}",
        warnings=result.warnings,
    )


def write_manifest(
    examples_dir: Path, results: list[PackageResult],
) -> None:
    """Write a per-run summary at examples/_apply_manifest.json."""
    examples_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "packages": [
            {
                "name": r.name,
                "status": r.status,
                "message": r.message,
                "warnings": list(r.warnings),
            }
            for r in results
        ],
    }
    (examples_dir / "_apply_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8",
    )


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    """Command-line interface for one-off and batch use."""
    parser = argparse.ArgumentParser(
        description=(
            "Apply LLM TOML responses to the examples directory."
        ),
    )
    parser.add_argument(
        "--package",
        action="append",
        default=None,
        help=(
            "Process only this package (may be given more than once). "
            "Default: process every package whose prompt directory "
            f"contains a {RESPONSE_FILENAME}."
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
            "Re-apply responses even if examples already exist. "
            "Replaces example directories and the templated README."
        ),
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate responses without writing any files.",
    )
    parser.add_argument(
        "--prompts-dir",
        type=Path,
        default=PROMPTS_DIR,
        help=f"Prompts dir (default: {PROMPTS_DIR}).",
    )
    parser.add_argument(
        "--examples-dir",
        type=Path,
        default=EXAMPLES_DIR,
        help=f"Examples dir (default: {EXAMPLES_DIR}).",
    )
    parser.add_argument(
        "--branch-per-package",
        action="store_true",
        help=(
            "Commit each package onto its own branch named "
            f"`{BRANCH_PREFIX}<package>`, rather than writing all "
            "files to the working tree. Requires a clean working "
            f"tree on `{BASE_BRANCH}`."
        ),
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help=(
            "Push each created branch to origin. Only valid in "
            "combination with --branch-per-package."
        ),
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=SCRIPT_DIR,
        help=(
            "Path to the git repository root for branch operations "
            f"(default: {SCRIPT_DIR})."
        ),
    )
    args = parser.parse_args(list(argv))
    if args.push and not args.branch_per_package:
        parser.error("--push requires --branch-per-package")
    if args.branch_per_package and args.validate_only:
        parser.error(
            "--branch-per-package is incompatible with "
            "--validate-only",
        )
    return args


def main(argv: Iterable[str] | None = None) -> int:
    """Entry point. Returns a process exit code."""
    args = parse_args(argv if argv is not None else sys.argv[1:])
    if args.package:
        targets = list(args.package)
    else:
        targets = discover_packages(args.prompts_dir)
    if args.limit is not None:
        targets = targets[: args.limit]
    if args.branch_per_package:
        try:
            ensure_clean_state(args.repo_root)
        except GitError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
    results: list[PackageResult] = []
    for index, name in enumerate(targets, start=1):
        if args.branch_per_package:
            record = process_package_with_branching(
                name=name,
                prompts_dir=args.prompts_dir,
                examples_dir=args.examples_dir,
                repo_root=args.repo_root,
                force=args.force,
                push=args.push,
            )
        else:
            record = process_package(
                name=name,
                prompts_dir=args.prompts_dir,
                examples_dir=args.examples_dir,
                force=args.force,
                validate_only=args.validate_only,
            )
        results.append(record)
        line = (
            f"[{index}/{len(targets)}] {name}: {record.status} "
            f"-- {record.message}"
        )
        print(line)
        for warning in record.warnings:
            print(f"    warning: {warning}")
    if not args.validate_only:
        write_manifest(args.examples_dir, results)
    if args.branch_per_package:
        _print_branch_summary(results)
    bad = sum(
        1 for r in results
        if r.status in (
            "parse_failed", "validation_failed", "branch_failed",
        )
    )
    return 1 if bad else 0


def _print_branch_summary(results: list[PackageResult]) -> None:
    """Emit a summary block listing branches ready for review.

    The operator's next step is to push these branches and open
    pull requests, so we surface them prominently rather than
    leaving them buried in the per-package log lines.
    """
    branched = [r for r in results if r.status == "branched"]
    failed = [r for r in results if r.status == "branch_failed"]
    print()
    if branched:
        print(f"Branches ready to push and PR ({len(branched)}):")
        for r in branched:
            review_marker = (
                " [NEEDS REVIEW]"
                if "NEEDS REVIEW" in r.message else ""
            )
            print(f"  {BRANCH_PREFIX}{r.name}{review_marker}")
    if failed:
        print(f"\nFailed packages ({len(failed)}):")
        for r in failed:
            print(f"  {r.name}: {r.message}")


# A small README written into each package directory the first time
# the applier touches it. Mirrors the structure of the hand-written
# pandas/README.md so reviewers see a consistent shape across
# packages.
README_TEMPLATE = """\
# {package} Examples

Each sub-directory contains a self-contained example. The order in
which the examples are to appear is specified in `order.json` (an
array of directory names in the expected order).

In each example directory you'll find:

* `config.toml` - must conform to the specification outlined here:
  https://docs.pyscript.net/latest/user-guide/configuration/ This is
  parsed and ultimately turned into a JSON representation as part of
  the package's API object.
* `setup.py` - Python code for contextual and environmental setup,
  NOT SEEN BY THE END USER, but is run before the `code.py` code is
  evaluated. Allows us to create useful (IPython) shims, avoid
  repeating boilerplate and whatnot.
* `code.py` - the actual code added to the editor which forms the
  practical example of using the package.
"""


# ---------------------------------------------------------------------
# Git workflow: one branch per package.
# ---------------------------------------------------------------------


class GitError(RuntimeError):
    """Raised when a git operation fails or a precondition isn't met."""


def _run_git(
    args: list[str], cwd: Path, check: bool = True,
) -> subprocess.CompletedProcess:
    """Run a git command in `cwd` and return the completed process.

    All callers pass argument lists (no shell), so quoting and
    escaping are handled by the OS. When `check` is True, a non-zero
    exit raises GitError with stderr included for diagnosis.
    """
    completed = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
    )
    if check and completed.returncode != 0:
        cmd = " ".join(["git", *args])
        raise GitError(
            f"`{cmd}` failed in {cwd}: "
            f"{completed.stderr.strip() or completed.stdout.strip()}"
        )
    return completed


def _git_current_branch(cwd: Path) -> str:
    """Return the name of the currently checked-out branch."""
    return _run_git(
        ["rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd,
    ).stdout.strip()


def _git_working_tree_clean(cwd: Path) -> bool:
    """True when `git status --porcelain` produces no output."""
    out = _run_git(["status", "--porcelain"], cwd=cwd).stdout
    return out.strip() == ""


def _git_branch_exists(cwd: Path, branch: str) -> bool:
    """True when a local branch with the given name exists."""
    completed = _run_git(
        ["show-ref", "--verify", "--quiet", f"refs/heads/{branch}"],
        cwd=cwd,
        check=False,
    )
    return completed.returncode == 0


def ensure_clean_state(cwd: Path) -> None:
    """Verify the repo is on `main` with a clean working tree.

    Raises GitError if either condition fails. Called once at the
    start of a `--branch-per-package` run so the user gets a clear
    message before any package is touched.
    """
    branch = _git_current_branch(cwd)
    if branch != BASE_BRANCH:
        raise GitError(
            f"expected to start on '{BASE_BRANCH}', currently on "
            f"'{branch}'; commit or stash and switch to "
            f"'{BASE_BRANCH}' first",
        )
    if not _git_working_tree_clean(cwd):
        raise GitError(
            "working tree is not clean; commit or stash changes "
            "before running with --branch-per-package",
        )


def _commit_message(parsed: ParsedResponse, low_context: bool) -> str:
    """Compose the commit message for one package's branch.

    The subject mentions the package name. The body lists each
    example's directory name and title. Low-context packages get a
    `[NEEDS REVIEW]` prefix on the subject and an extra paragraph
    so reviewers know to look harder. A `Generated-By` trailer at
    the end identifies the commit as automation-authored for any
    later tooling that wants to grep for it.
    """
    subject = f"Add PyScript examples for {parsed.package}"
    if low_context:
        subject = f"[NEEDS REVIEW] {subject}"
    lines = [subject, ""]
    lines.append(
        f"Generated by apply_llm_response.py from "
        f"prompts/{parsed.package}/response.toml.",
    )
    lines.append("")
    if low_context:
        lines.append(
            "This package was flagged as low-context at prompt "
            "time: no usable README, tutorial, or documentation "
            "page was found. The LLM was asked to draw on its own "
            "knowledge of the package, so the examples need extra "
            "scrutiny before merging.",
        )
        lines.append("")
    lines.append("Examples included:")
    for example in parsed.examples:
        lines.append(f"- {example.dir_name}: {example.title}")
    lines.append("")
    lines.append("Generated-By: apply_llm_response.py")
    return "\n".join(lines) + "\n"


def commit_package_to_branch(
    parsed: ParsedResponse,
    repo_root: Path,
    examples_dir: Path,
    low_context: bool,
    force: bool = False,
) -> str:
    """Create a branch, commit the package's files, and return to main.

    Returns the branch name. Assumes the working tree is clean and
    the repo is currently on `main` (the caller must have run
    `ensure_clean_state`). On any failure, attempts to leave the
    repo back on `main` with a clean working tree.
    """
    branch = f"{BRANCH_PREFIX}{parsed.package}"
    if _git_branch_exists(repo_root, branch):
        if not force:
            raise GitError(
                f"branch '{branch}' already exists; pass --force "
                f"to replace it",
            )
        # Delete the existing branch so checkout creates it fresh.
        _run_git(["branch", "-D", branch], cwd=repo_root)
    try:
        _run_git(["checkout", "-b", branch], cwd=repo_root)
        write_package(parsed, examples_dir, force=force)
        try:
            relative = (
                examples_dir / parsed.package
            ).resolve().relative_to(repo_root.resolve())
        except ValueError as exc:
            raise GitError(
                f"examples_dir is not inside the repo: {exc}",
            ) from exc
        _run_git(["add", "--", str(relative)], cwd=repo_root)
        _run_git(
            ["commit", "-m", _commit_message(parsed, low_context)],
            cwd=repo_root,
        )
    except Exception:
        # Try to leave the repo on main with no half-applied state.
        _git_recover_to_main(repo_root, branch)
        raise
    _run_git(["checkout", BASE_BRANCH], cwd=repo_root)
    return branch


def _git_recover_to_main(repo_root: Path, branch: str) -> None:
    """Best-effort cleanup after a commit-step failure.

    Used in the exception path of `commit_package_to_branch`. We
    don't raise from here because a failure during cleanup would
    mask the original error; instead we let the caller propagate
    its own GitError.
    """
    _run_git(
        ["checkout", "--force", BASE_BRANCH],
        cwd=repo_root, check=False,
    )
    if _git_branch_exists(repo_root, branch):
        _run_git(
            ["branch", "-D", branch], cwd=repo_root, check=False,
        )


def push_branch(repo_root: Path, branch: str) -> None:
    """Push a branch to origin, setting the upstream tracking ref.

    Uses `--set-upstream` so a subsequent plain `git push` from the
    command line works as the operator expects.
    """
    _run_git(
        ["push", "--set-upstream", "origin", branch], cwd=repo_root,
    )


def is_low_context(prompts_dir: Path, package_name: str) -> bool:
    """True when the prompt directory carries a `.warning` marker."""
    return (
        prompts_dir / package_name / WARNING_FILENAME
    ).exists()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())