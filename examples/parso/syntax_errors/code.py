# ---------------------------------------------------------------------
# Parso recovers from errors, so it can report ALL of them in one pass.
# Python's built-in compile() bails out at the first syntax error;
# parso keeps going and produces a tree plus a list of issues.
# ---------------------------------------------------------------------

heading("A messy script with several problems")
note(
    "Below is some intentionally broken Python. We'll ask parso "
    "for every syntax error in one go, instead of fixing them one "
    "at a time and re-running."
)

broken_source = """\
def greet(name)
    print('hello', name)

for i in range(3)
    print(i)

continue

x = 1 +
"""

# Pretty-print the source with line numbers so the errors line up.
numbered = "<pre style='background:#f6f8fa;padding:8px'>"
for i, line in enumerate(broken_source.splitlines(), start=1):
    numbered += f"{i:>3}  {line}\n"
numbered += "</pre>"
display(HTML(numbered), append=True)

heading("Asking parso for all the issues")
note(
    "load_grammar gives us a grammar object whose iter_errors "
    "method yields one Issue per problem found. Each issue knows "
    "its message and start/end position."
)

grammar = parso.load_grammar()
module = grammar.parse(broken_source)
issues = list(grammar.iter_errors(module))

note(f"Found <strong>{len(issues)}</strong> issue(s):")
rows = []
for issue in issues:
    line, col = issue.start_pos
    rows.append(
        f"<tr><td>{line}:{col}</td>"
        f"<td><code>{issue.message}</code></td></tr>"
    )
table = (
    "<table border='1' cellpadding='6' cellspacing='0'>"
    "<tr><th>Position</th><th>Message</th></tr>"
    + "".join(rows)
    + "</table>"
)
display(HTML(table), append=True)
