#!/usr/bin/env bash
# Rebuild the published site and push it. Vercel redeploys automatically on push.
#
#   ./publish.sh                 rebuild maps + site, commit, push
#   ./publish.sh "my message"    same, with a custom commit message
set -euo pipefail
cd "$(dirname "$0")"

PY=./.venv/bin/python
[ -x "$PY" ] || PY=python3

echo "▶ rebuilding maps and site"
$PY run_pipeline.py --maps

echo "▶ running QA"
$PY -m pytest tests/ -q

MSG="${1:-Update published maps and data $(date +%Y-%m-%d)}"
git add -A
if git diff --cached --quiet; then
  echo "✓ nothing changed — no deploy needed"
  exit 0
fi
git commit -q -m "$MSG"
git push -q origin main
echo "✓ pushed — Vercel will redeploy automatically"
git log -1 --format='  %h  %s'
