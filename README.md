# Book Summaries

A Hugo site containing 830 book summaries in 15 categories, using the
[Shibui theme](https://github.com/ntk148v/shibui).

Live site: https://summaries.muthu.co/

The site defaults to Shibui’s light theme, regardless of the system color scheme.

## Requirements

- Hugo **0.164.0** (the CI version; standard or extended build)
- Python **3.11+** for the build verifier

The theme and Mermaid browser runtime are included in this repository. Building
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
image, search record, Mermaid block, canonical URL, structured-data block, feed,
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
categories: ["Productivity And Habits"]
description: "A concise description of the book."
image: "image.png"
---
```

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

## Categories and diagrams

Browse summaries using the category links and page navigation. Search controls
are not displayed, and the browser search scripts are not loaded.

Hugo creates 80px and 160px WebP thumbnails for listings and search results. Original
images remain available in each article bundle. Homepage counts are derived from
published content, and category navigation remains above the catalog.

Mermaid fences use standard Markdown syntax: an opening fence of three backticks
followed by `mermaid`. The local runtime renders diagrams as they approach the
viewport; the source remains available if a diagram fails to render or JavaScript
is disabled. The two original Graphviz diagrams were exported to adjacent SVGs,
so Graphviz is no longer a build dependency. Original embedded HTML diagrams
remain supported; Markdown rendering permits trusted HTML from this repository.

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
