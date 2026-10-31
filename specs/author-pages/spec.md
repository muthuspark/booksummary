# Author pages — Spec

## Summary

<!-- Format: State the outcome, scope, and measurable reason for doing this. -->

Readers can click author names from book summaries and catalog cards to browse every summarized book attributed to that person. An alphabetical Authors directory makes authors independently discoverable. Coauthored books appear under each credited author.

## Problem

<!-- Format: Describe the current behavior, observed failure/opportunity, affected users, and evidence. -->

Author names currently appear as plain text, so a reader who enjoys a book cannot follow its author to other summaries. Existing category browsing groups topics rather than people. Exploration found 839 summaries, 720 distinct author display strings, and 85 summaries with apparent coauthor credits across 78 strings. These counts are a baseline, not fixed acceptance targets. Grouping by the full display string would fragment authors such as John Gottman between solo and collaboration pages.

## Goals and Non-Goals

<!-- Format: Use `### Goals` and `### Non-goals` headings, each followed by a Markdown bullet list. Keep each item testable or explicitly bounded. -->

- Goals: clickable individual authors in summary headers and all shared catalog cards; complete author catalogs across categories; an alphabetical author directory with counts; consistent discovery for future summaries.
- Non-goals: external bibliographies, author biographies or portraits, fuzzy author search, author-specific recommendation sections, rewriting book titles or body prose, and changing existing summary URLs.

## Users and Scenarios

<!-- Format: Use `### Actors` followed by a Markdown bullet list, then `### Scenarios` followed by a Markdown numbered list. Include the expected result for each scenario. -->

- A reader follows a linked author from a summary to discover other summarized books.
- A reader follows an author from the homepage, category listings, related-book cards, or an author catalog.
- A reader opens Authors from site navigation, selects a person, then opens a summary.
- A contributor adds a solo or coauthored summary and expects it to appear under every credited author.

## Requirements

<!-- Format: Use stable IDs such as REQ-001. For each requirement state the behavior, inputs/outputs, and priority. -->

- REQ-001: Each individual author in summary-header credits and shared catalog-card metadata is a descriptive, keyboard-accessible internal link.
- REQ-002: Author catalogs use /authors/<author-slug>/ and include all and only published summaries attributed to that author, across categories, once each.
- REQ-003: Catalogs show the author name, total summary count, alphabetical book listing, and pagination using the existing catalog page size.
- REQ-004: Coauthors receive separate links and share membership of the same summary; existing readable attribution and book titles are preserved.
- REQ-005: /authors/ lists authors alphabetically with accurate summary counts. Site navigation includes Authors.
- REQ-006: New summaries participate without manually maintaining author directory pages.
- REQ-007: Author pages remain usable without client-side JavaScript and fit the existing responsive site presentation.
- REQ-008: The author directory provides a labelled name filter with live result counts, clear and no-results states, plus letter headings and jump links. Matching ignores case and accents and accepts any part of a name. All authors and letter navigation remain available without JavaScript. Rows remain compact, readable, and keyboard accessible across screen sizes.

## User/System Flows

<!-- Format: Use numbered steps. Name the actor, system action, state change, and failure branch at each relevant step. -->

1. Reader opens a summary or book listing, focuses or clicks a linked author name, and reaches that author's catalog.
2. Reader sees the author name and count, browses alphabetical summaries, follows pagination when needed, and selects a book.
3. Reader selects Authors in navigation, scans the alphabetical directory and counts, then opens an author catalog.
4. Contributor supplies individual author credits with a new summary; the next successful build includes the summary on each author's page and updates directory counts.

## Decisions and Constraints

<!-- Format: Use `### Confirmed Decisions`, `### Assumptions`, `### Constraints`, and `### Open Questions` headings, each followed by Markdown bullets. Do not hide unresolved choices. -->

### Confirmed Decisions
- The user requested clickable author names and a way to browse an author's books, then invoked specification after the exploration recommendation.
### Assumptions
- The exploration's recommended scope is the specification baseline: individual coauthors, a directory, navigation, and alphabetical catalogs.
- Book counts refer only to published summaries on this site, not a complete external bibliography.
### Constraints
- Preserve existing summary URLs, display attribution, category browsing, metadata search compatibility, and publishing workflow.
- Use established site typography, responsive behavior, and native links.
### Trade-offs
- Accurate coauthor membership requires reviewing existing attribution rather than grouping whole display strings.
### Open Questions
- No unresolved product questions; ambiguous identity or attribution discovered during migration requires evidence before assigning a person.

## Edge Cases and Failure Handling

<!-- Format: Use a case/action table or bullets with trigger, expected behavior, recovery, and user-visible error. -->

- An author with one summary still has a working catalog.
- Where reviewed primary attribution proves a legacy credit inaccurate, author links display the verified individual names; the legacy title and text are retained.
- Coauthors with shared surnames are expanded into their individual credited names after review; punctuation or the word "and" alone is insufficient evidence.
- Repeated credit of the same author does not duplicate a book or inflate counts.
- Names containing initials, punctuation, or diacritics retain readable labels and resolve to working URLs.
- Conflicting names or URL collisions must be resolved explicitly before release; unrelated people must not silently share a catalog.
- Missing, empty, or malformed individual author attribution prevents a verified release and identifies the affected summary.
- Authors with no published summaries do not appear in the directory.
- A renamed attribution is reviewed for its URL impact; redirects for historical author URLs are outside this initial release.

## Acceptance Criteria

<!-- Format: Use stable IDs such as AC-001. Make each criterion observable and state how it will be verified. -->

- AC-001: Every published summary header and every shared book-card occurrence renders individual author links pointing to existing internal author catalogs; verify generated HTML and keyboard navigation.
- AC-002: Each author catalog contains exactly that author's published summaries across categories, including solo and coauthored books, with no duplicates. Verify complete generated membership against source attribution and explicit John Gottman and Daniel Goleman regression cases.
- AC-003: /authors/ is reachable from site navigation, lists every published author alphabetically exactly once, and displays accurate counts; verify generated directory and navigation.
- AC-004: Each author catalog shows its readable name and total count and orders books alphabetically across pagination at the existing page size; verify one-book and synthetic multi-page cases.
- AC-005: Existing summary URLs, author display strings, search-record compatibility, category browsing, images, and feeds pass existing regression checks.
- AC-006: Initials, punctuation, diacritics, shared-surname coauthors, duplicate credits, malformed attribution, and slug collisions are covered by migration review or focused verification. Invalid data fails verification with an actionable source reference.
- AC-007: New solo and coauthored summaries created through the documented and automated writing paths supply valid author attribution and appear under every credited author; verify automation tests and build fixtures.
- AC-008: Author links, directory, and catalogs work without JavaScript; keyboard focus remains visible and layouts are readable on mobile and desktop; verify representative pages.
- AC-009: Verify author-name filtering by first/last/partial name, case and accents, clearing, no results, letter heading jumps, compact touch targets, enlarged text, and full directory access without JavaScript.

## Explanation and Output Artifacts

<!-- Format: Use a Markdown bullet list with separate `Audience:`, `Writing profile:`, `Primary artifact:`, `Supporting artifacts:`, and `Accessibility:` fields. Prefer an 80% ASD-STE100 controlled-language style for explanatory prose unless strict ASD-STE100 or plain language is required. Choose the clearest medium: prose, diagram, interactive HTML, or narrated explainer video. State the topic, purpose, interaction or narration needs, delivery location, and acceptance evidence for each requested artifact. -->

- Deliver author catalogs, the Authors directory, and navigation links with the feature implementation.
- Update contributor documentation with solo/coauthor examples and explain that author catalogs contain summaries available on this site.
- Record migration evidence, checks performed, and any deviations in the implementation handoff. Implementation and verification are complete; plan.md records the technical changes and verification evidence, and task.md tracks execution.
