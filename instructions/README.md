# Custom Instructions

Standing instructions that shape how Claude behaves across a whole account, project, or
repository — as opposed to a **skill**, which activates only when a specific task comes up.

Rough rule of thumb:

| | Custom instruction | Skill |
|---|---|---|
| **When it applies** | Always, in every conversation of its scope | Only when its description matches the request |
| **What it holds** | Preferences, tone, standing constraints | A procedure for one kind of task |
| **Where it lives** | Account settings, a project, or `CLAUDE.md` | `skills/<name>/SKILL.md` |

## Layout

One Markdown file per instruction, named after **what it does** — the same rule as skills:

```
instructions/
├── README.md
├── build-warning.md
└── anti-sycophancy.md
```

Not named after where it is pasted. Instructions get copied one at a time, and a file called
`personal.md` holding four unrelated rules cannot be. Scope is declared in the header instead,
so one file can be reused without dragging the rest along.

Each file has a header stating **where it is meant to be pasted**, **what language it is written
in**, and **what it assumes**, then a short note on what it actually does and what it costs.
Then the instruction text itself, below a rule:

```markdown
# <Name>

**Scope:** account-level (Claude Settings → Personal preferences)
**Language:** Italian
**Assumes:** something about the reader that decides whether this fits them

<a paragraph or two: what it changes, and what the trade-off is>

---

<the instruction text, verbatim>
```

Keep the instruction text **verbatim**. These files are meant to be copied and pasted back into
Claude, so a paraphrase is worse than useless — commentary belongs in the header, not mixed
into the body.

## How to use one

**Account-level** — open Claude Settings, go to *Personal preferences*, and paste the file body.
It then applies to every conversation on the account.

**Project-level** — open the project in Claude, go to its instructions field, and paste the
file body. It applies only inside that project.

**Repository-level** — save the file body as `CLAUDE.md` at the root of a repository. Claude
Code reads it automatically at the start of every session in that repo.

## Before committing one

Custom instructions attract personal detail more than skills do — they are written for an
audience of one, so nothing in them ever felt like it needed sanitising. Re-read the checklist
in the root [`CLAUDE.md`](../CLAUDE.md) before adding a file here. In particular: employer and
client names, the shape of your working day, and details about family members tend to end up in
personal preferences without anyone noticing.
