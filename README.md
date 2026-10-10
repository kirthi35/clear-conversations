# Clear Conversations

**Find the explanation that lost the thread. Keep the one that worked.**

Clear Conversations is a skill for Claude Code and Codex.
It reviews retained sessions, identifies supported communication problems, and suggests changes suited to your conversations.
It also records successful explanations and can compare later sessions after an accepted instruction change.

The assistant reads complete relevant exchanges before making a finding.
It separates communication problems from technical errors, scope disagreements, and unresolved cases.
It does not score you or treat “I don't understand” as proof that an explanation failed.

## A concrete change

This example is synthetic. The assistant is explaining why a task status changes only after the user reloads the page.

**Before**

> The materialized projection requires client reconciliation after the asynchronous lifecycle transition.

**After**

> The worker saves the new task status. The browser receives no live update. Reloading makes the browser request the saved status.

The second response identifies the actors and the missing step.
A real review must establish these technical facts before using this explanation.

## Install

You need Git, local session access, and Python 3.10 or later.
The collector uses the Python standard library. You do not need to install Python packages.

Check your Python version:

```sh
python3 --version
```

If the version is older than 3.10, use an available interpreter such as `python3.11` for collector and test commands.

### Codex

Install the personal skill:

```sh
mkdir -p ~/.agents/skills
git clone https://github.com/kirthi35/clear-conversations.git ~/.agents/skills/clear-conversations
```

Invoke the skill in Codex:

```text
$clear-conversations Review my latest 10 retained sessions. Give me the strongest evidence and small instruction suggestions.
```

Codex uses `~/.agents/skills` for personal skills.
If the skill does not appear, restart Codex. See [Codex skill documentation](https://learn.chatgpt.com/docs/build-skills).

### Claude Code

Install the personal skill:

```sh
mkdir -p ~/.claude/skills
git clone https://github.com/kirthi35/clear-conversations.git ~/.claude/skills/clear-conversations
```

Invoke the skill in Claude Code:

```text
/clear-conversations Review my latest 10 retained sessions. Give me the strongest evidence and small instruction suggestions.
```

Claude Code uses `~/.claude/skills` for personal local skills.
See [Claude Code skill documentation](https://code.claude.com/docs/en/skills) for discovery and other installation scopes.

### Use one installation with both hosts

Both hosts support symlinked skill directories.
If you installed the Codex copy, you can share it with Claude Code:

```sh
mkdir -p ~/.claude/skills
ln -s ~/.agents/skills/clear-conversations ~/.claude/skills/clear-conversations
```

Use this command only when the destination does not already exist.
You can also install separate copies.

## Choose what to review

Installation controls where the skill is available.
The review source controls which retained sessions the assistant reads.
Either host can review Claude Code sessions, Codex sessions, or both, when local permissions allow access.

By default, the skill selects the latest 10 retained root sessions across both sources.
A root session is the main conversation. Separate subagent sessions are excluded from the default sample.
Retained records can be incomplete. The report states its sources, selected period, sample size, and reading limits.
The collector sorts discovered sessions by file modification time.
If a scan limit applies, the selection contains the latest discovered sessions, not necessarily the latest sessions overall.

Try one of these requests after invoking the skill:

- “Review only my Codex sessions since 2026-10-01.”
- “Review this session. Separate explanation problems from technical mistakes.”
- “Show one successful explanation and one concrete before/after rewrite.”
- “Apply the accepted wording to this repository's AGENTS.md. Preserve unrelated instructions.”
- “Compare later sessions with the accepted instruction. State where the evidence is insufficient.”

The review suggests instruction changes. It does not automatically edit `CLAUDE.md`, `AGENTS.md`, or memory.
An explicit update request authorizes the selected change, subject to the host's file permissions.

## What you receive

The assistant reports up to three prioritized findings, a supported successful pattern, and evidence limits.
Each finding cites source lines, explains the observed result, and gives a tailored recommendation.
Proposed rewrites preserve technical facts and unresolved questions.

For example, a synthetic review could say:

> The assistant introduced an undefined term before explaining why the page needed a reload.
>
> **Evidence:** `examples/synthetic-session.jsonl:1–5`. The user asked about the reload, then requested a plain explanation.
>
> **Observed:** The user correctly restated the explanation after the assistant identified the worker and browser.
>
> **Proposed instruction:** Explain the user's action and data flow before naming internal mechanisms.
>
> **Limit:** This record does not establish whether the described runtime behavior was technically correct.

Read the [complete synthetic report](examples/report.md) and its [synthetic source](examples/synthetic-session.jsonl).
No public example contains a real private conversation.

## How the review works

1. The collector lists retained session files within explicit scan limits.
2. The assistant selects the requested sample and reads paginated conversation records.
3. The assistant reads the whole relevant exchange, including corrections and recovery.
4. The assistant checks alternative causes and cites the evidence for each conclusion.
5. The assistant proposes small changes and preserves patterns that helped the user.

The collector does not produce keyword verdicts or communication scores.
It provides source locations and extracted records. The host assistant performs the analysis.
See [collector commands and limits](references/collector.md) for manual use.

The report uses ASD-STE100 writing principles: short sentences, explicit actors, consistent terms, and concrete context before diagrams.
Formal compliance requires checking the applicable rules and dictionary.
This project does not claim certification or measured time savings.

## Privacy and limits

The collector reads local files, writes JSON to standard output, and makes no network requests.
It does not create a transcript archive or run background collection.
The host assistant may send supplied material to its provider under the host's settings and policies.
Local extraction does not mean that the full review stays on your device.

Redaction is best effort. It cannot guarantee removal of credentials, personal data, or business secrets.
Review material before sharing it. Keep private reports and transcripts out of public issues and pull requests.

The review cannot recover deleted sessions or omitted context.
Session formats can change, and unsupported records can reduce coverage.
The assistant must disclose scan limits, malformed records, compaction, and unfinished pagination.
Later-session comparisons show observed behavior; they do not establish that an instruction caused a change.

## Development

Run collector tests from the repository root:

```sh
python3 -m unittest discover -s tests -v
```

Use Python 3.10 or later. The tests use synthetic fixtures, not your retained sessions.
Use the [manual behavior scenarios](evals/manual-scenarios.md) to check the assistant's judgments and authorization boundaries.
Collector tests alone do not establish the quality of an assistant's review.
Report quality depends on the host model. Check the evidence and proposed wording before applying instruction changes.

## Sources and license

- [Codex skills](https://learn.chatgpt.com/docs/build-skills): personal installation and skill discovery.
- [Claude Code skills](https://code.claude.com/docs/en/skills): personal installation, invocation, and supporting files.
- [Agent Skills specification](https://agentskills.io/specification): portable `SKILL.md` structure.
- [Official ASD-STE100 standard](https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf): writing rules and controlled vocabulary.

The project contains original instructions and synthetic examples. It does not reproduce the ASD-STE100 dictionary.
Project code and original content use the [MIT license](LICENSE).
