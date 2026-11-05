# The research report

The report is a published page: the user reads it there, shares it, and comes back to it while designing. It teaches a reader who arrives cold, so it leads with what was learned and why it matters to us, and the evidence follows. The section list below is the backbone. Rename, split or add sections as the topic needs, as long as each of these jobs is done somewhere.

## Sections

1. **Summary.** The answer to the question in one paragraph, the three to five learnings that matter most for us, and the reading tally: papers and articles read in full, end to end, out of those found or glimpsed. A reader who stops here knows the conclusion and how much reading it rests on. Count with `scripts/tally.py` over every notes file (first round, second pass and any Learn-step reading), so a source several readers saw counts once. Before counting, read each note's account of how its sources came back: a source that came back only as the fetch tool's summary or in fragments moves to Glimpsed, whatever the note calls it.
2. **Questions and method.** What was asked, and the goals in their priority order. The sources and channels swept, the recency window, and the data windows and groups measured (customers and staff apart).
3. **Terms used here.** Every internal or field term the report relies on, one line each, before the first section that uses it.
4. **Our system's pros and cons, checked.** Cover each pro, con and flaw the user named, as far as the topic touches it. Say whether the code and the production data confirm it, refute it or reframe it, with the numbers, because the user's impression can be wrong. Then add the pros and cons the user did not name. Real customer usage, including the feedback hidden in session text, is the main evidence. Describe the system only as far as a reader needs it to follow these verdicts. Reading the whole system is what lets the analysis fit our case; it is not content for the page.
5. **What the field says.** One section per question or theme, each header stating the finding ("Leaner prompts score higher", not "Prompt length"). Each section covers what is established, what rests on a single source, where sources disagree, and what changed recently. Every claim is cited.
6. **What it means for us.** This is where the learnings meet our use case and the checked pros and cons from section 4:
   - **Doing right:** practice that matches the evidence, so that it is kept on purpose.
   - **Doing wrong or missing:** practice the evidence contradicts, or that the field does and we do not, each with its measured cost to us.
   - **A gap table:** our practice against the field, dimension by dimension.
   - **Shortcuts our product allows:** what our scale, schema, users or team let us skip or simplify relative to the general advice.
7. **Directions.** The most impactful learnings turned into ways to apply them, ranked by expected impact on the measured problems and the top goal. Each direction gives:
   - what would change in our system;
   - the evidence behind it (citations plus our numbers);
   - what it would not fix.

   These are directions for the proposal, not decisions.
8. **Threats to validity.** What was not measured, what rests on one source or a small sample, and where the data window or the staff-heavy usage mix could mislead.
9. **References.** Author–date (APA 7) in one alphabetical list, rendered by `scripts/references.py`; papers, documentation, industry sources and internal sources (PRs, design docs, queries) all go in it. ✓ marks a source a notes file's reading tally lists as read in full; the script sets it from the notes, so the marks and the tally always agree.

## Writing

- Plain words per AGENTS.md (Communication): name each idea before explaining it, and lead each section with its finding.
- Use tables where they compare, prose elsewhere. A diagram earns its place when the system's flow is the point.
- Every literature claim carries a citation; a claim with no source is dropped rather than kept unsourced. Every measured fact states its window and its counts.
- Cite in the draft with keys and let the script write the author and year. Write `[@key]` or `[@key; @other]` for a parenthetical citation, which renders "(Wang et al., 2026)". Write a bare `@key` for a narrative mention, which renders "Wang et al. (2026)". Never type the author and year by hand: a hand-typed citation gets no link, and its source drops out of the reference list. Each rendered citation links to its source, so a reader can open it from the text.
