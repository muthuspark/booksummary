#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

./scripts/build_site.sh

git add .
current_date=$(date +"%Y-%m-%d %H-%M-%S")
commit_message=${1:-"Release $current_date"}
if git diff --cached --quiet; then
  printf 'No changes to commit.\n'
else
  git commit -m "$commit_message"
fi
git push
printf 'Deployment completed successfully!\n'
