#!/usr/bin/env bash
# Improve up to two existing summaries using Search Console growth signals.
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd -- "$ROOT"
PYTHON=python3
if [[ -x "$ROOT/.venv/bin/python3" ]]; then
  PYTHON="$ROOT/.venv/bin/python3"
fi
dry_run=false
publish=false
codex_options=()
analytics_options=()
usage() {
  cat <<'HELP'
Usage: scripts/improve_trending_summaries.sh [OPTIONS]

Compare adjacent 28-day GSC windows, select up to two growing summaries, and
ask Codex to improve content and visuals where useful. Build and verify locally.

  --dry-run              Fetch/select and print the prompt; do not run Codex/build
  --count 1|2            Maximum articles (default: 2)
  --credentials FILE     Service-account JSON (default: GOOGLE_APPLICATION_CREDENTIALS)
  --property PROPERTY    GSC property (default: sc-domain:summaries.muthu.co)
  --analytics-json FILE  Replay a previously saved analytics.json without GSC access
  --model MODEL          Override the configured Codex model
  --profile PROFILE      Use a named Codex configuration profile
  --publish              After verification, commit and push with render_publish.sh
  -h, --help             Show help

Requires Python 3.11+, Git and flock; live data also needs requirements-gsc.txt.
Editing requires an authenticated Codex CLI and Hugo. Reports and prompts are
kept under .git/gsc-improver/. Credentials are never sent to Codex.
GOOGLE_APPLICATION_CREDENTIALS is read from the environment or the project's .env.
Uses the project's .venv Python when available.
HELP
}
while (($#)); do
  case "$1" in
    --dry-run) dry_run=true; shift ;;
    --publish) publish=true; shift ;;
    --model|--profile|--count|--credentials|--property|--analytics-json)
      if (($# < 2)) || [[ -z "$2" || "$2" == --* ]]; then
        printf 'Missing value for %s\n' "$1" >&2; exit 2
      fi
      case "$1" in
        --model|--profile) codex_options+=("$1" "$2") ;;
        *) analytics_options+=("$1" "$2") ;;
      esac
      shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'Unknown option: %s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
done
for dependency in "$PYTHON" git flock; do
  command -v "$dependency" >/dev/null || { printf 'Missing dependency: %s\n' "$dependency" >&2; exit 1; }
done
if ! "$dry_run"; then
  for dependency in codex hugo; do
    command -v "$dependency" >/dev/null || { printf 'Missing dependency: %s\n' "$dependency" >&2; exit 1; }
  done
  # Share the writer's lock to prevent concurrent content/build operations.
  exec 9>"$(git rev-parse --git-path summary-writer.lock)"
  flock -n 9 || { printf 'Another summary-writing run is active.\n' >&2; exit 1; }
  if "$publish" && [[ -n "$(git status --porcelain)" ]]; then
    printf 'Publishing requires a clean checkout because render_publish.sh stages all changes.\n' >&2
    exit 1
  fi
fi
umask 077
report_root="$(git rev-parse --git-path gsc-improver)"
mkdir -p -- "$report_root"
run_dir="$(mktemp -d "$report_root/run.XXXXXXXX")"
printf 'Run report: %s\n' "$run_dir"
"$PYTHON" scripts/gsc_summary_candidates.py prepare --output "$run_dir" "${analytics_options[@]}"
[[ -f "$run_dir/prompt.txt" ]] || exit 0
if "$dry_run"; then
  cat "$run_dir/prompt.txt"
  exit 0
fi
codex --search --ask-for-approval never exec \
  --sandbox workspace-write -c sandbox_workspace_write.network_access=true \
  --cd "$ROOT" --output-last-message "$run_dir/result.txt" "${codex_options[@]}" - < "$run_dir/prompt.txt"
"$PYTHON" scripts/gsc_summary_candidates.py validate --output "$run_dir"
./scripts/build_site.sh
if "$publish"; then
  if [[ -z "$(git status --porcelain)" ]]; then
    printf 'No changes after review and build; nothing to publish.\n'
  else
    ./render_publish.sh 'Improve summaries gaining search traction'
  fi
else
  printf 'Verified locally. Review changes; use render_publish.sh when ready to publish.\n'
fi
