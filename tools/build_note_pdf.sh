#!/usr/bin/env bash
# Build a notes PDF from Markdown: learning/notes/task3/illustrated-notes.md -> .pdf
#
# Usage: tools/build_note_pdf.sh [slug]
#   slug defaults to task3 (expects learning/notes/<slug>/illustrated-notes.md).
#
# Requires: pandoc + xelatex (TeX Live) + the macOS fonts named below.
# On other platforms swap mainfont / CJKmainfont to a font pair that has
# Chinese glyphs and the circled numbers ①②③ / ≈ used in the notes.
set -euo pipefail

SLUG="${1:-task3}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIR="$ROOT/learning/notes/$SLUG"
SRC="$DIR/illustrated-notes.md"
OUT="$DIR/$SLUG-illustrated-notes.pdf"

[ -f "$SRC" ] || { echo "missing $SRC" >&2; exit 1; }

HEADER="$(mktemp -t note-pdf-header).tex"
trap 'rm -f "$HEADER"' EXIT
cat > "$HEADER" <<'TEX'
\makeatletter\define@key{Gin}{alt}{}\makeatother
\usepackage{caption}
\captionsetup{labelformat=empty,labelsep=none,font={small,it}}
\usepackage{etoolbox}
\apptocmd{\tableofcontents}{\clearpage}{}{}
\AtBeginEnvironment{longtable}{\footnotesize}
TEX

pandoc "$SRC" -o "$OUT" --pdf-engine=xelatex \
  --resource-path="$DIR" --shift-heading-level-by=-1 -H "$HEADER" \
  -V geometry:margin=2.2cm -V fontsize=10pt -V linestretch=1.3 \
  -V mainfont="Arial Unicode MS" \
  -V CJKmainfont="Songti SC" -V CJKsansfont="Heiti SC" \
  -V monofont="Menlo" -V CJKmonofont="Heiti SC" \
  --toc --toc-depth=2

echo "wrote ${OUT#"$ROOT"/}"
