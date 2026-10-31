---
target: "Authors directory, Image #1 and layouts/_default/terms.html"
total_score: 27
p0_count: 0
p1_count: 1
timestamp: 2026-10-31T06-56-54Z
slug: layouts-default-terms-html
---
# Authors directory critique

## Anti-patterns verdict

**Pass:** this does not look like a generic AI-generated interface. The light surface, Crimson Text, and plain list fit the reading site. Keep that identity. The opportunity is better retrieval and grouping.

The deterministic scan was unavailable: detect.mjs exited with “Error: bundled detector not found.” The browser overlay also failed because detect.js returned HTTP 404. These are tooling failures, not evidence that the page has zero issues. Manual browser inspection supplied the evidence below.

## Overall impression

The directory is clear at first glance but inefficient at its actual scale. A reader can understand the page immediately and still struggle to reach Virginia Woolf. The biggest improvement is helping readers reach a name quickly.

## Design health: 27/40

| Heuristic | Score | Key finding |
|---|---:|---|
| Visibility of system status | 3/4 | Authors is active; directory size and current letter are absent. |
| Match with the real world | 3/4 | Plain names and counts; displayed-name ordering needs a cue. |
| User control and freedom | 3/4 | Native navigation and Back work. |
| Consistency and standards | 3/4 | Cohesive typography; mobile scanning pattern changes. |
| Error prevention | 3/4 | Broad linked rows support accurate selection. |
| Recognition rather than recall | 2/4 | No letter landmarks or surname lookup. |
| Flexibility and efficiency | 1/4 | Browser Find is the only practical lookup accelerator. |
| Aesthetic and minimalist design | 3/4 | Uncluttered, but spacing weakens information grouping. |
| Error recovery | 3/4 | Navigation is reversible; no input-error flow to assess. |
| Help and documentation | 3/4 | Intro explains counts and coauthors. |
| **Total** | **27/40** | **Acceptable; retrieval improvements needed.** |

Scores apply to this low-risk directory, not a full accessibility or error-state audit.

## What works

- Clear heading and active Authors navigation establish location immediately.
- Quiet typography suits extended reading. Names lead and counts stay secondary.
- Entire author rows are clickable. Keyboard focus is visible, and tested desktop/mobile layouts have no horizontal overflow.

## Priority issues

### P1: Finding an author requires too much scrolling

There are 779 entries, with no search or letter jumps. The rendered page is roughly 47,000px tall on desktop and 81,500px on mobile. A reader seeking a later name must scroll extensively or know browser Find.

**Fix:** add a labelled “Find an author” field matching any part of a name, with result count, clear action, and no-results guidance. Pair it with A–Z jumps for browsing. Retain the full static directory as a fallback.

**Suggested command:** impeccable shape, then craft, focused on author lookup.

### P2: Mobile spacing separates names from their counts

At 390px wide, linked rows measure 88px high, with approximately 104px between row starts. The name and its count read as separate items, reducing visible entries and increasing thumb scrolling.

**Fix:** keep short names and counts on one row when space permits. Let long names wrap, with their count closely attached. Retain at least 44px touch targets and readable name text.

**Suggested command:** impeccable adapt.

### P2: The long list has no internal landmarks

One H1 leads into an uninterrupted list. Readers lose alphabetical orientation; screen-reader heading navigation cannot jump between letters.

**Fix:** add letter section headings and stable fragment targets, connected to the A–Z navigation. Add “779 authors · A–Z by displayed name” as a compact ordering cue. Avoid automatic surname parsing across culturally varied names.

**Suggested command:** impeccable layout and clarify.

### P3: Counts feel detached on the wider layout

The large empty interval between name and count makes it harder to connect the two visually.

**Fix:** bring the count column closer or modestly narrow the list. Preserve the plain rows; extra cards, portraits, and decorative separators would add noise.

**Suggested command:** impeccable polish.

## Cognitive load and emotional journey

**Moderate load:** two checklist failures, chunking and mobile grouping. The problem is traversal, not 779 simultaneous decisions. Five familiar navigation links do not justify an overload finding.

Arrival feels calm and understandable. That confidence fades when the sought author starts with a later letter and no shortcut appears. A quick successful lookup would provide the strongest improvement to the experience.

## Persona red flags

- **Alex, frequent reader:** locating Virginia Woolf depends on browser Find or extensive scrolling.
- **Sam, keyboard user:** native links and focus work, but hundreds of links lack heading-based shortcuts. A real screen-reader session was not run.
- **Casey, mobile reader:** broad targets help tapping, but stacked counts increase scrolling and weaken scanning.

## Minor observations

- Links resemble ordinary text at rest; a subtle consistent affordance could help first-time visitors.
- “Authors | Book Summaries” would finish the lowercase browser title.
- Keep the existing light palette and Crimson Text. A visual redesign is unnecessary for these fixes.

## Questions to consider

1. Which lookup approach should lead: **search plus A–Z jumps (recommended)**, **A–Z jumps only**, or **search only**?
2. Which scope: **retrieval plus mobile spacing (recommended)** or **all four issues**?
