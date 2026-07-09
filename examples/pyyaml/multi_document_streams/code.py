# ---------------------------------------------------------------------
# A single YAML stream can hold many documents, separated by '---'.
# This is how Kubernetes manifests, Ansible playbooks, and CI
# pipelines often bundle multiple resources into one file.
# ---------------------------------------------------------------------

heading("Multi-document YAML: a tiny deployment manifest")
note(
    "Three YAML documents in one stream, each describing a different "
    "kind of resource. <code>yaml.safe_load_all</code> returns an "
    "iterator yielding one Python object per document."
)

manifest = """
---
kind: Service
name: weather-api
port: 8080
---
kind: Deployment
name: weather-api
replicas: 3
image: weather-api:2.5.0
---
kind: ConfigMap
name: weather-api-config
data:
  log_level: info
  cache_ttl: 300
"""

# safe_load_all yields documents one at a time, so it scales to large
# files. We materialize the iterator into a list here for inspection.
documents = list(yaml.safe_load_all(manifest))

note(f"Found <strong>{len(documents)}</strong> documents in the stream.")
for doc in documents:
    note(
        f"<code>{doc['kind']}</code> &rarr; "
        f"<strong>{doc['name']}</strong>"
    )

heading("Writing several documents back out")
note(
    "Use <code>yaml.safe_dump_all</code> to serialize an iterable "
    "of Python objects as a multi-document YAML stream. "
    "<code>explicit_start=True</code> writes the leading "
    "<code>---</code> before each document."
)

# Bump the deployment's replica count and re-emit the whole stream.
for doc in documents:
    if doc["kind"] == "Deployment":
        doc["replicas"] = 5

updated = yaml.safe_dump_all(
    documents,
    default_flow_style=False,
    sort_keys=False,
    explicit_start=True,
)

display(HTML(f"<pre>{updated}</pre>"), append=True)
