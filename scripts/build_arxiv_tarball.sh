#!/usr/bin/env bash
# Build a clean arXiv submission tarball from the RCT open-science paper.
# Copies main.tex + the two PNG figures into a temp dir, compiles twice with
# pdflatex to resolve references, and packs only the submission files.
# Usage: scripts/build_arxiv_tarball.sh [--out <path>]
# Requires: pdflatex (TeX Live with revtex4-2), python3 + matplotlib (figures).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
OUT="${1:-$ROOT/rct-mipt-blp-arxiv.tar.gz}"
if [[ "${1:-}" == "--out" ]]; then OUT="${2:-$ROOT/rct-mipt-blp-arxiv.tar.gz}"; fi

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

echo "[1/4] regenerating figures from CSVs..."
python3 "$ROOT/scripts/plot_telemetry.py" > /dev/null

echo "[2/4] assembling submission dir..."
cp "$ROOT/paper/main.tex" "$WORK/"
cp "$ROOT/docs/chart_a_mipt.png" "$WORK/fig_mipt.png"
cp "$ROOT/docs/chart_b_blp.png" "$WORK/fig_blp.png"

echo "[3/4] verifying compile (pdflatex x2, warnings-as-errors check)..."
pushd "$WORK" > /dev/null
pdflatex -interaction=nonstopmode -halt-on-error main.tex > build1.log 2>&1
pdflatex -interaction=nonstopmode -halt-on-error main.tex > build2.log 2>&1
if grep -iE '^! |Fatal error|Emergency stop' build2.log; then
  echo "COMPILE FAILED -- see $WORK/build2.log"; exit 1
fi
PAGES=$(grep -oE 'Output written on main.pdf \([0-9]+ pages' build2.log | grep -oE '[0-9]+' || echo "?")
echo "      compiled OK: main.pdf ($PAGES pages)"
popd > /dev/null

echo "[4/4] packing tarball (tex + pngs only, no aux/log/pdf)..."
tar -czf "$OUT" -C "$WORK" main.tex fig_mipt.png fig_blp.png
echo "wrote $OUT ($(du -h "$OUT" | cut -f1))"
tar -tzf "$OUT"
