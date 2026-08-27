# Claude Skills

A small, curated set of [Claude](https://claude.ai) skills I actually use — plus the custom
instructions behind them. Each one is self-contained: copy a folder, and it works.

## What is a skill?

A skill is a folder with a `SKILL.md` file in it. The file describes a task and how to do it
well, and Claude loads it **only when the conversation calls for it** — the `description` field
tells Claude when to reach for it.

The point is that the instructions live in a file rather than in your head. You don't re-explain
your process every time; you write it once, and it fires when it is relevant.

Skills are just Markdown. No framework, no build step, no dependencies beyond whatever the skill
itself calls for.

## The skills

| Skill | What it does | Language | Needs |
|---|---|---|---|
| [`travel-podcast`](skills/travel-podcast/) | Turns any place into a self-contained HTML audio guide, narrated by the browser, with separate scripts for adults, teenagers and children | 🇮🇹 Italian | nothing |
| [`external-interviews`](skills/external-interviews/) | When a task needs an answer only an outside person can give, opens a link-based conversation with them instead of guessing or stalling | 🇬🇧 English | [interviews MCP](https://interviews.oiarplatform.com) |
| [`post-idea`](skills/post-idea/) | Reads your RSS and newsletter digest, and proposes 3-4 LinkedIn post angles worth writing — then writes the one you pick | 🇮🇹 Italian | [feedandpost.it MCP](https://feedandpost.it) |

Two of these depend on an MCP connector, noted in the table and explained in full at the top of
each `SKILL.md`. Each skill stops and says so when its connector is missing, rather than
inventing output — worth knowing before you install one.

`travel-podcast` and `post-idea` are written in Italian, because that is the language they
produce. Translating the instructions without translating the output would be worse than
leaving them as they are.

## Custom instructions

[`instructions/`](instructions/) holds standing instructions — the rules that apply to *every*
conversation, not just one task. A skill is a procedure that waits to be needed; a custom
instruction is a preference that is always on. See
[`instructions/README.md`](instructions/README.md) for the difference and for where each kind
gets pasted.

## Installing a skill

**Claude Code** — clone the repo and copy the skill folder into your skills directory:

```bash
git clone https://github.com/luciovalente/claude_skill.git
cp -r claude_skill/skills/travel-podcast ~/.claude/skills/
```

`~/.claude/skills/` makes it available everywhere. For a single project, use
`.claude/skills/` inside the project instead. Restart Claude Code and the skill is live.

**Claude.ai** — go to Settings → Capabilities → Skills and upload the skill folder as a zip.

You never invoke a skill by name. Describe your task the way you normally would, and if the
description matches, Claude loads it. To confirm one is installed, ask Claude which skills it
can see.

## Using them as a starting point

Take one apart. The skills here encode my priorities — my topics, my audience, my tolerance for
a chatty audio guide — and yours differ. `post-idea` in particular is written to be retargeted:
it asks for your themes, your audience and your experience, and its triage is only as good as
those answers.

The conventions I follow when writing these are in [`CLAUDE.md`](CLAUDE.md), including the
checklist for what must never end up in a public skill repo.

## License

[MIT](LICENSE) — use, modify and redistribute freely.

Should a third-party skill ever be added here, it keeps its own `LICENSE` inside its folder and
those terms take precedence there. Everything currently in this repo is original work.
