#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

python3 scripts/author_pages.py
printf 'Building site with Hugo...\n'
hugo --minify --cleanDestinationDir --panicOnWarning
python3 scripts/verify_site.py docs
printf 'Site built and verified in docs/.\n'
