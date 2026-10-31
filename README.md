# Book Summaries

A Hugo site containing 830 book summaries in 15 categories, using the
[Shibui theme](https://github.com/ntk148v/shibui).

Live site: https://summaries.muthu.co/

The site defaults to Shibui’s light theme, regardless of the system color scheme.

## Requirements

- Hugo **0.164.0** (the CI version; standard or extended build)
- Python **3.11+** for the build verifier

The theme and standalone SVG diagram images are included in this repository. Building
does not require Quarto, Pandoc, Graphviz, Node.js, Go modules, or a theme download.

## Preview

```sh
hugo server
```

Open the localhost URL printed by Hugo (normally http://localhost:1313/).
The development configuration writes to ignored `public/`, keeping localhost URLs
and live reload out of `docs/`.
If the port is already in use, add `--port 1314`.

## Build and verify

```sh
./scripts/build_site.sh
```

This builds a clean production site into `docs/` and checks every summary route,
image, search record, diagram image, canonical URL, structured-data block, feed,
and local HTML link. It also checks that Google ad scripts and Quarto runtime
files are absent. This build-only script does **not** commit or push changes.

To run the steps separately:

```sh
hugo --minify --cleanDestinationDir --panicOnWarning
python3 scripts/verify_site.py docs
```

`--cleanDestinationDir` removes stale generated files, including the old Quarto
libraries. Keep source files in `content/`, `static/`, `assets/`, or `layouts/`,
never in `docs/`.

## Publish

The production output remains `docs/`, including `CNAME` for
`summaries.muthu.co` and `.nojekyll`. This preserves the GitHub Pages arrangement
that publishes from the repository's `/docs` folder.

Review your changes, then run:

```sh
./render_publish.sh
# Or supply a commit message:
./render_publish.sh "Update book summaries"
```

The publish script builds and verifies the site, stages all repository changes,
commits them using your message or `Release YYYY-MM-DD HH-MM-SS`, and runs
`git push`. It stops if the build, verification, or commit fails. If there are no
changes to commit, it still pushes any existing local commits.

Hugo copies `CNAME` and `robots.txt` from `static/` automatically; no manual copy
commands are needed.

In GitHub Settings → Pages, the publishing source should be **Deploy from a
branch**, with that branch and the **/docs** folder selected. The custom domain
remains **summaries.muthu.co**. DNS does not change for this migration.

The GitHub Actions workflow builds and verifies pull requests and pushes to
`main`/`master`, then uploads the generated site as an artifact. It does not modify
the repository or deploy automatically; publishing continues through the existing
Pages branch configuration.

## Content and assets

Each summary is a Hugo leaf bundle:

```text
content/posts/productivity_and_habits/atomic-habits/
├── index.md
└── image.png
```

Its URL remains `/posts/productivity_and_habits/atomic-habits/`, and the explicit
`/posts/productivity_and_habits/atomic-habits/index.html` URL still works.
Directory names, including underscores, were preserved.

A new summary needs YAML front matter followed by Markdown:

```yaml
---
title: "Book Title by Author"
author: "Author"
authors: ["Author"]
categories: ["Productivity And Habits"]
description: "A concise description of the book."
image: "image.png"
---
```

The `author` field preserves the readable display credit used by titles and search.
The `authors` field groups books under individual author pages. It is required and
must be a **one-line JSON array** of nonblank, unique, double-quoted names (valid
YAML). Other YAML list forms are not supported by the standard-library verifier.
Reuse each author's existing canonical spelling, including initials and diacritics.
For a coauthored book, include each person separately:

```yaml
author: "John Gottman and Nan Silver"
authors: ["John Gottman", "Nan Silver"]
```

Expand shared surnames in the list, for example `authors: ["Nicky Lee", "Sila Lee"]`.
Verify credits against the author or publisher rather than splitting display text
mechanically. Known spelling variants and duplicate names fail verification.
If two different people would share a name or route, resolve their distinct author
term paths and verification expectations explicitly before publishing.

Run `python3 scripts/author_pages.py` to validate source credits, or
`python3 scripts/test_author_pages.py` for attribution and Hugo pagination fixtures.
The full build checks every author directory entry, count, catalog, and credit link.

Place its image beside `index.md`. Dates are optional; the migrated summaries did
not have publication dates, so listings sort alphabetically and omit invented
dates. The home and section feeds contain up to 50 summaries. Add a date and
adjust the list/feed sort if chronological publishing is needed later.

- `content/_index.md`: homepage introduction.
- `hugo.toml`: domain, metadata, analytics, menus, taxonomy, and output settings.
- `assets/css/custom.css`: small additions for book listings, search, and diagrams.
- `layouts/`: project overrides; the Shibui base layout and CSS remain active.
- `static/`: domain file, robots.txt, logos, browser scripts, and other shared assets.
- `docs/`: generated production site, tracked for GitHub Pages.

## Write a random planned summary

`scripts/write_random_summary.sh` picks one unchecked book from `progress.md` and
uses [Codex noninteractive mode](https://learn.chatgpt.com/docs/non-interactive-mode)
to research and write its summary with a suitable hero image and SVG diagrams when
useful. It follows the category heading, creates a new leaf bundle, and skips
existing bundles, including partial work from an earlier run.

```sh
# Preview a random selection and its full prompt without running Codex:
./scripts/write_random_summary.sh --dry-run

# Write and publish one randomly selected summary:
./scripts/write_random_summary.sh

# Optionally use a configured model or profile:
./scripts/write_random_summary.sh --model YOUR_MODEL --profile YOUR_PROFILE
```

Install and authenticate Codex (`codex login`) first. The script also requires
Bash, Python 3.11+, Git, `flock`, and Hugo on `PATH`. It uses your configured Codex
model, tools, and skills, enables web search and workspace network access, and
runs with the workspace-write sandbox. Image generation must be available to the
Codex session; a relevant licensed image with attribution is an allowed fallback.
The image must be saved as a real `image.png` of at least 512px in each dimension,
with provenance in `image-source.md`. Graphviz is needed if new flow diagrams
are rendered through the existing diagram generator.

The script independently checks the article and image, builds and verifies the
site, confirms the published metadata matches the selected book, then checks off
its progress entry and updates the totals. Only one run can execute at a time.
Writing or validation failures keep the book unchecked and preserve partial files
for review; finish or remove that partial bundle before expecting it to be selected
again. After a successful run, the script calls `./render_publish.sh`, which rebuilds,
stages all repository changes, commits, and pushes. Dry runs and runs with no eligible
books do not publish. A publishing failure returns a nonzero status and leaves the
completed summary checked off; fix the publishing issue and rerun `./render_publish.sh`.

Run the isolated automation tests without calling Codex:

```sh
python3 scripts/test_write_random_summary.py
```

## Categories and diagrams

Browse summaries using the category links and page navigation. Author names in
summary headers and book cards open catalogs of their solo and coauthored books
across categories. The Authors navigation link opens an alphabetical directory
with counts. Catalogs include summaries available on this site, not external
bibliographies. Search controls
are not displayed, and the browser search scripts are not loaded.

Hugo creates 80px and 160px WebP thumbnails for listings and search results. Original
images remain available in each article bundle. Homepage counts are derived from
published content, and category navigation remains above the catalog.

Diagrams are standalone SVG images beside each summary, referenced with standard
Markdown image syntax. They display without JavaScript, include accessible text,
and remain sharp at any zoom level. Original embedded HTML diagrams remain
supported; Markdown rendering permits trusted HTML from this repository.

The 1,023 converted diagrams have editable node, connection, and group definitions
in `scripts/diagrams.json`. To regenerate them after editing those definitions,
install Graphviz and run:

```sh
python3 scripts/render_diagrams.py
# Or regenerate one summary's diagrams:
python3 scripts/render_diagrams.py --only think-like-a-programmer
```

Graphviz is only needed to regenerate diagram assets, not to build or view the
site. After adding a new diagram definition, add its Markdown image reference to
the summary and run the build verifier.

Google Analytics (`G-Q0SHDCJVLL`) is preserved. Google AdSense scripts and the
obsolete publisher `ads.txt` are removed.

## Theme maintenance

Shibui is vendored in `themes/shibui/`, including its MIT license. The exact
upstream revision is recorded in `themes/shibui/UPSTREAM_COMMIT`. No submodule
initialization is needed when cloning this repository.

For updates, compare the recorded revision with upstream, replace the vendored
theme files from a reviewed upstream revision, update `UPSTREAM_COMMIT`, and run
the build verifier. Keep project changes outside the vendored theme. The local
layout overrides add the catalog, hero images, search, undated posts, and book SEO
metadata while inheriting Shibui's base layout and styles.
