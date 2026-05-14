#!/usr/bin/env bash
set -euo pipefail

# Reassemble the WhatsApp split archive and extract it.
# Run from the repository root after the parts have been downloaded.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$SCRIPT_DIR"
BUNDLE_DIR="$REPO_ROOT/whatsapp_bundle"
PART1="$BUNDLE_DIR/algae_box_portable.tar.gz.part01"
PART2="$BUNDLE_DIR/algae_box_portable.tar.gz.part02"
ARCHIVE="$BUNDLE_DIR/algae_box_portable.tar.gz"

DRY_RUN=false

usage() {
  cat <<'EOF'
Usage: ./restore_whatsapp_bundle.sh [--dry-run]

Options:
  --dry-run   Show actions without writing files.
  -h, --help  Show this help.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=true
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
  shift
done

if [[ ! -f "$PART1" || ! -f "$PART2" ]]; then
  echo "Error: WhatsApp split parts not found in $BUNDLE_DIR" >&2
  echo "Expected:" >&2
  echo "  $PART1" >&2
  echo "  $PART2" >&2
  exit 1
fi

run() {
  if $DRY_RUN; then
    echo "[dry-run] $*"
  else
    eval "$@"
  fi
}

echo "Bundle directory: $BUNDLE_DIR"
echo "Reassembling archive: $ARCHIVE"
run "cat '$PART1' '$PART2' > '$ARCHIVE'"

echo "Extracting archive into repository root"
run "tar -xzf '$ARCHIVE' -C '$REPO_ROOT'"

echo "Done. Extracted contents now available under:"
echo "- $REPO_ROOT/portable_artifacts"
echo "- $REPO_ROOT/CfdOF"
echo "- other project files contained in the archive"
