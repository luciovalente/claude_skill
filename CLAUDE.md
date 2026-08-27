# Working on this repository

This repo is a **public** collection of Claude skills and custom instructions. Everything
committed here is world-readable, permanently, and search-indexable. That single fact drives
most of the rules below.

## What lives here

```
skills/<skill-name>/SKILL.md      one folder per skill, SKILL.md is mandatory
skills/<skill-name>/assets/       templates and static files the skill fills in
skills/<skill-name>/scripts/      executable helpers the skill calls
instructions/<scope>.md           standing instructions (see instructions/README.md)
```

No other top-level directories without a reason. A skill that needs a companion document keeps
it inside its own folder, not in a shared `docs/`.

## Naming

- Folder name **is** the skill name: lowercase, hyphen-separated, no spaces or underscores.
  `travel-podcast`, not `Travel Podcast` or `travel_podcast`.
- The `name:` field in the frontmatter must match the folder name exactly. Claude resolves
  skills by folder; a mismatch produces a skill that silently never triggers.
- Name the skill after **what it does**, not after who wrote it or what it is built on.
  `post-idea`, not `lucios-post-helper`. Personal names in a skill name are a smell: they mean
  the skill is either not reusable, or reusable and mislabelled.

## Format of a SKILL.md

YAML frontmatter, then the body. Only two frontmatter fields are required:

```yaml
---
name: skill-name
description: What it does, followed by the phrasings that should trigger it.
---
```

`description` is the only thing Claude sees when deciding whether to load a skill, so it does
double duty: it states the purpose **and** enumerates the trigger phrases. Write it in the
language the user will actually speak. A vague description is the most common reason a
well-written skill never fires.

Optional frontmatter: `license` when the skill carries terms of its own.

The body must cover four things, in whatever order reads best:

1. **Purpose** — what the skill produces, in one or two sentences.
2. **When it triggers / how it is used** — the situation that calls for it, and any situation
   that looks similar but should *not* call for it.
3. **Prerequisites** — MCP connectors, API keys, files, tools. Say explicitly what Claude
   should do when a prerequisite is missing: stop and report it, rather than improvise. A skill
   that fabricates output when its data source is unreachable is worse than one that fails.
4. **A concrete usage example** — a real invocation with real-looking output. This is the part
   readers skip to first, and the part that shows whether the skill is worth their time.

Write in the imperative, addressed to Claude ("Read the full text before proposing it"), not in
the third person about Claude. Skip the marketing register — no "powerful", no "seamlessly".
State what happens and what to do when it doesn't.

## Adding a new skill

1. Create `skills/<name>/` and write `SKILL.md` against the format above.
2. **Sanitise it** — see the next section. Do this before the first commit, not after: git
   history is public too, and a redaction commit only advertises what to look for.
3. Add a row to the skill index in [`README.md`](README.md): name, link, one line of
   description. The index is the 30-second view of the repo; a skill missing from it does not
   exist.
4. Verify the skill still works after sanitising. Replacing a real path with a placeholder can
   break a code path that was never exercised with a placeholder in it.

## What must never be committed

Redact these before the first commit, always:

- **Absolute local paths** — `/Users/<name>/...`, `/home/<name>/...`, `C:\Users\...`.
  Use `<YOUR_PROJECT_PATH>` or a relative path.
- **Hostnames and SSH aliases** — server names, `~/.ssh/config` entries. Use `<YOUR_SSH_HOST>`.
- **IP addresses**, including private and container-internal ones. Use `<DB_HOST>`.
- **Credentials of any kind** — passwords, API keys, tokens, private keys, connection strings.
  Also the *format* of a key when it hints at how keys are issued.
- **Internal infrastructure** — container names, compose file layouts, deploy topology,
  internal domains. A deploy runbook is a map of your attack surface.
- **Real client, employer, or project names**, in prose and in examples alike. Invent a
  placeholder company; if an example needs a company, `ClientCo` does the job.
- **Personal details about identifiable people** — colleagues, family, anyone who did not
  choose to be in a public repo. This includes details that look harmless in isolation.

Two things are deliberately **not** on that list:

- **Public service endpoints** the skill genuinely depends on. `feedandpost.it` and
  `oiarplatform.com` appear in these skills on purpose: they are public services, and replacing
  them with placeholders would leave a skill that cannot run.
- **Public professional identity.** An author's name and public role are fine. What is not fine
  is the private layer underneath it.

When unsure whether something belongs to the public or the private layer, leave it out and note
the gap. A skill with a `<PLACEHOLDER>` is usable; a leak is not reversible.

## Third-party skills

If a skill originates elsewhere — an Anthropic example, a plugin ecosystem, someone's gist —
say so at the top of its `SKILL.md`, keep its original `LICENSE` inside its own folder, and do
not rename it to obscure where it came from. The root MIT license covers original work in this
repo only; a per-folder license takes precedence within that folder.

Do not commit a third-party skill whose licence you have not read.
