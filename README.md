# Clear Conversations

**Stop asking your coding assistant to explain its explanation.**

An AI answer can contain a wall of text and still miss the question you asked.
Sometimes the assistant uses unfamiliar terms. Sometimes it keeps explaining a cause that does not match what you reported.

Clear Conversations reviews those exchanges and proposes better explanations and small instruction changes.
It is a **skill**: reusable instructions that your coding assistant follows when you invoke it.
The same skill works in Claude Code and Codex.

## Install

You need Git, access to your locally saved conversations, and Python 3.10 or later.
The included session reader uses Python's standard library. No Python packages are required.

Check your Python version:

```sh
python3 --version
```

If your default Python is older, use an available interpreter such as `python3.11` for the reader and tests.

### Claude Code

```sh
mkdir -p ~/.claude/skills
git clone https://github.com/kirthi35/clear-conversations.git ~/.claude/skills/clear-conversations
```

### Codex

```sh
mkdir -p ~/.agents/skills
git clone https://github.com/kirthi35/clear-conversations.git ~/.agents/skills/clear-conversations
```

If the skill does not appear, restart your coding assistant.

## Run one command

In Claude Code, enter:

```text
/clear-conversations
```

In Codex, the same invocation uses `$clear-conversations`.
No extra prompt is required.

The assistant then:

1. Finds your latest 10 available saved conversations across Claude Code and Codex.
2. Reads the relevant exchanges, including your corrections and the assistant's recovery.
3. Returns supported findings, clearer rewrites, and a small proposed instruction.
4. Shows the instruction and target file before asking whether to save it.

Either assistant can review both sources when local permissions allow access.
If one source is missing, the review uses the other.
If neither source is available, the assistant explains the next useful collection step.

The default review uses main conversations, rather than separate subagent conversations.
The assistant also honors a narrower scope when you explicitly provide one.

## What the result looks like

These examples are illustrative. They are invented scenarios, not excerpts from private conversations or verified runtime findings.

### Problem: the explanation does not match the reported failure

**Illustrative exchange**

> **Assistant:** A chat session expires after 60 minutes. That explains why the chat stopped working.
>
> **User:** But this is a new chat. It fails after three minutes.

**Review**

**Classification:** Unresolved technical mismatch.
The 60-minute limit does not explain the reported three-minute failure by itself.
The cause remains unknown. A clearer explanation must expose that mismatch before proposing another cause.
The mismatch alone does not prove a communication failure.

**Proposed rewrite**

> The 60-minute expiry does not explain a new chat failing after three minutes by itself.
> We have not identified the cause of this earlier failure.
> We need evidence from the failed request before choosing another explanation.

**Proposed instruction**

> When a reported observation conflicts with your explanation, state the mismatch first.
> Keep the cause unresolved until evidence identifies it.

For a project that uses `AGENTS.md`, the assistant could propose this diff after inspecting that file:

```diff
+ When a reported observation conflicts with your explanation, state the mismatch first.
+ Keep the cause unresolved until evidence identifies it.
```

The review shows the target file and proposed change for your decision.
It does not silently save the rule.

### Problem: internal terms hide the user's flow

**Illustrative scenario:** A task status changes on the page only after the user reloads it.

**Before**

> The materialized projection requires client reconciliation after the asynchronous lifecycle transition.

**Review**

**Classification:** Communication gap in the wording; technical flow unverified.
The response names internal mechanisms before identifying what the worker and browser do.
The rewrite below is suitable only if the implementation evidence supports that flow.

**Proposed rewrite**

> The worker saves the new task status. The browser receives no live update.
> Reloading makes the browser request the saved status.

**Proposed instruction**

> Explain the user's action and data flow before naming internal mechanisms.

Read the [complete illustrative report](examples/report.md) and its [synthetic source](examples/synthetic-session.jsonl).
A real review cites source files and lines, includes useful excerpts, and preserves uncertainty.
It also identifies successful explanations when the evidence supports them.

## What the review checks

The assistant separates communication problems from technical errors, scope disagreements, and unresolved cases.
Your confusion alone does not prove that an explanation failed.
The assistant reads the whole relevant exchange and checks whether a correction or clearer explanation resolved the misunderstanding.

The report contains up to three prioritized findings. It does not invent findings to fill that limit.
Suggested rules address the supported problem, rather than imposing a permanent preference from one incident.

Reports follow ASD-STE100 writing principles: short sentences, explicit actors, consistent terms, and concrete context before diagrams.
This project does not claim formal compliance, certification, or measured time savings.

## Privacy and limits

The session reader accesses local files, writes JSON to standard output, and makes no network requests.
Your coding assistant may send that material to its provider under the assistant's settings and policies.
Local extraction does not mean that the complete review stays on your device.

Redaction is best effort. It cannot guarantee removal of credentials, personal data, or business secrets.
Keep private transcripts and reports out of public issues and pull requests.

The review covers available retained records, not your complete conversation history.
The reader sorts discovered files by modification time, within bounded scans.
If a scan limit applies, the selected files are the latest discovered conversations, not necessarily the latest overall.
The assistant discloses missing context, unread ranges, and other evidence limits.

A review does not automatically edit `CLAUDE.md`, `AGENTS.md`, or memory.
An explicit save request authorizes only the accepted change to the selected file.
Later comparisons can check the behavior again, but cannot establish causation from an instruction change alone.

See [session reader commands and limits](references/collector.md) for collection details.

## Development

Run tests from the repository root with Python 3.10 or later:

```sh
python3 -m unittest discover -s tests -v
```

The tests use synthetic fixtures, not your retained sessions.
The [manual behavior scenarios](evals/manual-scenarios.md) check assistant judgments and authorization boundaries.
Report quality depends on the host model. Check the evidence and proposed wording before saving instruction changes.

## Sources and license

- [Claude Code skills](https://code.claude.com/docs/en/skills): personal installation and invocation.
- [Codex skills](https://learn.chatgpt.com/docs/build-skills): personal installation and discovery.
- [Agent Skills specification](https://agentskills.io/specification): portable skill structure.
- [Official ASD-STE100 standard](https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf): writing rules and controlled vocabulary.

The project contains original instructions and synthetic examples. It does not reproduce the ASD-STE100 dictionary.
Project code and original content use the [MIT license](LICENSE).
