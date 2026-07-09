# ---------------------------------------------------------------------
# Branching on the distribution family using `id()` and `like()`.
# ---------------------------------------------------------------------

heading("Raw os-release contents")
note(
    "<code>distro.os_release_info()</code> returns the parsed "
    "key-value pairs from <code>/etc/os-release</code>. This is "
    "useful when you need a field that doesn't have a dedicated "
    "helper (for example, <code>VARIANT</code> or <code>BUG_REPORT_URL</code>)."
)

os_release = distro.os_release_info()
display(os_release or {"(no os-release available in this environment)": ""},
        append=True)


heading("Picking a code path by distribution family")
note(
    "Many tools install differently on Debian-likes vs. Red Hat-likes. "
    "<code>distro.id()</code> gives the specific distribution, while "
    "<code>distro.like()</code> returns a space-separated list of "
    "parent families (e.g. <code>'debian'</code> for Ubuntu, or "
    "<code>'rhel fedora'</code> for CentOS Stream)."
)


def install_command_for(distro_id, distro_like):
    """Pick a plausible package install command for a given distro."""
    family = f"{distro_id} {distro_like}".split()
    if "debian" in family or "ubuntu" in family:
        return "sudo apt-get install <package>"
    if "rhel" in family or "fedora" in family or "centos" in family:
        return "sudo dnf install <package>"
    if "arch" in family:
        return "sudo pacman -S <package>"
    if "alpine" in family:
        return "sudo apk add <package>"
    return "(no known package manager for this system)"


# Demonstrate the logic on a few representative distributions, since
# the sandbox itself won't report as any of them.
samples = [
    ("ubuntu", "debian"),
    ("debian", ""),
    ("centos", "rhel fedora"),
    ("fedora", ""),
    ("manjaro", "arch"),
    ("alpine", ""),
]

rows = "<tr><th>id</th><th>like</th><th>install command</th></tr>"
for sample_id, sample_like in samples:
    cmd = install_command_for(sample_id, sample_like)
    rows += (
        f"<tr><td><code>{sample_id}</code></td>"
        f"<td><code>{sample_like or '-'}</code></td>"
        f"<td><code>{cmd}</code></td></tr>"
    )
display(HTML(f"<table border='1' cellpadding='4'>{rows}</table>"), append=True)

note(
    f"On the actual host, <code>distro.id()</code> is "
    f"<code>{distro.id() or '(empty)'}</code> and "
    f"<code>distro.like()</code> is "
    f"<code>{distro.like() or '(empty)'}</code>, so "
    f"<code>install_command_for(...)</code> would suggest: "
    f"<code>{install_command_for(distro.id(), distro.like())}</code>."
)
