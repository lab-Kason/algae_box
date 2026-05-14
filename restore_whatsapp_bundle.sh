#!/usr/bin/env bash
set -euo pipefail

# Reassemble the WhatsApp split archive and extract it.
# Run from the repository root, or pass the folder that contains the parts.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$SCRIPT_DIR"
DRY_RUN=false

find_bundle_dir() {
  local candidate
  for candidate in "${1:-}" "$SCRIPT_DIR/whatsapp_bundle" "$SCRIPT_DIR" "$PWD/whatsapp_bundle" "$PWD"; do
    if [[ -n "$candidate" && -f "$candidate/algae_box_portable.tar.gz.part01" && -f "$candidate/algae_box_portable.tar.gz.part02" ]]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  return 1
}

usage() {
  cat <<'EOF'
Usage: ./restore_whatsapp_bundle.sh [bundle_dir] [--dry-run]

Options:
  bundle_dir  Optional folder containing the .part files.
  --dry-run   Show actions without writing files.
  -h, --help  Show this help.
EOF
}

BUNDLE_HINT=""
if [[ $# -gt 0 && "${1:-}" != --* ]]; then
  BUNDLE_HINT="$1"
  shift
fi

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

if ! BUNDLE_DIR="$(find_bundle_dir "$BUNDLE_HINT")"; then
  echo "Error: could not find the WhatsApp split bundle." >&2
  echo "Looked in:" >&2
  echo "  $SCRIPT_DIR/whatsapp_bundle" >&2
  echo "  $SCRIPT_DIR" >&2
  echo "  $PWD/whatsapp_bundle" >&2
  echo "  $PWD" >&2
  echo "Expected files:" >&2
  echo "  algae_box_portable.tar.gz.part01" >&2
  echo "  algae_box_portable.tar.gz.part02" >&2
  exit 1
fi

PART1="$BUNDLE_DIR/algae_box_portable.tar.gz.part01"
PART2="$BUNDLE_DIR/algae_box_portable.tar.gz.part02"
ARCHIVE="$BUNDLE_DIR/algae_box_portable.tar.gz"

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
