#!/bin/bash
set -euo pipefail

# Only run in remote cloud sessions
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Verify required tools are available
if ! command -v python3 &>/dev/null; then
  echo "ERROR: python3 not found" >&2
  exit 1
fi

if ! command -v git &>/dev/null; then
  echo "ERROR: git not found" >&2
  exit 1
fi

# Install the session-log hook into the user's ~/.claude environment
python3 "${CLAUDE_PROJECT_DIR}/install.py"
