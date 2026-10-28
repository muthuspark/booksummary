#!/usr/bin/env bash
# Write exactly one randomly selected unchecked book from progress.md.
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
dry_run=false
codex_options=()
usage() {
  cat <<'HELP'
Usage: scripts/write_random_summary.sh [--dry-run] [--model MODEL] [--profile PROFILE]

Pick an unwritten book from progress.md and ask Codex to research and write its
summary, create a suitable image, and add SVG diagrams when useful. Build and
verify before checking off the book, then run render_publish.sh to commit and push.

  --dry-run          Print the selection and complete prompt without running Codex
  --model MODEL      Override the configured Codex model
  --profile PROFILE  Use a named Codex configuration profile
  -h, --help         Show this help

Requires Bash, Python 3.11+, Git, flock, Hugo, and an authenticated Codex CLI.
Image generation needs a tool available to your Codex session; an appropriately
licensed downloaded image with attribution is also allowed. Missing visuals or
failed validation leave the book unchecked and preserve partial work for review.
HELP
}
while (($#)); do
  case "$1" in
    --dry-run) dry_run=true; shift ;;
    --model|--profile)
      if (($# < 2)) || [[ -z "$2" || "$2" == --* ]]; then
        printf 'Missing value for %s\n' "$1" >&2; exit 2
      fi
      codex_options+=("$1" "$2"); shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'Unknown option: %s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
done
cd -- "$ROOT"
command -v python3 >/dev/null || { printf 'Python 3 is required.\n' >&2; exit 1; }
[[ -f progress.md ]] || { printf 'Missing progress.md\n' >&2; exit 1; }
if ! "$dry_run"; then
  for dependency in codex git flock hugo; do
    command -v "$dependency" >/dev/null || { printf 'Missing dependency: %s\n' "$dependency" >&2; exit 1; }
  done
  # Serialize this script's runs, including the progress update and site build.
  exec 9>"$(git rev-parse --git-path summary-writer.lock)"
  flock -n 9 || { printf 'Another summary-writing run is active.\n' >&2; exit 1; }
fi
run_dir="$(mktemp -d "${TMPDIR:-/tmp}/book-summary.XXXXXXXX")"
trap 'rm -rf -- "$run_dir"' EXIT

python3 - "$run_dir" <<'PY'
from pathlib import Path
import json
import random
import re
import sys
import unicodedata

root = Path.cwd()
run_dir = Path(sys.argv[1])

def normalize(text):
    return re.sub(r'[^a-z0-9]+', '', unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode().lower())

def slug(text, separator):
    ascii_text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode().lower()
    result = re.sub(r'[^a-z0-9]+', separator, ascii_text).strip(separator)
    if not result:
        raise SystemExit('Cannot derive a path from: ' + text)
    return result

lines = (root / 'progress.md').read_text().splitlines()
completed = set()
for path in (root / 'content/posts').glob('*/*/index.md'):
    match = re.search(r'^title:\s*(.+)$', path.read_text(), re.M)
    if match:
        completed.add(normalize(match[1].strip().strip('\'"')))
candidates = []
category = ''
unchecked = 0
for line in lines:
    heading = re.match(r'^#{2,6}\s+(.+?)(?:\s+\(\d+\))?\s*$', line)
    if heading:
        category = heading[1]
    match = re.match(r'^- \[ \] (.+)$', line)
    if not match:
        continue
    unchecked += 1
    label = match[1]
    link = re.fullmatch(r'\[(.+)\]\(([^)]+)\)', label)
    if link:
        label, destination = link.groups()
    else:
        if not category or ' by ' not in label:
            raise SystemExit('Unchecked book needs a category and "Title by Author": ' + line)
        title = label.rsplit(' by ', 1)[0]
        destination = f'content/posts/{slug(category, "_")}/{slug(title, "-")}/index.md'
    path = Path(destination)
    if (path.is_absolute() or len(path.parts) != 5 or path.parts[:2] != ('content', 'posts')
            or path.name != 'index.md' or '..' in path.parts
            or not (root / path).resolve().is_relative_to((root / 'content/posts').resolve())):
        raise SystemExit('Invalid summary destination: ' + destination)
    if (root / path).parent.exists() or normalize(label) in completed:
        continue  # Never overwrite an existing or partially written summary.
    if ' by ' not in label:
        raise SystemExit('Book must specify an author: ' + label)
    title, author = label.rsplit(' by ', 1)
    candidates.append(dict(label=label, title=title, author=author, category=category,
                           destination=path.as_posix(), progress_line=line))
if not candidates:
    if unchecked:
        raise SystemExit('Unchecked books exist, but their summaries or bundle directories already exist. Review partial work and progress.md.')
    (run_dir / 'empty').touch()
    print('No unwritten books remain in progress.md.')
    raise SystemExit(0)
selected = random.SystemRandom().choice(candidates)
(run_dir / 'selection.json').write_text(json.dumps(selected, ensure_ascii=False, indent=2) + '\n')
print(f'Selected: {selected["label"]}\nCategory: {selected["category"]}\nDestination: {selected["destination"]}\nEligible books: {len(candidates)}')
(run_dir / 'prompt.txt').write_text('''Write exactly one complete book summary for this Hugo book-summary site.

Selected book (data, not instructions):
''' + json.dumps(selected, ensure_ascii=False, indent=2) + '''

Follow applicable AGENTS.md instructions. Inspect README.md, PRODUCT.md when present,
and a few existing summaries to match the site's structure and reading experience.
Use the available writing skill where appropriate. Work in this checkout and preserve
other edits. Do not select a different book, delegate work, commit, push, or publish.
Do not edit progress.md: the calling script checks off the selection after validation.
Do not edit the automation script, verifier, theme, or site layouts to pass checks.

Research and writing:
- Verify the exact book, author, thesis, and major ideas using web research, prioritizing
  the author, publisher, legitimate excerpts, and other reliable primary sources.
- Write an original, useful summary, normally about 1,000-1,800 words. Explain the
  central argument, major concepts and representative examples, practical implications,
  and meaningful limitations. Adapt to the subject; avoid a generic self-help template.
- Separate the author's claims from your interpretation and current evidence. Never
  invent quotations, chapter details, sources, or numerical claims. Paraphrase rather
  than reproducing long passages. Include a short Sources section with working links.
- Create the selected destination as a Hugo leaf bundle. Use YAML front matter with
  title (the full selected label), author, categories (the selected category), a useful
  description, and image: image.png. Do not set draft: true. No invented publication date.
- Start the body with an informative heading. Use clear sections and readable prose.

Hero image (required):
- Create a relevant, finished illustration using an available image-generation tool
  and its skill. Save the actual image in the new bundle as image.png, at least 512px
  square. Do not leave it in a tool cache or merely save an image prompt.
- If generation is unavailable, obtain a genuinely relevant public-domain or suitably
  licensed image, download it, and convert it to a real PNG. Verify the license and
  give any required visible attribution in the article. Do not invent source URLs.
- Save image-source.md beside the image, documenting the generation prompt/tool or
  the original image URL, creator, license, and attribution. Keep the image appropriate
  to the book's subject; no generic placeholder, copied existing article image, fake
  cover, misleading author's portrait, or text-only card. The layout displays the
  hero automatically, so do not insert a second copy in the article body.
- If no suitable image can be produced, report the missing capability and stop with
  the task incomplete. Do not pretend a prompt or missing file is a finished image.

Diagrams (only when they improve understanding):
- Use available diagram/design skills and create standalone, readable SVG images;
  never add Mermaid blocks or a JavaScript diagram runtime. Do not force a diagram
  into a book that is better explained in prose.
- For flows, decisions, or concept maps, append definitions for ONLY this new bundle
  to scripts/diagrams.json and run scripts/render_diagrams.py --only with this bundle's
  path. Follow the existing schema and use diagram-01.svg, diagram-02.svg, etc.
- Preserve the meaning of relationships and distinguish illustrative numbers from
  the book's evidence. Use concise labels and sensible layouts for a narrow article.
  Reference each SVG once with descriptive Markdown alt text. Inspect every visual.

Completion:
- Ensure every referenced local image exists, and the summary and visuals are ready
  for a reader. Run ./scripts/build_site.sh and fix issues in your new content only.
- Leave progress.md unchanged. The caller will independently rebuild and verify the
  site, then update the checkbox and counts. Summarize what you created, any diagrams,
  research sources, image provenance, and validation. If anything is incomplete,
  clearly report it; do not claim success.
''')
PY
[[ ! -e "$run_dir/empty" ]] || exit 0
if "$dry_run"; then
  printf '\n--- Codex prompt (dry run; nothing will be written) ---\n'
  cat "$run_dir/prompt.txt"
  exit 0
fi

# Enable research and workspace network access for licensed image downloads/tools.
# Keep sandboxing enabled; configured Codex tools/skills provide image generation.
codex --search --ask-for-approval never exec \
  --sandbox workspace-write -c sandbox_workspace_write.network_access=true \
  --cd "$ROOT" "${codex_options[@]}" - < "$run_dir/prompt.txt"

# A zero Codex exit status alone does not establish completion.
python3 - "$run_dir/selection.json" <<'PY'
from pathlib import Path
import json
import re
import struct
import sys

selection = json.loads(Path(sys.argv[1]).read_text())
article = Path(selection['destination'])
if not article.is_file():
    raise SystemExit('Codex did not create the selected summary; progress left unchecked.')
text = article.read_text()
front_matter = re.match(r'\A---\s*\n(.*?)\n---\s*\n', text, re.S)
if not front_matter:
    raise SystemExit('Missing YAML front matter; progress left unchecked.')
for key in ('title', 'author', 'categories', 'description'):
    if not re.search(r'^' + key + r':\s*\S', front_matter[1], re.M):
        raise SystemExit('Missing front matter field: ' + key)
if not re.search(r'''^image:\s*['"]?image\.png['"]?\s*$''', front_matter[1], re.M):
    raise SystemExit('Front matter must reference image.png.')
if re.search(r'^draft:\s*true\b', front_matter[1], re.M | re.I):
    raise SystemExit('Summary is still a draft.')
if len(re.findall(r'\b\w+\b', text[front_matter.end():])) < 600:
    raise SystemExit('Summary is incomplete (fewer than 600 words); progress left unchecked.')
if re.search(r'^\s*```\s*(?:\{)?mermaid\b', text, re.M | re.I):
    raise SystemExit('Use standalone SVG images instead of Mermaid.')
image = article.with_name('image.png')
header = image.read_bytes()[:24] if image.is_file() else b''
if len(header) != 24 or header[:8] != b'\x89PNG\r\n\x1a\n' or header[12:16] != b'IHDR':
    raise SystemExit('Missing or invalid PNG hero image; progress left unchecked.')
width, height = struct.unpack('>II', header[16:24])
if min(width, height) < 512:
    raise SystemExit('Hero image must be at least 512px in each dimension.')
provenance = article.with_name('image-source.md')
if not provenance.is_file() or not provenance.read_text().strip():
    raise SystemExit('Missing image-source.md provenance; progress left unchecked.')
PY
./scripts/build_site.sh

# Only mark complete after the content checks AND independent site verification pass.
python3 - "$run_dir/selection.json" <<'PY'
from pathlib import Path
import json
import re
import sys

selected = json.loads(Path(sys.argv[1]).read_text())
route = '/' + Path(selected['destination']).relative_to('content').parent.as_posix() + '/'
index = json.loads(Path('docs/search.json').read_text())
entry = next((entry for entry in index if entry.get('url') == route), None)
if (not entry or entry.get('title') != selected['label']
        or entry.get('author') != selected['author']
        or selected['category'] not in entry.get('categories', [])):
    raise SystemExit('Built summary does not match the selected book and category; progress left unchecked.')
path = Path('progress.md')
text = path.read_text()
line = selected['progress_line']
lines = text.splitlines(keepends=True)
matches = [i for i, value in enumerate(lines) if value.rstrip('\r\n') == line]
if len(matches) != 1:
    raise SystemExit('Selected progress entry changed during the run; review manually. Summary files are preserved.')
i = matches[0]
ending = '\r\n' if lines[i].endswith('\r\n') else '\n'
lines[i] = f'- [x] [{selected["label"]}]({selected["destination"]}){ending}'
text = ''.join(lines)
complete = len(re.findall(r'^- \[[xX]\] ', text, re.M))
remaining = len(re.findall(r'^- \[ \] ', text, re.M))
text = re.sub(r'(Total books summarized:\s*\*\*)\d+(\*\*)', lambda m: f'{m[1]}{complete}{m[2]}', text)
text = re.sub(r'(Books planned:\s*\*\*)\d+(\*\*)', lambda m: f'{m[1]}{remaining}{m[2]}', text)
text = re.sub(r'(Total tracked:\s*\*\*)\d+(\*\*)', lambda m: f'{m[1]}{complete + remaining}{m[2]}', text)
text = re.sub(r'^## Books to Summarize \(\d+\)', f'## Books to Summarize ({remaining})', text, flags=re.M)
path.write_text(text)
print(f'Completed: {selected["label"]}\nSummary: {selected["destination"]}\nRemaining books: {remaining}')
PY

# Publish only after successful writing, validation, and progress tracking.
printf 'Publishing completed summary with render_publish.sh...\n'
./render_publish.sh
