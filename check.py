"""
Serve a package's generated examples in live PyScript editors, so a
reviewer can run them in a browser before approving the branch.

Two ways to run it:

    python check.py pandas      # test a named package
    python check.py             # infer the package from the branch

With no argument, the script asks git for the current branch. A
branch named `examples/<package>` means we're testing `<package>`.
On `main` (or any branch that isn't an `examples/...` branch) the
script can't infer a package and asks you to name one.

Once the package is known, the script starts a local web server and
prints a URL with the package pre-filled as a query argument. Open
that URL and the page will:

1. Read the target package from the `?package=` query argument.
2. Fetch the package's examples from the server's `/examples.json`
   endpoint, which reads `examples/<package>/` on disk (the source
   of truth during review, before `build_data.py` has baked them
   into the published API).
3. Fill a dropdown with the package's examples, in order.
4. For the selected example, build a fresh PyScript editor wired up
   with the example's setup, code, and configuration. Changing the
   dropdown rebuilds the editor for the newly selected example.

The server serves the repository root statically and reads
`examples/<package>/` from the same root for the examples endpoint.
Run this from the repo root, like the other scripts.
"""

import argparse
import json
import subprocess
import sys
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Iterable
from urllib.parse import parse_qs

import build_data

# The repository root is the directory this script lives in.
REPO_ROOT = Path(__file__).resolve().parent

# The branch-name prefix that marks a per-package example branch.
BRANCH_PREFIX = "examples/"

# The path at which the generated check page is served. Anything not
# matching this falls through to ordinary static file serving.
CHECK_PATH = "/check"

# The path at which the package's examples are served as JSON. The
# page fetches this rather than reading the published `api/` files,
# so it reflects the current state of `examples/<package>/` on disk.
EXAMPLES_PATH = "/examples.json"

# The PyScript release whose editor and runtime we load. Pinned so a
# future PyScript change can't silently alter the test harness.
PYSCRIPT_VERSION = "2026.6.1"

DEFAULT_PORT = 8000


def current_branch(repo_root: Path) -> str | None:
    """Return the current git branch name, or None if undetermined.

    Returns None rather than raising when git fails or we're not on
    a branch, so the caller can fall back to asking for a package.
    """
    completed = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return None
    branch = completed.stdout.strip()
    return branch or None


def package_from_branch(branch: str | None) -> str | None:
    """Extract a package name from an `examples/<package>` branch.

    Returns None for any branch that isn't an example branch (such
    as `main`), signalling that the caller must ask for a package.
    """
    if branch is None:
        return None
    if not branch.startswith(BRANCH_PREFIX):
        return None
    package = branch[len(BRANCH_PREFIX):]
    return package or None


def resolve_package(
    argument: str | None, repo_root: Path,
) -> str:
    """Decide which package to test, from the argument or the branch.

    An explicit argument always wins. Otherwise we infer from the
    branch. If neither yields a package, raise SystemExit with a
    message telling the operator to name one.
    """
    if argument:
        return argument
    branch = current_branch(repo_root)
    package = package_from_branch(branch)
    if package:
        return package
    where = f"branch '{branch}'" if branch else "an unknown branch"
    raise SystemExit(
        f"On {where}, so no package could be inferred. "
        "Re-run with a package name, e.g. `python check.py pandas`.",
    )


def build_page(package: str) -> str:
    """Return the HTML for the check page for a given package.

    The package name is baked into the page as a fallback, but the
    page reads the live `?package=` query argument at runtime so the
    same page works for any package. The page fetches the examples
    from the server's examples endpoint, fills a dropdown, and
    (re)builds a PyScript editor for the selected example.
    """
    base = f"https://pyscript.net/releases/{PYSCRIPT_VERSION}"
    return _PAGE_TEMPLATE.format(
        package=package,
        pyscript_css=f"{base}/core.css",
        pyscript_js=f"{base}/core.js",
        examples_path=EXAMPLES_PATH,
    )


# The check page. The Python `.format()` call fills in the package
# name and the pinned PyScript asset URLs; all the literal braces in
# the embedded JavaScript are doubled so they survive formatting.
_PAGE_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport"
          content="width=device-width, initial-scale=1" />
    <title>PyScript example check</title>
    <link rel="stylesheet" href="{pyscript_css}" />
    <script type="module" src="{pyscript_js}"></script>
    <style>
      body {{
        font-family: system-ui, sans-serif;
        max-width: 60rem;
        margin: 2rem auto;
        padding: 0 1rem;
      }}
      label {{
        font-weight: bold;
      }}
      select {{
        font-size: 1rem;
        padding: 0.25rem;
        margin: 0.5rem 0 1.5rem;
      }}
      #status {{
        color: #b00;
      }}
    </style>
  </head>
  <body>
    <h1>Checking package: <code id="package-name"></code></h1>
    <p>
      <label for="example-picker">Example:</label>
      <select id="example-picker"></select>
    </p>
    <h2 id="example-title"></h2>
    <p id="status"></p>
    <div id="editor-area"></div>

    <script type="module">
      // The package baked in at generation time, used only if the
      // query argument is absent.
      const fallbackPackage = "{package}";

      // A monotonically increasing counter gives each rebuilt editor
      // a unique environment name, so a freshly selected example
      // never inherits a previous example's namespace or config.
      let editorGeneration = 0;

      function getPackageName() {{
        // Prefer the live query argument; fall back to the baked-in
        // package name.
        const params = new URLSearchParams(window.location.search);
        return params.get("package") || fallbackPackage;
      }}

      function setStatus(message) {{
        document.getElementById("status").textContent = message;
      }}

      async function loadExamples(packageName) {{
        // Fetch the package's examples from the server, which reads
        // `examples/<package>/` on disk. This is the source of
        // truth during review: the published `api/` files are only
        // rebuilt by build_data.py after PRs are merged.
        const url = `{examples_path}?package=${{packageName}}`;
        const response = await fetch(url);
        if (!response.ok) {{
          throw new Error(
            `Could not load examples (status ${{response.status}}).`
          );
        }}
        const data = await response.json();
        return data.examples || [];
      }}

      function buildEditor(example) {{
        // Destroy any existing editor and build a fresh one for the
        // given example. Setup code (if present) runs invisibly in a
        // setup editor sharing a unique environment with the visible
        // code editor.
        //
        // Editors are built with createElement and appended. Scripts
        // created this way are live (unlike scripts assigned via
        // innerHTML, which the browser treats as inert), and
        // PyScript's observer picks them up. Building the markup as
        // an innerHTML string is avoided deliberately: a literal
        // closing script tag in such a string would prematurely
        // terminate this page's own inline script.
        const area = document.getElementById("editor-area");
        area.innerHTML = "";
        editorGeneration += 1;
        const env = `check_${{editorGeneration}}`;
        const config = JSON.stringify(example.config || {{}});

        // Each example gets its own target div, and the editor's
        // `target` attribute tells PyScript to render the editor
        // (and its output area) inside that div. The example's
        // display() calls then land in the editor's own output area,
        // so we don't need to bind anything in the Python namespace.
        // See: https://docs.pyscript.net/2026.3.1/user-guide/editor/
        //      #custom-rendering-location
        const targetId = `output-${{editorGeneration}}`;
        const target = document.createElement("div");
        target.id = targetId;
        const bind = `__pyscript_display_target__ = "${{targetId}}"\\n`;

        if (example.setup) {{
          // Only the setup editor carries the config; the visible
          // editor inherits it via the shared environment.
          const setup = document.createElement("script");
          setup.setAttribute("type", "py-editor");
          setup.setAttribute("env", env);
          setup.setAttribute("setup", "");
          setup.setAttribute("config", config);
          setup.textContent = bind + example.setup;
          area.appendChild(setup);
        }}

        const editor = document.createElement("script");
        editor.setAttribute("type", "py-editor");
        editor.setAttribute("env", env);
        editor.setAttribute("target", targetId);
        // Without a setup editor, the visible editor needs the config.
        if (!example.setup) {{
          editor.setAttribute("config", config);
          editor.textContent = bind + (example.code || "");
        }}
        editor.textContent = example.code || "";
        area.appendChild(editor);

        // The target div sits after the editors; PyScript renders
        // each editor's CodeMirror surface and output area inside it.
        area.appendChild(target);
      }}

      function showExample(examples, index) {{
        // Update the title and (re)build the editor for the example
        // at the given index.
        const example = examples[index];
        document.getElementById("example-title").textContent =
          example.title || "";
        buildEditor(example);
      }}

      async function main() {{
        const packageName = getPackageName();
        document.getElementById("package-name").textContent =
          packageName;
        let examples;
        try {{
          examples = await loadExamples(packageName);
        }} catch (error) {{
          setStatus(error.message);
          return;
        }}
        if (examples.length === 0) {{
          setStatus(
            `The package "${{packageName}}" has no examples to check.`
          );
          return;
        }}
        const picker = document.getElementById("example-picker");
        examples.forEach((example, index) => {{
          const option = document.createElement("option");
          option.value = String(index);
          option.textContent = example.title || `Example ${{index + 1}}`;
          picker.appendChild(option);
        }});
        picker.addEventListener("change", () => {{
          showExample(examples, Number(picker.value));
        }});
        // Show the first example on load.
        picker.value = "0";
        showExample(examples, 0);
      }}

      // Run after the full page load, by which point PyScript's
      // module script has executed and its observer is watching for
      // editor tags. Running main() inline during initial parse can
      // inject the first editor before PyScript is ready to see it,
      // leaving the first example blank until the dropdown changes.
      if (document.readyState === "complete") {{
        main();
      }} else {{
        window.addEventListener("load", main);
      }}
    </script>
  </body>
</html>
"""


class CheckRequestHandler(SimpleHTTPRequestHandler):
    """Serve the repo root statically, plus the check page and the
    examples endpoint at the configured paths.

    Static files (the published `api/`, any other tracked content)
    are handled by the standard static file server. The check page
    and `/examples.json` are served from in-memory and on-disk data
    respectively.

    Every response carries the two cross-origin isolation headers
    PyScript needs for SharedArrayBuffer (which the editor's worker-
    based execution relies on). Without these on *every* response,
    the page is not cross-origin isolated and the editor fails.
    """

    # Set by the factory in `serve` so the handler knows which page
    # to emit. A class attribute because the handler is instantiated
    # per-request by the server.
    page_html: str = ""

    def end_headers(self) -> None:
        """Add cross-origin isolation headers to every response."""
        self.send_header(
            "Cross-Origin-Opener-Policy", "same-origin",
        )
        self.send_header(
            "Cross-Origin-Embedder-Policy", "require-corp",
        )
        super().end_headers()

    def do_GET(self) -> None:
        """Route /check, /examples.json, else static file serving."""
        path, _, query = self.path.partition("?")
        if path == CHECK_PATH:
            self._serve_bytes(
                self.page_html.encode("utf-8"),
                "text/html; charset=utf-8",
            )
            return
        if path == EXAMPLES_PATH:
            self._serve_examples(query)
            return
        super().do_GET()

    def _serve_bytes(self, body: bytes, content_type: str) -> None:
        """Write a 200 response with the given body and content type."""
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_examples(self, query: str) -> None:
        """Return the requested package's examples as JSON.

        The package comes from the `?package=` query argument so
        one running server can serve any package without restart.
        Reads `examples/<package>/` on disk via
        `build_data.load_examples`.
        """
        params = parse_qs(query)
        package_name = (params.get("package") or [""])[0]
        if not package_name:
            self._serve_error(400, "missing 'package' query argument")
            return
        try:
            examples = build_data.load_examples(package_name)
        except Exception as exc:
            self._serve_error(500, str(exc))
            return
        payload = json.dumps({"examples": examples}).encode("utf-8")
        self._serve_bytes(payload, "application/json")

    def _serve_error(self, status: int, message: str) -> None:
        """Write a JSON error response with the given status."""
        body = json.dumps({"error": message}).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def make_handler_class(page_html: str, repo_root: Path):
    """Build a request-handler class bound to the page and root.

    `SimpleHTTPRequestHandler` serves the directory given to its
    constructor; we use `functools.partial` to pin it to the repo
    root, and a subclass to carry the page HTML.
    """
    class _Handler(CheckRequestHandler):
        page_html = ""

    _Handler.page_html = page_html
    return partial(_Handler, directory=str(repo_root))


def serve(
    package: str,
    repo_root: Path,
    port: int,
    open_browser: bool = True,
) -> None:  # pragma: no cover - exercised manually, not in tests.
    """Start the local server and print the URL to open.

    `package` is used only to compose the URL printed to the
    operator. The server itself is package-agnostic: each request
    to /examples.json names the package in its query string, so a
    single running server can show any package as you change the
    `?package=` query and reload.
    """
    page_html = build_page(package)
    handler = make_handler_class(page_html, repo_root)
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    url = (
        f"http://localhost:{port}{CHECK_PATH}?package={package}"
    )
    print(f"Checking package: {package}")
    print(f"Open this URL in your browser:\n\n    {url}\n")
    print(
        "To check a different package, change the `package` query "
        "argument in the URL and reload.",
    )
    print("Press Ctrl-C to stop the server.")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
    finally:
        server.server_close()


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    """Parse the command-line interface."""
    parser = argparse.ArgumentParser(
        description=(
            "Serve a package's generated examples in live PyScript "
            "editors for review."
        ),
    )
    parser.add_argument(
        "package",
        nargs="?",
        default=None,
        help=(
            "The package to test. If omitted, inferred from an "
            "`examples/<package>` git branch."
        ),
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Port for the local server (default: {DEFAULT_PORT}).",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't try to open a browser automatically.",
    )
    return parser.parse_args(list(argv))


def main(
    argv: Iterable[str] | None = None,
    serve_fn=serve,
) -> int:
    """Entry point. Returns a process exit code.

    `serve_fn` is injectable so tests can verify the wiring without
    starting a blocking server.
    """
    args = parse_args(argv if argv is not None else sys.argv[1:])
    package = resolve_package(args.package, REPO_ROOT)
    serve_fn(
        package=package,
        repo_root=REPO_ROOT,
        port=args.port,
        open_browser=not args.no_browser,
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())