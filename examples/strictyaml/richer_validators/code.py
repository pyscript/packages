# ---------------------------------------------------------------------
# Putting more of strictyaml's validator vocabulary to work, and
# constructing a YAML document directly from Python data.
# ---------------------------------------------------------------------

heading("A schema with enums, datetimes, optional keys, and patterns")
note(
    "Imagine a small task tracker. Each task has a status drawn from a "
    "fixed set, an optional due date, and a free-form tag map where "
    "the keys can be anything but the values must be strings."
)

tasks_yaml = """
# Today's tasks
- title: Write release notes
  status: in-progress
  priority: 2
  due: 2026-04-15T17:00:00
  tags:
    project: strictyaml
    area: docs

- title: Review pull requests
  status: todo
  priority: 1
  tags:
    project: strictyaml
    area: review

- title: Deploy build
  status: done
  priority: 3
  due: 2026-04-10T09:30:00
  tags:
    project: strictyaml
    area: ops
"""

task_schema = Seq(Map({
    "title": Str(),
    "status": Enum(["todo", "in-progress", "done"]),
    "priority": Int(),
    Optional("due"): Datetime(),
    "tags": MapPattern(Str(), Str()),
}))

tasks = load(tasks_yaml, task_schema)

note("Parsed tasks (note the real <code>datetime</code> objects):")
for task in tasks:
    due = task.data.get("due", "—")
    display(HTML(
        f"<li><strong>{task['title'].data}</strong> "
        f"[{task['status'].data}] priority {task['priority'].data}, "
        f"due {due}</li>"
    ), append=True)

heading("Filtering with the typed data")
todo_or_active = [
    t.data["title"] for t in tasks
    if t.data["status"] in ("todo", "in-progress")
]
note(f"Open tasks: <strong>{', '.join(todo_or_active)}</strong>")

heading("Building YAML from a Python dict")
note(
    "Use <code>as_document</code> to turn native Python data into a "
    "YAML document. Combine with a schema to validate as you build."
)

new_task = as_document(
    {
        "title": "Ship 1.8",
        "status": "todo",
        "priority": 1,
        "tags": {"project": "strictyaml", "area": "release"},
    },
    schema=Map({
        "title": Str(),
        "status": Enum(["todo", "in-progress", "done"]),
        "priority": Int(),
        "tags": MapPattern(Str(), Str()),
    }),
)

display(HTML(f"<pre>{new_task.as_yaml()}</pre>"), append=True)
