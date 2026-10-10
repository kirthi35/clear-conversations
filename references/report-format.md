# A report the user can act on

Write the main report in approximately 300–500 words total. A smaller review can be shorter.
Keep necessary source detail in evidence notes below it.
Use ordinary user actions before internal implementation terms.

## Main report

Start with the strongest supported conclusion and what the user can change.
State whether the review is complete or partial in one short coverage sentence.
Print the exact date interval. Distinguish dialogue reviewed from files found.

Add a compact numeric summary near the top:

| Measure | Count |
| --- | --- |
| Session files found | Verified discovery count |
| Dialogue sessions fully reviewed | Verified complete-review count |
| Dialogue sessions partly reviewed | Verified partial-review count, or “not counted” |
| Distinct supported issues | Number of findings in this report |

Replace these placeholders with evidence-supported counts. Add source counts and excluded-file categories when they affect coverage.
For larger reviews, use a source table with Claude Code and Codex rows.
Show files found, fully reviewed sessions, partly reviewed sessions, and unread files in separate columns when those counts are available.
Unknown counts must remain “unknown” or “not counted”, rather than zero.
Do not add unlike units, such as session counts and issue counts.
A finding count measures distinct issues reported. It does not measure every occurrence or overall conversation quality.
For sampled frequencies, give the numerator, denominator, and selection method. Avoid percentages from a selected sample.
Keep detailed coverage below the main report if the summary becomes crowded.

## What kept happening

When a problem recurs, replace the generic issue list with a compact repeated-problems table:

| Repeated problem | Separate episodes | Effect on the user | Change to try |
| --- | --- | --- | --- |
| The assistant said “fixed”, but the user's browser still failed. | 2 episodes in 2 reviewed sessions | The user repeated the failed check. | State which action passed and which remains untested. |

This row is synthetic. Use actual counts and source keys in real reports.
Show episode counts separately from affected-session counts; include the reviewed-session denominator when comparable coverage supports it.
Use “at least” for incomplete coverage, and “reported” for counts supported only by earlier reviews.
Do not use an inventory count as a fully reviewed denominator.
A repeated problem needs at least two distinct task exchanges. Several follow-ups in one unresolved exchange count as one episode.
Mention important one-off incidents separately. Do not force every issue into a repeated pattern.

In evidence notes, list each counted episode with its source and session identity.
Reconcile copied exchanges and overlapping exports before counting; recount unique sessions independently of episodes.
A reported total that disagrees with its evidence rows must be flagged, not copied as a verified number.
Show whether the user needed another explanation, repeated a failed action, or corrected scope.
Do not infer wasted minutes, actual runtime damage, or instruction adherence without evidence.
If an existing rule covers the pattern, inspect it when available before proposing another rule.

Show one strongest before/after example. Quote the historical response exactly, apart from necessary redaction.
Label the replacement as proposed. Preserve the facts, tested paths, and unknown cause.

Explain what worked when the source supports a successful pattern.
Propose one or two small instruction changes linked to the findings.
State that an instruction change affects future guidance. It does not repair the current runtime fault.
Show a known target and proposed diff before asking to save an unauthorized edit.
Preserve already authorized instruction-update behavior.

## Evidence notes

Use keys such as E1 and E2 to connect findings to source locations.
Include the relevant goal, exchange, classification, observed result, and limits.
For unavailable runtime evidence, write “the transcript reports” rather than treating an assistant's assertion as verified.

Report coverage separately:

- Exact date interval and the available sources.
- Candidate files discovered and dialogue-bearing sessions fully read.
- Automated or empty files, unresolved dates, and excluded subagents.
- Partly read sessions, sampled exchanges, and omitted source ranges.
- Discovery or reading limits and their effect on the conclusion.

Do not equate an inventory count with reviewed conversations.
Anchor interval findings to confirmed in-window dialogue. Treat earlier messages as context and unknown-date observations as provisional.
Do not treat automated files as failures or invent understanding scores.
Do not generalize sampled behavior to every interaction.

## Final check

Check all nonquoted prose sentences against the 25-word descriptive and 20-word procedural limits.
Remove repeated observations, excerpts, and technical background that does not change the next decision.
Keep required evidence, conditions, uncertainty, and source references.
Label public examples as synthetic and remove private names, source paths, session identities, and measurements.
