"""
Send PyScript-example prompts to an OpenAI-compatible LLM gateway.

For each package in `prompts/<package>/` whose `prompt.md` exists but
which doesn't yet have a `response.toml`, this script builds a chat
completion request, sends it, and writes the reply to `response.toml`
for `apply_llm_response.py` to consume.

Requests run concurrently with a small bounded worker pool, because
the gateway exposes only synchronous chat completions (no batch API),
so client-side concurrency is the way to get through a few hundred
packages in reasonable time. The default pool size is deliberately
conservative.

The run is resumable in the simplest possible way: a package that
already has a `response.toml` is skipped, so an interrupted run can
be restarted and will only do the work that remains. A package whose
request fails after retries gets a `.run_failed` marker and the run
continues.

Run with `--help` for the flag set.

Environment:

- PROXY_API_KEY    -- the gateway API key (required).
- PROXY_BASE_URL   -- the gateway base URL (required).

Output files (gitignored):

- prompts/<package>/response.toml  -- the LLM's reply.
- prompts/<package>/.run_failed    -- written when a request errors.
- prompts/_run_manifest.json       -- per-run summary.
"""

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

from openai import OpenAI


# Where things live, relative to the script's directory.
SCRIPT_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = SCRIPT_DIR / "prompts"
SHARED_DIR_NAME = "_shared"

# Filenames inside per-package and shared directories.
PROMPT_FILENAME = "prompt.md"
RESPONSE_FILENAME = "response.toml"
RUN_FAILED_FILENAME = ".run_failed"
SYSTEM_PROMPT_FILENAME = "system_prompt.md"
SETUP_TEMPLATE_FILENAME = "setup_template.py"
REFERENCE_EXAMPLE_DIRNAME = "reference_example"

# Manifest file.
RUN_MANIFEST_FILENAME = "_run_manifest.json"

# Defaults. The model id and client headers match the values
# confirmed against the gateway. The base URL and key are read from
# the environment and never hard-coded.
DEFAULT_MODEL = "us.anthropic.claude-opus-4-7"
DEFAULT_MAX_TOKENS = 16_000
DEFAULT_CONCURRENCY = 4
DEFAULT_MAX_RETRIES = 4
CLIENT_HEADERS = {
    "X-Client-Source": "anaconda-cli-dev",
    "X-Client-Version": "0.0.1",
}


@dataclass
class SharedAssets:
    """The shared content sent with every prompt.

    `system_prompt` becomes the system message; `reference_block`
    is prepended to each per-package prompt in the user message.
    """

    system_prompt: str
    reference_block: str


def load_shared_assets(prompts_dir: Path) -> SharedAssets:
    """Read the system prompt and assemble the reference block.

    The reference block is one string: the setup template followed by
    the contents of every file in the reference example directory,
    each clearly labeled. This mirrors what a human attaching files
    to a chat would provide.
    """
    shared = prompts_dir / SHARED_DIR_NAME
    system_prompt = (
        shared / SYSTEM_PROMPT_FILENAME
    ).read_text(encoding="utf-8")
    parts: list[str] = []
    setup_template_path = shared / SETUP_TEMPLATE_FILENAME
    if setup_template_path.exists():
        parts.append(
            f"=== shared file: {SETUP_TEMPLATE_FILENAME} ===\n\n"
            f"{setup_template_path.read_text(encoding='utf-8')}"
        )
    ref_root = shared / REFERENCE_EXAMPLE_DIRNAME
    if ref_root.is_dir():
        for path in sorted(_walk_files(ref_root)):
            relative = path.relative_to(ref_root)
            parts.append(
                f"=== reference example: "
                f"{REFERENCE_EXAMPLE_DIRNAME}/{relative} ===\n\n"
                f"{path.read_text(encoding='utf-8')}"
            )
    reference_block = "\n\n".join(parts)
    return SharedAssets(
        system_prompt=system_prompt,
        reference_block=reference_block,
    )


def _walk_files(root: Path) -> Iterable[Path]:
    """Yield every regular file under `root`, recursively."""
    for entry in root.iterdir():
        if entry.is_dir():
            yield from _walk_files(entry)
        else:
            yield entry


def discover_packages(prompts_dir: Path) -> list[str]:
    """Return prompt directories that need a response, sorted.

    A package qualifies if it has a `prompt.md` but no
    `response.toml`. This skip-if-done rule is the whole of the
    resumability mechanism.
    """
    if not prompts_dir.is_dir():
        return []
    out: list[str] = []
    for entry in prompts_dir.iterdir():
        if not entry.is_dir() or entry.name.startswith("_"):
            continue
        if not (entry / PROMPT_FILENAME).exists():
            continue
        if (entry / RESPONSE_FILENAME).exists():
            continue
        out.append(entry.name)
    out.sort(key=str.lower)
    return out


def build_messages(
    package_prompt: str, shared: SharedAssets,
) -> list[dict]:
    """Construct the chat messages for one request.

    The system message carries the rules; the user message carries
    the shared reference block followed by the per-package prompt.
    No provider-specific extras (this gateway passes through neither
    prompt caching nor batch features).
    """
    user_content = (
        f"{shared.reference_block}\n\n{package_prompt}"
        if shared.reference_block
        else package_prompt
    )
    return [
        {"role": "system", "content": shared.system_prompt},
        {"role": "user", "content": user_content},
    ]


def extract_response_text(completion) -> str:
    """Pull the assistant text out of a chat completion response."""
    return completion.choices[0].message.content or ""


def write_response(package_dir: Path, body: str) -> None:
    """Write the response text to disk, clearing any prior failure."""
    package_dir.mkdir(parents=True, exist_ok=True)
    (package_dir / RESPONSE_FILENAME).write_text(
        body, encoding="utf-8",
    )
    failure = package_dir / RUN_FAILED_FILENAME
    if failure.exists():
        failure.unlink()


def write_failure(package_dir: Path, reason: str) -> None:
    """Record a failure for a package so re-runs can find and retry."""
    package_dir.mkdir(parents=True, exist_ok=True)
    (package_dir / RUN_FAILED_FILENAME).write_text(
        reason + "\n", encoding="utf-8",
    )


@dataclass
class PackageResult:
    """The outcome of one package, for the manifest and summary."""

    name: str
    status: str
    message: str
    prompt_tokens: int = 0
    completion_tokens: int = 0


def process_one(
    name: str,
    prompts_dir: Path,
    shared: SharedAssets,
    client: OpenAI,
    model: str,
    max_tokens: int,
) -> PackageResult:
    """Send one package's prompt and write its response or failure.

    Returns a PackageResult either way; this function never raises
    for an API error, so one bad package can't sink a concurrent
    run. Retries are handled by the client's own retry policy.
    """
    package_dir = prompts_dir / name
    prompt_text = (
        package_dir / PROMPT_FILENAME
    ).read_text(encoding="utf-8")
    messages = build_messages(prompt_text, shared)
    try:
        completion = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=messages,
        )
    except Exception as exc:
        write_failure(package_dir, f"{type(exc).__name__}: {exc}")
        return PackageResult(
            name=name, status="failed",
            message=f"{type(exc).__name__}: {exc}",
        )
    body = extract_response_text(completion)
    write_response(package_dir, body)
    usage = completion.usage
    return PackageResult(
        name=name,
        status="succeeded",
        message="response written",
        prompt_tokens=getattr(usage, "prompt_tokens", 0),
        completion_tokens=getattr(usage, "completion_tokens", 0),
    )


def run_concurrently(
    targets: list[str],
    prompts_dir: Path,
    shared: SharedAssets,
    client: OpenAI,
    model: str,
    max_tokens: int,
    concurrency: int,
) -> list[PackageResult]:
    """Process all targets through a bounded thread pool.

    Results are printed as they complete so the operator sees
    progress on a long run. The pool size caps how many requests
    are in flight against the gateway at once.
    """
    results: list[PackageResult] = []
    total = len(targets)
    done = 0
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = {
            pool.submit(
                process_one,
                name=name,
                prompts_dir=prompts_dir,
                shared=shared,
                client=client,
                model=model,
                max_tokens=max_tokens,
            ): name
            for name in targets
        }
        for future in as_completed(futures):
            record = future.result()
            results.append(record)
            done += 1
            print(
                f"[{done}/{total}] {record.name}: "
                f"{record.status} -- {record.message}",
            )
    # Sort results to a stable order for the manifest, independent
    # of completion timing.
    results.sort(key=lambda r: r.name.lower())
    return results


def write_run_manifest(
    prompts_dir: Path, results: list[PackageResult],
) -> None:
    """Write a per-run summary at prompts/_run_manifest.json."""
    prompts_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "packages": [
            {
                "name": r.name,
                "status": r.status,
                "message": r.message,
                "prompt_tokens": r.prompt_tokens,
                "completion_tokens": r.completion_tokens,
            }
            for r in results
        ],
    }
    (prompts_dir / RUN_MANIFEST_FILENAME).write_text(
        json.dumps(payload, indent=2), encoding="utf-8",
    )


def print_summary(results: list[PackageResult]) -> None:
    """Print a short tally of successes and failures after a run."""
    succeeded = [r for r in results if r.status == "succeeded"]
    failed = [r for r in results if r.status == "failed"]
    print()
    print(
        f"Done: {len(succeeded)} succeeded, {len(failed)} failed "
        f"(of {len(results)}).",
    )
    if failed:
        print("Failed packages:")
        for r in failed:
            print(f"  {r.name}: {r.message}")
        print(
            "Re-run to retry them; packages with a response are "
            "skipped automatically.",
        )


def make_client(max_retries: int) -> OpenAI:
    """Build the gateway client from environment configuration.

    Refuses to run if the key or base URL is missing, with a clear
    message rather than a confusing SDK error later.
    """
    key = os.environ.get("PROXY_API_KEY")
    if not key:
        raise SystemExit(
            "PROXY_API_KEY is not set; export it and re-run.",
        )
    base_url = os.environ.get("PROXY_BASE_URL")
    if not base_url:
        raise SystemExit(
            "PROXY_BASE_URL is not set; export it and re-run.",
        )
    return OpenAI(
        base_url=base_url,
        api_key=key,
        default_headers=CLIENT_HEADERS,
        max_retries=max_retries,
    )


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    """Parse the command-line interface."""
    parser = argparse.ArgumentParser(
        description=(
            "Send PyScript-example prompts to an OpenAI-compatible "
            "LLM gateway, concurrently."
        ),
    )
    parser.add_argument(
        "--package", action="append", default=None,
        help=(
            "Process only this package (may be given more than "
            "once). Default: every package without a response."
        ),
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Stop after this many packages.",
    )
    parser.add_argument(
        "--concurrency", type=int, default=DEFAULT_CONCURRENCY,
        help=(
            f"Number of requests in flight at once "
            f"(default: {DEFAULT_CONCURRENCY})."
        ),
    )
    parser.add_argument(
        "--model", default=DEFAULT_MODEL,
        help=f"Model id to use (default: {DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--max-tokens", type=int, default=DEFAULT_MAX_TOKENS,
        help=(
            f"Per-request output token cap "
            f"(default: {DEFAULT_MAX_TOKENS})."
        ),
    )
    parser.add_argument(
        "--max-retries", type=int, default=DEFAULT_MAX_RETRIES,
        help=(
            f"Per-request retry attempts on transient errors "
            f"(default: {DEFAULT_MAX_RETRIES})."
        ),
    )
    parser.add_argument(
        "--yes", action="store_true",
        help="Skip the confirmation prompt before sending.",
    )
    parser.add_argument(
        "--prompts-dir", type=Path, default=PROMPTS_DIR,
        help=f"Prompts dir (default: {PROMPTS_DIR}).",
    )
    return parser.parse_args(list(argv))


def confirm_run(request_count: int, auto_yes: bool) -> bool:
    """Report how many requests will be sent and ask to proceed.

    There is no cost figure to show (the gateway has no batch
    discount and no caching to model), so we simply report the
    request count. `auto_yes` skips the prompt.
    """
    print(f"About to send {request_count} request(s) to the gateway.")
    if auto_yes:
        print("--yes set; proceeding.")
        return True
    answer = input("Proceed? [y/N] ").strip().lower()
    return answer in ("y", "yes")


def main(
    argv: Iterable[str] | None = None,
    client_factory: Callable[[int], OpenAI] = make_client,
) -> int:
    """Entry point. Returns a process exit code.

    `client_factory` is injectable so tests can substitute a fake
    client without monkeypatching the SDK.
    """
    args = parse_args(argv if argv is not None else sys.argv[1:])
    if args.package:
        targets = list(args.package)
    else:
        targets = discover_packages(args.prompts_dir)
    if args.limit is not None:
        targets = targets[: args.limit]
    if not targets:
        print("No packages need a response; nothing to do.")
        return 0
    if not confirm_run(len(targets), args.yes):
        print("Aborted.")
        return 0
    client = client_factory(args.max_retries)
    shared = load_shared_assets(args.prompts_dir)
    results = run_concurrently(
        targets=targets,
        prompts_dir=args.prompts_dir,
        shared=shared,
        client=client,
        model=args.model,
        max_tokens=args.max_tokens,
        concurrency=args.concurrency,
    )
    write_run_manifest(args.prompts_dir, results)
    print_summary(results)
    failed = sum(1 for r in results if r.status == "failed")
    return 1 if failed else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())