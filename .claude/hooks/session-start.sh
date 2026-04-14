#!/bin/bash
set -euo pipefail

# Only run in Claude Code on the web
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

echo "Installing Second Brain T dependencies..."

pip3 install pdfplumber python-docx python-pptx python-telegram-bot --quiet

echo "Dependencies installed."
