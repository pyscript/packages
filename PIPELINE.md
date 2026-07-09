# Generating PyScript Package Examples - Pipeline Runbook

This document walks through generating PyScript examples for many
packages at once, using the LLM-assisted pipeline that lives in this
repository. It is written for an operator running the pipeline
end-to-end without supervision; a separate "Reviewing PRs" section
near the end covers what someone reviewing the resulting pull
requests needs to know.

If you only want to run the static site locally, or contribute a
single hand-written example via a regular PR, see the project's main
[README](README.md) instead. This runbook is for the automated content
generation workflow only.

The pipeline involves mostly-unattended LLM runtime plus however long
you spend reviewing the resulting GIT branches. Expect to spread it
across a working day, with the LLM step running in the background
while you do other work.

## What this pipeline does

The site catalogues hundreds of Python packages and wants short,
illustrative examples for each one that's supported by PyScript.
Writing those examples by hand for every package would take forever,
so we use an LLM to draft them, then a human reviews each one before
it lands.

The pipeline is five steps:

1. `build_data.py` - refresh the catalogue of packages and their
   support status from upstream sources.
2. `generate_examples.py` - for packages that are green-status but
   don't yet have examples, build a per-package prompt by scraping
   the package's README and documentation.
3. `run_llm.py` - send each prompt to the LLM and capture the reply.
4. `apply_llm_response.py --branch-per-package` - validate each
   reply, write the examples into the repos, and put each package's
   examples on its own git branch ready for review.
5. Review each branch by hand, open one PR per package, and once
   they're merged, run `build_data.py` again to bake the new
   examples into the published API.

Steps 1, 2, 3, and 4 are run from the command line. Step 5 is a
human review and a manual PR submission per package. The pipeline
is deliberately designed to keep humans in the loop, because the
site is curated and the LLM output needs scrutiny before it ships.

## Before you start: first-time setup

You only need to do this once.

### Clone the repository

If you have push access to the canonical repository, clone it
directly:

```sh
git clone git@github.com:pyscript/packages.git
cd packages
```

If you don't have push access, fork the repository on GitHub first,
then clone your fork. Add the canonical repository as an `upstream`
remote so you can keep your fork up to date:

```sh
git clone git@github.com:<YOUR_USERNAME>/packages.git
cd packages
git remote add upstream git@github.com:pyscript/packages.git
git fetch upstream
```

Either way, make sure your `main` branch is up to date with
`pyscript/packages` before starting a run.

### Install Python dependencies

The pipeline uses Python 3.12 or newer. Set up a virtual environment
and install the requirements:

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Set the LLM gateway environment variables

The LLM step talks to an OpenAI-compatible gateway. You need two
environment variables set whenever you run `run_llm.py`:

```sh
export PROXY_API_KEY=<your gateway API key>
export PROXY_BASE_URL=<the gateway URL>
```

Put these in your shell's startup file if you'll be doing this work
regularly. The script refuses to run without them, with a clear
message rather than a confusing failure later.

Depending on your AI infrastructure, you may need to be working
within your company's VPN - otherwise requests to you AI endpoints
may not work.

### Sanity-check the gateway

Before doing real work, confirm the gateway is reachable:

```sh
python gateway_probe.py
```

If you see "gateway is working" and a usage summary, you're set. If
you see a 401 or 403, double-check your API key. If you see a
connection error, check your network, your VPN and the 
`PROXY_BASE_URL`.

## Running the pipeline

The five steps in order. After each step you should pause and check
the output before moving on. The pipeline is designed to be safe to
re-run, so if anything looks wrong you can fix the cause and re-run
the step without losing progress.

### Step 1: refresh the catalogue

```sh
python build_data.py
```

This fetches the latest Pyodide support graph, the community-
submitted status updates from the Google Form, and the top-100 PyPI
download stats, then writes them to `api/`. It always runs all four
of its internal sub-steps; that's normal.

**Check before moving on:**

- Run `git status` and look at what changed under `api/`. New
  packages added, status changes, or note updates are all
  expected. Major unexpected churn is not.
- If you're happy with the changes, commit them now: this step is
  about the *catalogue*, not about generating examples.

### Step 2: generate prompts

```sh
python generate_examples.py
```

This looks at every green-status package in `api/all.json` that
doesn't already have examples, and builds a prompt under
`prompts/<package>/` containing the package's README, documentation
links, and metadata. It's resumable - if you've already run it for a
package, it skips that package. To re-run for a single package, pass
`--package <name>`; to force a re-run regardless, pass `--force`.

The entire `prompts/` directory is gitignored, so this step never
touches what would be committed.

**Check before moving on:**

- Look at the script's output. It tells you how many prompts were
  written. For an incremental run it should be small.
- If a package was marked "no usable documentation found" with a
  `.warning` marker, that's a flag, not an error. The LLM will be
  asked to rely on its own knowledge for those packages, and the
  resulting examples will be flagged for extra-careful review.

### Step 3: send prompts to the LLM

```sh
python run_llm.py
```

This sends each per-package prompt to the LLM and writes the reply
to `prompts/<package>/response.toml`. The script:

- Asks you to confirm before sending, showing the request count.
  Type `y` to proceed.
- Sends requests concurrently (default: 4 at a time) so a few
  hundred packages finish in tens of minutes rather than hours.
- Retries transient failures automatically.
- Writes a `.run_failed` marker for any package that fails after
  retries, so you can see what didn't work.
- Is resumable: a package with a `response.toml` is skipped on
  re-run, so an interrupted run picks up where it left off.

A junior dev can leave this running and come back to it. If you
close your laptop or lose network mid-run, just re-run the command.

**Check before moving on:**

- The script prints a summary at the end: how many succeeded and
  how many failed. A small number of failures is normal; a large
  number means something's wrong (often: a rate limit being hit at
  the chosen concurrency).
- If you saw failures, re-run the script. It'll only retry the
  failed packages. If they fail again, lower the concurrency:
  `python run_llm.py --concurrency 2`.
- Spot-check a handful of `prompts/<package>/response.toml` files
  by eye. They should be readable TOML containing 1-3 examples
  each. Garbled output here is rare but indicates a serious problem
  with the LLM or the prompt; stop and ask for help if you see it.

### Step 4: validate responses and put each package on its own branch

```sh
python apply_llm_response.py --branch-per-package
```

This reads each `response.toml`, validates its structure (TOML
parses, Python files parse, the various rules about IPython imports
and helpers are respected), writes the examples to
`examples/<package>/`, and creates a git branch named
`examples/<package>` with exactly one commit for each successful
package. Failed validations produce no branch - they're listed in
the script's output instead. The script ends with a summary block
listing every branch ready to push.

The script requires the working tree to be clean and the current
branch to be `main`. If it isn't, it refuses to start with a clear
message; commit or stash anything outstanding first.

**Check before moving on:**

- Read the summary. It lists each created branch by name. Branches
  for packages that were flagged low-context (see step 2) are
  marked `[NEEDS REVIEW]`.
- If any packages failed validation, the script tells you why. The
  most common cause is the LLM producing TOML that doesn't quite
  follow the rules. For those, you can either re-run the LLM step
  for just that package and try again, or fix it by hand:

```sh
rm prompts/<package>/response.toml
python run_llm.py --package <package>
python apply_llm_response.py --branch-per-package --package <package>
```

### Step 5: review and PR each branch

Now the human work begins. For every branch the script created, you
should look at it, decide whether the examples are good, and either
open a PR or fix and re-run.

To list the branches the pipeline created:

```sh
git branch --list 'examples/*'
```

Pick one and check it out:

```sh
git checkout examples/<package_name>
git log -1
git diff main..HEAD
```

The helpful `check.py` script will load the PyScript editor
environment for each example, so you can check it works in the
browser.

When in the branch just run:

```sh
python check.py
```

Your browser should open with the expected first example.

If you find yourself in the main branch and need to try out a
specific package, just pass it as an argument:

```sh
python check.py pandas
```

Finally, when in the browser, if you append `?package=<package_name>`
to the URL, the examples for that the named package will be displayed
(if available).

For each branch, look at the three files per example
(`config.toml`, `setup.py`, `code.py`) and ask:

- Does the code do something genuinely useful with the package?
- Does it actually run in PyScript? (You can copy the code into a
  local PyScript page to verify, or rely on review judgement for
  small low-risk examples.)
- Are the explanations clear and not hallucinated?
- Are the helpers (`display`, `heading`, `note`) used as intended,
  not redefined?
- Is the example progression sensible: introduction first, then
  more involved usage?

If the branch is good, push it and open a PR.

**If you have push access to the canonical repository:**

```sh
git push origin examples/<package_name>
```

Then open a PR via the GitHub UI from `examples/<package_name>` into
`main`.

**If you're working from a fork:**

Your `origin` points to your fork, not to `pyscript/packages`.
That's fine - push to your fork and PR from there:

```sh
git push origin examples/<package_name>
```

Then on GitHub, open a PR from
`<YOUR_USERNAME>/packages:examples/<package_name>` into
`pyscript/packages:main`. The GitHub UI will offer this as a
"compare across forks" PR.

If the branch needs changes, edit the files on the branch, commit,
and push again. The PR will update automatically.

Repeat for every branch. You can do this gradually - the branches
sit on your fork or the canonical repo waiting for review, so
there's no rush.

## Reviewing PRs

This section is for someone reviewing the example PRs the operator
has opened. You don't need to have run any of the pipeline yourself
to review; you only need a clone of the repository and Python 3.12
or newer.

### Get the branch locally

Fetch any branches the operator has pushed but you don't yet have
locally, then check out the branch for the package you want to
review:

```sh
git fetch
git checkout examples/<package>
```

If you're reviewing a PR from a contributor's fork, you can fetch
their branch directly from the PR page on GitHub (the "checkout
with command line" link gives you the right `git fetch` invocation
to pull their branch into a local `pr/<n>` branch).

### Run the examples locally

From the repository root:

```sh
python check.py
```

With no argument and a checked-out `examples/<package>` branch,
`check.py` infers the package name from the branch and starts a
local web server, printing a URL to open. The page loads each of
the package's examples into a [PyScript editor](
https://docs.pyscript.net/2026.3.1/user-guide/editor/) using a
dropdown to switch between them.

To actually run an example: scroll to the bottom of the editor for
that example, hover over it, and click the play button that
appears at the bottom-right corner of the editor toolbar. The
example's setup runs invisibly first, then the visible code runs,
and any output appears beneath the editor.

If port 8000 is already in use on your machine, pass `--port` to
pick a different one:

```sh
python check.py --port 8765
```

To check more than one package without restarting the server,
change the `package` query argument in the URL in your browser and
reload. For example, after starting the server with the `pandas`
branch checked out, you can also look at `numpy`'s examples (if
they exist on disk) by changing the URL's `?package=pandas` to
`?package=numpy` and reloading.

### What to look at

Use the same review checklist as the operator (see step 5 above):
does each example do something genuinely useful with the package;
does it run cleanly in PyScript; are the explanations clear and
not hallucinated; are the helpers used as intended; does the
progression of examples make sense.

### How to give feedback

If you have small, concrete improvements - typo fixes, clearer
wording, a better example variant - the simplest path is to push
commits directly to the `examples/<package>` branch on the PR.
The PR will update automatically.

If you have larger concerns or aren't sure about a change, leave a
comment on the PR. The operator (or another reviewer) can act on
the feedback.

If the example needs a fundamentally different approach and you
don't want to rewrite it yourself, request changes on the PR with
a clear description of what's missing or wrong, and the operator
can re-run that single package through the pipeline (see "I want
to re-run the pipeline for one specific package" in the
troubleshooting section) to produce a fresh attempt.

### Editing the examples directly

The files you'll be editing live under `examples/<package>/`, one
sub-directory per example. Each sub-directory has at most three
files: `config.toml` (PyScript runtime config), `code.py` (the
visible code), and an optional `setup.py` (invisible boilerplate
that runs before the code). The display order is fixed by
`order.json` at the package root if present, otherwise alphabetical
by directory name.

After editing, re-run `python check.py` (or just reload the page
if the server is still running) to see your changes take effect.
A page reload re-fetches the examples from disk, so you don't have
to restart the server between edits.

## After PRs are merged: re-bake examples into the API

Once one or more example PRs have been merged into `main`, run
`build_data.py` again to fold the new examples into the published
API:

```sh
git checkout main
git pull
python build_data.py
git add api/
git commit -m "Bake newly merged examples into the API"
```

This commit can go through a regular PR; it doesn't need any
special branching.

## Troubleshooting

### "The cleanliness check refuses to start"

`apply_llm_response.py --branch-per-package` requires a clean
working tree on `main`. If you have uncommitted changes, commit or
stash them. If you're on a different branch, switch to `main`. If
git reports untracked files, check whether they should be added to
`.gitignore` (most likely yes, if they're from the pipeline).

### "A package keeps failing the LLM step"

Lower the concurrency and try just that package:

```sh
python run_llm.py --concurrency 1 --package <name>
```

If it still fails, look at the error message in
`prompts/<name>/.run_failed`. A 4xx response means a problem with
the request shape (rare; ask for help); a 5xx or timeout is usually
transient and worth retrying after a few minutes.

### "A package keeps failing validation"

The LLM's output for that package is not following the rules.
Options:

- Delete the response and re-run the LLM step. Sometimes a re-roll
  produces clean output.

```sh
rm prompts/<name>/response.toml
python run_llm.py --package <name>
```

- If repeated re-rolls fail, look at
  `prompts/<name>/response.toml` by hand. The validator's error
  message tells you which rule was broken. Often you can fix the
  TOML by editing it, then re-run `apply_llm_response.py`.

### "I want to re-run the pipeline for one specific package"

All four scripts support `--package <name>`. You can chain them:

```sh
python generate_examples.py --package <name> --force
python run_llm.py --package <name>
python apply_llm_response.py --branch-per-package --package <name> --force
```

`--force` is needed where a previous run already produced output -
without it, the scripts skip work that's already been done.

### "I want to abandon a branch and start over for a package"

```sh
git branch -D examples/<name>
git push origin --delete examples/<name>  # if you pushed it
```

Then re-run from step 2.

### "The branches were created but I want to discard them all and start over"

```sh
for branch in $(git branch --list 'examples/*' | sed 's/^[* ]*//'); do
    git branch -D "$branch"
done
```

This deletes only local branches. If any were pushed to a remote,
delete them there too.

### "The script complains about `PROXY_API_KEY` not being set"

You haven't exported the gateway environment variables for this
shell session. See first-time setup above.

### "I want to see what the pipeline did on its last run"

Each script writes a manifest:

- `prompts/_run_manifest.json` - what the LLM step did.
- `examples/_apply_manifest.json` - what the apply step did.

Both are gitignored; they're only there to help you.

## When to ask for help

A junior dev can usually work through everything above without
help. Reach out when:

- The LLM's output for many packages is consistently misshapen
  (suggests a prompt or model regression that needs investigation,
  not a one-off fix).
- The gateway is returning errors you don't understand and they're
  not transient.
- Validation rules seem wrong for a real, well-formed example
  (suggests a validator bug worth fixing rather than working
  around).
- You're about to merge a large batch of example PRs and want a
  second pair of eyes.

Everything else - failed runs, individual packages misbehaving,
branches that need redoing - is part of the normal job.

## Limitations and cost - an honest reflection

This runbook describes a pipeline that is easy to *run* across a *huge*
number of packages but whose output is very hard to *judge*. That is what you
get when quantitative - packages processed, minutes elapsed - is valued
above qualitative: whether an example teaches anybody anything.

Two worlds meet here. The first is deterministic: scraping, validation,
branch creation. Traditional runbook work. It either runs or it breaks, and
when it breaks it's obvious. The second is the LLM, whose output no amount of
automated validation can vouch for. We want examples with three attributes:
meaningful, useful and trusted. The pipeline was built on the hypothesis
that AI would get us there quicker, easier and more accurately than
paying developers to plan and write content. It delivered "quicker". It has
not made any of the three attributes easier to achieve, and it has
muddied our ability to tell whether we have achieved them at all.

### What the numbers say

We started with the 325 packages Pyodide officially supports. 203 came
back with output we had enough confidence in to call content. Of those,
a human reviewer judged 111 good enough in the browser to become pull
requests. 92 consumed reviewer attention and produced nothing.

The low survival rate is also a misleading one, because "worked in the
browser" was never the bar. The educational quality of those 111 has not
been assessed. We know they execute. Executing is a precondition for
being useful, not a demonstration of it. So of meaningful, useful and
trusted, the pipeline has produced evidence for none - only for the
thing that must be true before any of the three can be checked: does it run?
That's easy to check but, on its own, worth nothing.

### The shape of the work

Writing a good example is reflective craft. You learn enough of the
package to reveal something interesting and useful about it, and the learning
is where the value lies. Reviewing two hundred machine-drafted examples
is not that. It is auditing, at the machine's tempo, of content that
looks plausible but may not be.

That is a cost that's easy to miss. 

Here's a concrete example: the prompt tells the model to put
the package imports at the top of the first example, where a reader will
see them. It frequently buries them in `setup.py` instead, where they
run invisibly. The example still executes. It parses, it produces
output, it passes every validator we have. It is also useless as
teaching, because the one line showing you how to reach the library has
been hidden. Nothing catches this but a human reading with attention -
and the reviewer must read *every* example that way, because there is no
telling in advance which ones are affected.

Cory Doctorow has a name for this, borrowed from automation theory: the
*reverse centaur*. A centaur is a person assisted by a machine that
shoulders something onerous. A reverse centaur is a machine assisted by
a person, who works at the machine's pace and carries the blame when the
machine is wrong. His example is a freelancer commissioned to write ten
"best of summer" listicles on a short deadline. Everyone understood the
job was not to write them but to supervise a chatbot, and nobody costed
the fact that checking ten lists of fifteen items is slow, laborious
human work. The pieces went out full of hallucinations nobody caught.
Step 5 of this runbook has the same shape.

### On "quicker"

We have not measured wall-clock time end to end,
review included. Until someone does, "quicker" is an impression formed
watching `run_llm.py` finish, not a fact. The `[NEEDS REVIEW]` marker in
step 4 is the pipeline quietly admitting it knows when it has produced
work of which it is unconfident.

I tried to close the loop - a second LLM pass to check and refine the
first, hoping accuracy could be automated away. Writing a prompt that
reliably yields accurate technical content across a multitude of diverse
packages turns out to be very hard,
and a human has to check the result regardless. We would have added a
step, a cost, and a second source of plausible error, and removed
nothing.

## Resolutions considered

Two obvious moves, both of which fail.

**Replace review with automated tests.** We validate that Python parses.
We don't validate that it runs in a browser and produces output. A non-trivial
headless Playwright runner in CI would catch missing modules, wrong
signatures, output that never appears, and is worth building for its own
sake. It does not save the reviewer. Someone still reads every example
that passes, because passing was never the goal, and someone still
investigates every example that fails. The work is merely re-sorted, not
removed. The `setup.py` problem is invisible to any test we could write:
the code is correct, but the pedagogy is wrong.

**Harvest rather than generate.** Almost every package on PyPI already
ships examples - README snippets, docstrings, `examples/` directories.
Maintainer-written, known-correct, already licensed. Why not reuse them?
Because they must run *in the browser*. Most of these packages don't
know that's possible, and their docs assume an environment we are not
in. Harvesting gives us correct code that is presented in a way that doesn't
fit the shape of browser based examples.

Which leaves an uncomfortable conclusion. No automation available to us
removes the human judgement, because the human judgement *is* the most valuable
outcome we're aiming for. Meaningful, useful, trusted - each a judgement,
and none of them exists in a system that often cannot and only accidentally
makes such judgements.

## What we should do

**Target by usage, not availability.** Weighting by popularity - Anaconda
download counts, or similar - was always the plan; we started from
Pyodide's supported list because it existed. A hundred hand-written
examples covering what people actually import would be unambiguously
good, and cost less human attention than the 92 dead ends we have
already paid for. Not generating at scale saves AI time and effort by
declining to spend it on work it is unsuited to.

**Publish provenance, in three tiers.** `[NEEDS REVIEW]` currently
appears in the operator's terminal and stays there. Show it. In `api/`
and on the site:

- `verified` - human-authored, or human-reviewed for educational quality.
- `tested` - machine-generated, executes correctly in the browser.
- `unreviewed` - machine-generated, parses only.

Our 111 are `tested`. None are `verified`, and we shouldn't imply
otherwise. It costs a small schema change. It turns an invisible quality
problem into a visible one, and a visible quality problem is an
invitation to engage and improve things.

## Crowd sourcing (and its limits)

Which brings me to crowd-sourcing - from which I have both long term experience
and scars. I've contributed to OpenStreetMap since 2008 and Wikipedia
since 2004, and both make me *more* cautious, not less.

What both get right is granularity. The barrier to a first contribution
is small. Our `examples/<package>/` layout - three small
files per example - is already at the right grain, and that is a real
strength of what's been built. **The seed examples may turn out to be
worth more as scaffolding for first contributions than as actual content.**

What both also show is where the crowd doesn't go. In Wikipedia and
OpenStreetMap alike, rural coverage is systematically worse: fewer local
contributors, more bot-generated filler. Anyone who has mapped rural
Britain knows this. The crowd turns up for London or Edinburgh but does not
turn up for Upper Piddlington, somewhere in the back of beyond.

Substitute "twelve downloads a month" for "rural". The crowd will turn
up for popular packages like `pandas`. Perhaps this is even what we want?

So the proposal is narrower than "crowd-source it".

Crowd-sourcing serves the head of the distribution, where the examples
matter most because that's where the users are. Provenance labelling
serves the tail, honestly. And the relationship between human and
machine changes from an AI with a human bolted on
as quality assurance, and becomes a drafting tool for collaboratively crafted
examples.

Same tech, different social arrangement. What the tool does matters far less
than who it does it for, and who it does it to.

That inversion - from AI-first, which this pipeline embodies, to
human-first, which it could serve - is the change of posture I'm
proposing. It isn't a rejection of the work described here. The pipeline
is well-tested and its deterministic parts are genuinely useful. This is more a
reflection about where in the process the machine belongs. The crux is simple:
we set out to build something that would generate trust and meaning at scale,
yet trust and meaning are the things that cannot be generated by AI, for
trust and meaning only emerge through human interactions. This is the most
important lesson we can draw from this work.