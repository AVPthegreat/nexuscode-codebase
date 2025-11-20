#!/bin/bash
set -euo pipefail

DRY_RUN=true

print_usage() {
  cat <<'EOF'
Usage: cleanup_safe.sh [--apply] [--dry-run]

  --apply     Delete files for real. Without this flag the script only prints actions.
  --dry-run   (default) Show what would be deleted without touching anything.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply)
      DRY_RUN=false
      shift
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --help)
      print_usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      print_usage
      exit 1
      ;;
  esac
done

action() {
  if $DRY_RUN; then
    echo "[dry-run] $*"
  else
    echo "[apply] $*"
    "$@"
  fi
}

delete_paths=(
  "JudgeServer_backup"
  "Judger_backup"
  "OnlineJudge_backup"
  "OnlineJudgeFE_backup"
  "OnlineJudge/venv"
  "OnlineJudge/data"
  "JudgeServer/log"
  "Judger/log"
)

for path in "${delete_paths[@]}"; do
  if [[ -e $path ]]; then
    action rm -rf "$path"
  fi
done

delete_logs() {
  local base="$1"
  if [[ -d $base ]]; then
    action find "$base" -name '*.log' -type f -delete
  fi
}

delete_logs "OnlineJudge/data/log"
delete_logs "OnlineJudge/data/backend/log"
delete_logs "JudgeServer/log"
delete_logs "Judger/log"

delete_pycache() {
  local base="$1"
  if [[ -d $base ]]; then
    action find "$base" -type d -name '__pycache__' -prune -exec rm -rf '{}' +
  fi
}

for component in "JudgeServer" "Judger" "OnlineJudge" "OnlineJudgeFE"; do
  delete_pycache "$component"
done

echo "Cleanup plan complete. Re-run with --apply once you review the items above."