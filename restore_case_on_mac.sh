#!/usr/bin/env bash
set -euo pipefail

# Restore OpenFOAM working folders from tracked portable artifacts.
# Intended to be run from repository root on macOS/Linux.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$SCRIPT_DIR"
ARTIFACTS_DIR="$REPO_ROOT/portable_artifacts"
SRC_CASE="$ARTIFACTS_DIR/CfdOF_case"
SRC_MESH="$ARTIFACTS_DIR/CfdOF_meshCase"
TARGET_ROOT="$REPO_ROOT/CfdOF"
TARGET_CASE="$TARGET_ROOT/case"
TARGET_MESH="$TARGET_ROOT/meshCase"
BACKUP_ROOT="$REPO_ROOT/CfdOF_backup_$(date +%Y%m%d_%H%M%S)"

DRY_RUN=false
NO_BACKUP=false

print_usage() {
  cat <<'EOF'
Usage: ./restore_case_on_mac.sh [--dry-run] [--no-backup]

Options:
  --dry-run    Show actions without modifying files.
  --no-backup  Do not backup existing CfdOF/case and CfdOF/meshCase.
  -h, --help   Show this help.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=true
      ;;
    --no-backup)
      NO_BACKUP=true
      ;;
    -h|--help)
      print_usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      print_usage
      exit 1
      ;;
  esac
  shift
done

if [[ ! -d "$SRC_CASE" || ! -d "$SRC_MESH" ]]; then
  echo "Error: portable artifacts not found." >&2
  echo "Expected:" >&2
  echo "  $SRC_CASE" >&2
  echo "  $SRC_MESH" >&2
  exit 1
fi

run_cmd() {
  if $DRY_RUN; then
    echo "[dry-run] $*"
  else
    eval "$@"
  fi
}

echo "Repository root: $REPO_ROOT"
echo "Artifacts: $ARTIFACTS_DIR"
echo "Target root: $TARGET_ROOT"

run_cmd "mkdir -p '$TARGET_ROOT'"

if [[ -d "$TARGET_CASE" || -d "$TARGET_MESH" ]]; then
  if $NO_BACKUP; then
    echo "Existing CfdOF folders detected; backup disabled by --no-backup"
  else
    echo "Backing up existing CfdOF folders to: $BACKUP_ROOT"
    run_cmd "mkdir -p '$BACKUP_ROOT'"
    [[ -d "$TARGET_CASE" ]] && run_cmd "mv '$TARGET_CASE' '$BACKUP_ROOT/case'"
    [[ -d "$TARGET_MESH" ]] && run_cmd "mv '$TARGET_MESH' '$BACKUP_ROOT/meshCase'"
  fi
fi

if [[ -d "$TARGET_CASE" ]]; then
  echo "Removing existing target case folder: $TARGET_CASE"
  run_cmd "rm -rf '$TARGET_CASE'"
fi
if [[ -d "$TARGET_MESH" ]]; then
  echo "Removing existing target meshCase folder: $TARGET_MESH"
  run_cmd "rm -rf '$TARGET_MESH'"
fi

echo "Restoring case and meshCase..."
run_cmd "cp -R '$SRC_CASE' '$TARGET_CASE'"
run_cmd "cp -R '$SRC_MESH' '$TARGET_MESH'"

# Ensure a .foam opener file exists for ParaView convenience.
if [[ ! -f "$TARGET_CASE/case.foam" ]]; then
  echo "Creating case.foam convenience file"
  run_cmd "touch '$TARGET_CASE/case.foam'"
fi

echo "Restore complete."
echo "- Case: $TARGET_CASE"
echo "- Mesh: $TARGET_MESH"
if ! $NO_BACKUP; then
  echo "- Backup (if created): $BACKUP_ROOT"
fi

echo "Next: run OpenFOAM in Docker, or open $TARGET_CASE/case.foam in ParaView."
