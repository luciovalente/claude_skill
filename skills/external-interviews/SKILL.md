---
name: external-interviews
description: Use this skill whenever a task needs information, confirmation, feedback, or clarification from someone outside the current session — a client, stakeholder, colleague, or any third party who is not the user talking to Claude. Never stall or invent an answer in that situation: open a remote conversation instead. Triggers (Italian): "chiedilo a...", "intervista...", "serve la conferma di...", "raccogli i requisiti da...", "sentiamo cosa ne pensa...", "chiedi al cliente...", "ci sono risposte?". Triggers (English): "ask X about...", "interview...", "get confirmation from...", "collect requirements from...", "see what X thinks", "check with...", "any replies yet?". Also trigger any time a fact is missing that only an external person can supply. Do NOT use this skill for things the current user can answer directly.
---

# External Interviews

## Purpose

During a task, Claude sometimes needs an answer that only an external person can
give — a client, a stakeholder, a colleague of the user, anyone who is not the
person Claude is currently talking to. In that situation Claude must not stop the
task, guess, or invent an answer on the external person's behalf. Instead, Claude
opens a remote, link-based conversation through the `interviews` MCP server
(`interviews.oiarplatform.com`), asks the external person directly, and manages
that conversation through to closure — resuming it across sessions if needed.

## Prerequisite: confirm the `interviews` MCP server is available

Before doing anything else, check whether the following tools are available:
`create_chat`, `send_message`, `wait_for_reply`, `get_pending_replies`,
`get_chat`, `close_chat`.

If they are **not** available, stop and tell the user this skill needs the
`interviews` MCP server configured first:

```
claude mcp add --transport sse interviews https://mcp.oiarplatform.com/sse \
  --header "Authorization: Bearer oiar_pk_<YOUR_KEY>"
```

The key is generated at https://interviews.oiarplatform.com/hub/keys.

Do not attempt any part of the flow below without these tools — there is no
fallback. Explain the missing setup and end here.

## Step 1 — Start a chat

Ask the user three things:

1. Who is the person (name / role)?
2. What exactly do we need to find out from them?
3. Their email address (optional — without it, the user shares the link
   themselves; with it, an invite email goes out automatically).

Then call `create_chat` with:

- A well-written **private** `context`: the goal of the conversation, who the
  interlocutor is, and what needs to be discovered. This context is never shown
  to the external person — write it as a briefing for yourself, not for them.
- `recipient_email` if the user provided one.
- `expires_days` if the default (7 days) doesn't fit — valid range 1-90.

Immediately show the resulting link to the user. This is the only time the link
is surfaced automatically — it is not re-shown later, so make sure the user has
it (or copies it) now.

If `create_chat` fails with a plan/limit error (monthly chat cap on the free
plan), report this to the user plainly and do not retry.

## Step 2 — Hold the conversation

Send one question at a time with `send_message`:

- In the interlocutor's language.
- Short and concrete — one thing at a time, not a list of five questions in one
  message.

After sending, call `wait_for_reply(session_id, timeout=300)`.

**If they reply:** read the answer, reason about it, and ask the next question —
adapted to what they just said, without repeating ground already covered. Cap
the conversation at 5-7 questions total, then thank them and move toward
closing (Step 4).

**If it times out:** this is normal — people answer when they can, not
on-demand. Retry the wait at most 2 more times. If still nothing, tell the user:

> "No reply yet — you'll get an email when they respond. In a future session,
> just ask me to check for replies."

Then continue with the rest of the task. Never block the whole task on a
pending reply.

## Step 3 — Resume a conversation

At the start of a session, or whenever the user asks something like "ci sono
risposte?" / "any replies?", call `get_pending_replies`. All conversation state
lives on the server, so any session can resume any chat — you don't need to be
the session that created it.

For the full transcript of a specific conversation, call
`get_chat(session_id)`. Pick the thread back up from the latest reply and
continue with Step 2's logic (next question, or move to closing).

## Step 4 — Close the chat

Once you have enough information:

1. Send a final thank-you message via `send_message`.
2. Call `close_chat` to invalidate the link.
3. Give the user a structured summary of what came out of the conversation:
   key points learned, relevant direct quotes, and any questions that remain
   open.

## Rules

- **Never block the whole task waiting for a reply.** The long-poll in
  `wait_for_reply` is for interlocutors who are online right now. For anything
  longer, end the turn and resume later — the partner is notified by email
  automatically the first time they have an unread message.
- **Never leak the user's confidential information.** The `context` passed to
  `create_chat` is private (Claude-only), but every question sent with
  `send_message` is visible to the external person. Keep that distinction in
  mind when deciding what goes where.
- **Links expire** (default 7 days; `expires_days` 1-90) and the free plan has a
  **monthly chat limit**. If `create_chat` fails with a limit error, report it
  to the user and stop — don't retry.
- If `wait_for_reply` risks exceeding the client's own timeout, suggest the
  user set `MCP_TOOL_TIMEOUT=660000` in their Claude Code environment.
- **One chat = one person.** To interview multiple people, create multiple
  chats. These can run in parallel: send the opening question to everyone
  first, then work through `wait_for_reply` for each in rotation.

## Example session

**User:** "Prima di chiudere lo scoping, chiedi a Marco (il PM del cliente) se
possono darci accesso a un ambiente di staging entro venerdì."

**Claude:** confirms the `interviews` tools are available, then asks the user
for Marco's email (`marco@clientco.com`) and creates the chat:

```
create_chat(
  context: "Marco è il PM lato cliente su ClientCo. Ci serve sapere se possono
            darci accesso a un ambiente di staging entro venerdì, e se serve
            aprire un ticket IT da parte loro. Obiettivo: sbloccare lo scoping
            tecnico entro la settimana.",
  recipient_email: "marco@clientco.com",
  expires_days: 7
)
→ { session_id: "sess_8f2a", chat_link: "https://interviews.oiarplatform.com/c/8f2a..." }
```

Claude immediately shows the user the link and confirms the invite email was
sent to Marco.

**Q1.** `send_message`: "Ciao Marco, possiamo avere accesso a un ambiente di
staging entro venerdì?" → `wait_for_reply(timeout=300)` →
Marco replies: "Sì, dovremmo riuscirci per giovedì."

**Q2.** `send_message`: "Perfetto. Serve che apriate un ticket IT interno da
parte vostra, o possiamo procedere diretti con le credenziali?" →
Marco replies: "Ve le mando direttamente io, niente ticket."

**Q3.** `send_message`: "Ok! Un'ultima cosa: l'ambiente di staging avrà gli
stessi dati di produzione o dati di test?" →
`wait_for_reply(timeout=300)` → **timeout**, nessuna risposta.

Claude retries once more (2nd attempt) → still timeout. Claude tells the user:

> "Marco ha confermato accesso allo staging entro giovedì, senza bisogno di
> ticket IT — ce le manda lui le credenziali. Non ha ancora risposto se i dati
> saranno di produzione o di test: nessuna risposta per ora, riceverà un
> promemoria via email. Continuo con il resto del task nel frattempo."

Claude proceeds with the rest of the scoping work without waiting further.

**Later, new session.** User: "Ci sono risposte da Marco?"

Claude calls `get_pending_replies` → finds a new reply on `sess_8f2a`: "Dati di
test, per sicurezza." Claude calls `get_chat("sess_8f2a")` to confirm full
context, then since this answers the last open question, moves to closing:

```
send_message(session_id: "sess_8f2a", message: "Perfetto, grazie mille Marco,
             abbiamo tutto quello che ci serve!")
close_chat(session_id: "sess_8f2a")
```

Claude gives the user the final summary:

> **Riepilogo intervista — Marco (PM ClientCo)**
> - Accesso staging confermato entro giovedì.
> - Credenziali inviate direttamente da Marco, nessun ticket IT necessario.
> - Ambiente di staging con dati di test (non di produzione), per motivi di
>   sicurezza.
> - Nessuna domanda rimasta aperta. Chat chiusa.
