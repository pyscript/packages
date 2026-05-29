# ---------------------------------------------------------------------
# Parsing PEP 508 requirement strings and evaluating environment markers.
# ---------------------------------------------------------------------

heading("Parsing requirement strings")
note(
    "Each line in a <code>requirements.txt</code> follows PEP 508. "
    "<code>Requirement</code> breaks one apart into its name, extras, "
    "version specifier, and optional environment marker."
)

requirement_lines = [
    "requests>=2.31,<3",
    "django[bcrypt,argon2]>=4.2,<5",
    "numpy>=1.26 ; python_version >= '3.10'",
    "pywin32 ; sys_platform == 'win32'",
    "rich",
]

parsed_rows = []
for line in requirement_lines:
    req = Requirement(line)
    parsed_rows.append({
        "raw": line,
        "name": req.name,
        "extras": ", ".join(sorted(req.extras)) or "-",
        "specifier": str(req.specifier) or "(any)",
        "marker": str(req.marker) if req.marker else "-",
    })

display(pd.DataFrame(parsed_rows), append=True)


heading("Evaluating environment markers")
note(
    "Markers are tiny boolean expressions evaluated against the "
    "current Python environment. You can also evaluate them against "
    "a fabricated environment to ask 'would this install on Windows "
    "with Python 3.9?'."
)

marker = Marker("python_version >= '3.10' and sys_platform != 'win32'")

environments = [
    {"python_version": "3.9",  "sys_platform": "linux"},
    {"python_version": "3.10", "sys_platform": "linux"},
    {"python_version": "3.12", "sys_platform": "darwin"},
    {"python_version": "3.12", "sys_platform": "win32"},
]

eval_rows = []
for env in environments:
    eval_rows.append({
        **env,
        "marker_holds": marker.evaluate(environment=env),
    })

note(f"Evaluating: <code>{marker}</code>")
display(pd.DataFrame(eval_rows), append=True)


heading("Putting it together: would this requirement install here?")
note(
    "Combine a parsed requirement with a candidate version and a "
    "fabricated environment to predict whether a resolver would "
    "pick it."
)

req = Requirement(
    "numpy>=1.26,<2 ; python_version >= '3.10'"
)

candidate_versions = ["1.25.2", "1.26.4", "1.99.0", "2.0.0"]
target_env = {"python_version": "3.11", "sys_platform": "linux"}

resolution_rows = []
marker_holds = req.marker.evaluate(environment=target_env)
for raw in candidate_versions:
    v = Version(raw)
    in_specifier = v in req.specifier
    resolution_rows.append({
        "candidate": raw,
        "in specifier": in_specifier,
        "marker holds": marker_holds,
        "would install": in_specifier and marker_holds,
    })

note(
    f"Requirement: <code>{req}</code><br>"
    f"Target environment: <code>{target_env}</code>"
)
display(pd.DataFrame(resolution_rows), append=True)
