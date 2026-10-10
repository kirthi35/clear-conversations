# Illustrative review

This report and both sources are synthetic. All dates, actions, and messages were invented for the example.

## Summary

The same problem occurred in two separate chats: the assistant said “fixed”, but the user's browser still failed.
One chat concerned Save. The other concerned a CSV export.
Both assistants later acknowledged that their earlier checks had not verified the browser action.

**Illustrative period:** 2026-07-10 through 2026-10-10.

| Review summary | Count |
| --- | ---: |
| Session files supplied and fully reviewed | 2 |
| Dialogue messages examined | 17 |
| Distinct supported issues | 2 |
| Issues repeated in separate chats | 1 |
| Successful patterns identified | 1 |

Both supplied sessions are from Claude Code. No Codex records were supplied.
No exchanges were sampled, and no sessions remain partly read. No automated or empty files were supplied.
These fixtures illustrate the report format, rather than a real three-month review.

## What kept happening

| Repeated problem | Separate episodes | Effect on the user | Change to try |
| --- | --- | --- | --- |
| “Fixed” did not mean the browser action had passed. | 2 episodes in both reviewed sessions. E1 | The user repeated the failed action. | Say what passed and what remains untested. |

**One additional incident:** “Persistence layer” did not tell the user what to do. Explain unfamiliar terms and give a concrete action. E2

**Before — exact assistant response:**

> The terminal check passed. The issue is fixed now.

**After — proposed rewrite:**

> The terminal check passed, but we have not verified the Save button in your browser.
> Your browser still reports an error. The cause remains unknown.
> Next, click Save once and tell me the exact message.

The rewrite preserves the reported test result and identifies the next check.

## What worked

The assistant later asked the user to open the page, then click Save and report the message.
The user followed those steps and correctly restated the verification gap. E3 supports this successful pattern.
The record does not show that the runtime problem was repaired.

## Proposed rules

> State what was tested and what remains unverified before claiming that a problem is fixed.
>
> When the user requests a manual check, give one concrete action at a time.

These rules would guide future responses. They would not repair either browser failure.
No instruction file changed. The target remains unspecified.

## Evidence notes

- **E1 — communication; technical causes unresolved:** Two distinct episodes support this pattern. Save: [synthetic-session.jsonl](synthetic-session.jsonl), lines 1–3 and 6, session `synthetic-example`. Export: [synthetic-session-2.jsonl](synthetic-session-2.jsonl), lines 1–4, session `synthetic-export-example`. Each transcript reports a successful nonbrowser check and a continuing browser failure. Tool evidence is unavailable. Later follow-ups belong to these same episodes; they are not extra occurrences.
- **E2 — communication:** First source, lines 4–5. The assistant introduced “persistence layer” without defining it or answering the requested next action. This occurred once in the supplied evidence.
- **E3 — successful recovery:** First source, lines 6–11. The user performed the requested actions and accurately restated the difference between the tested paths.

These invented sessions demonstrate counting within an example. They do not establish a real user's behavior, permanent preferences, or technical causes.
