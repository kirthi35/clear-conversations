# Clear Conversations

**Stop asking your coding assistant to explain its explanation.**

An AI answer can contain a wall of text and still miss your question.
The assistant might claim a fix before checking your browser.
It might give an unfamiliar term instead of a useful next step.

Clear Conversations reviews your saved chats and proposes clearer explanations and small instruction changes.
It is a **skill**: reusable instructions that your coding assistant follows when you invoke it.
The same skill works in Claude Code and Codex.

## Install

Use the Git commands below to install the skill. **Python is not required to install or use it.**
Your coding assistant chooses available tools to read your saved conversations.

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

## From a saved chat to a useful rule

The sequence below is illustrative. The messages and outcomes are synthetic, rather than private conversation excerpts or verified runtime findings.

### 1. A previous chat left a gap

> **You:** The Save button shows an error. Please check why.
>
> **Assistant:** The terminal check passed. The issue is fixed now.
>
> **You:** I clicked Save in the browser again. It still shows an error.

The transcript reports one successful check and a continuing browser error.
It does not show a successful check of the Save button.
In a second invented chat, the assistant makes the same claim about a CSV export after checking only the server.
The user reports that the browser still exports an empty file.

### 2. Run one command

In Claude Code, enter:

```text
/clear-conversations
```

In Codex, use `$clear-conversations`.
No extra prompt is required.

The assistant reviews saved main conversations active during the last **three calendar months**, across both sources.
The interval runs from today's date back three months. The report prints the exact dates.
Older conversations resumed during that interval are included.

The assistant reads relevant exchanges, checks corrections and recovery, and returns a short report.
If one source is unavailable, the review uses the other and states the limitation.

### 3. Read the clear report

An illustrative report could say:

> **Change to try:** Separate what passed from what the user still reports as failing.
>
> The transcript reports a successful terminal check and a continuing browser error.
> It does not establish that the Save button was fixed.
>
> | Review summary | Count |
> | --- | ---: |
> | Synthetic sessions reviewed | 2 |
> | Messages examined | 17 |
> | Supported issues in the complete example | 2 |
> | Issues repeated in separate chats | 1 |
>
> **What kept happening**
>
> | Repeated problem | How often | Better response |
> | --- | --- | --- |
> | The assistant said “fixed”, but the browser action still failed. | 2 separate episodes in 2 reviewed chats | Say what passed, what remains untested, and what happens next. |
>
> **Proposed rewrite:** “The terminal check passed, but we have not verified Save in your browser. The cause remains unknown.”
>
> **What worked:** Later, the assistant gave one browser action at a time. The user followed the steps and restated the verification gap.
>
> **Proposed rule:** “State what was tested and what remains unverified before claiming that a problem is fixed.”

A real report supplies source references and evidence notes below the main explanation.
It distinguishes files found from conversations actually read.
The [complete synthetic report](examples/report.md) cites both invented sources: the [Save chat](examples/synthetic-session.jsonl) and the [export chat](examples/synthetic-session-2.jsonl).

### 4. Save a rule only if you accept it

The assistant shows the proposed wording and the selected instruction file before asking to save a new rule.
For example, an approved rule could become an instruction in your project's `AGENTS.md` or `CLAUDE.md`.

The saved rule guides future assistant behavior. It does not repair the current browser failure.
The assistant preserves unrelated instructions and shows the resulting change.
If you already requested a specific edit, the assistant uses that authorization.

## What the review covers

The default period is three calendar months, rather than an arbitrary number of recent files.
The assistant checks both sources in batches and reviews available candidates with relevant or unresolved activity dates.
Confirmed files outside the interval can be excluded.
A newer Claude Code chat does not displace an eligible Codex chat, or the reverse.

A file list is not a completed review.
The report separates files found, dialogue sessions read, automated or empty files, and sampled exchanges.
If a reading or discovery limit prevents complete coverage, the report says that the review is partial.

The assistant separates communication problems, technical errors, scope disagreements, and unresolved cases.
Your confusion alone does not prove that an explanation failed.
The report contains up to three supported issues, a useful rewrite, successful patterns, and small proposed rules.
The report starts with a numeric summary. Tables show source coverage and pair problems with suggested changes when useful.
Counts describe the reviewed evidence. Unknown counts remain unknown, and sampled results include their denominators.
“What kept happening” groups repeated problems and shows separate occurrences, affected sessions, and their effect on the user.
Repeated questions within one unresolved task do not automatically count as separate failures.
Copied exchanges and earlier reviews do not create new occurrences. Single incidents remain separate from recurring problems.
Its main explanation aims for approximately 300–500 words total and can be shorter.
Detailed evidence remains available below it.

Reports use ASD-STE100 writing principles: short sentences, explicit actors, consistent terms, and concrete context before diagrams.
This project does not claim formal compliance, certification, measured time savings, or a numeric clarity score.

## How sessions are read

Claude Code or Codex chooses suitable tools in its environment: native file tools, available commands, or the optional bundled reader.
A missing Python installation or a broken shell does not block the review when other permitted tools can read the sessions.
The assistant reports any material it could not read.

The optional [session reader](references/collector.md) handles date selection, bounded reads, duplicate records, and basic credential redaction.
Only this helper requires Python 3.10 or later. It uses the standard library and needs no additional Python packages.

## Your sessions and reports

The review runs through your coding assistant and its configured model. This skill adds no separate upload service.
Your review request authorizes reading the selected sessions with the assistant's permitted tools.
Useful names and technical details stay in the explanation. Passwords and tokens need not be repeated to explain a communication problem.
The assistant does not require a separate redaction step or another approval before reading authorized sessions.

Reports stay in the conversation unless you request a file or another destination.
Public examples use synthetic material or specifically approved excerpts.

The review covers available retained records, not your complete conversation history.
The assistant discloses missing sources, uncertain dates, unread ranges, and other evidence limits.
Without tool evidence, the report describes what the transcript says and preserves uncertainty about the runtime.

A review does not automatically edit `CLAUDE.md`, `AGENTS.md`, or memory.
An explicit save request authorizes only the accepted change to the selected file.
Later comparisons can check behavior again, but cannot establish causation from an instruction change alone.

See [optional reader commands and limits](references/collector.md) when using the bundled helper.

## Development

To develop or test the optional Python reader, use Python 3.10 or later:

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
