#!/bin/bash
# Second Brain T — ZeroClaw VPS Setup
# Run this once on your VPS to wire Second Brain T into ZeroClaw.
#
# Usage:
#   bash zeroclaw_setup.sh

set -euo pipefail

WORKSPACE="/root/.zeroclaw/workspace"
SBT_DIR="$WORKSPACE/second-brain-t"
KB_DIR="$WORKSPACE/knowledge"

echo ""
echo "=== Second Brain T + ZeroClaw Setup ==="
echo ""

# 1. Install / update Second Brain T
echo "[ 1/4 ] Installing Second Brain T..."
if [ -d "$SBT_DIR/.git" ]; then
    echo "  Already installed — pulling latest..."
    git -C "$SBT_DIR" pull --quiet
else
    git clone https://github.com/itozija/second-brain-t.git "$SBT_DIR" --quiet
    echo "  Cloned to $SBT_DIR"
fi

# 2. Install Python dependencies
echo ""
echo "[ 2/4 ] Installing Python dependencies..."
pip3 install pdfplumber python-docx python-pptx --quiet
echo "  Done"

# 3. Create knowledge folder
echo ""
echo "[ 3/4 ] Creating knowledge folder..."
mkdir -p "$KB_DIR"
echo "  $KB_DIR"
echo "  Drop your files (PDFs, notes, docs) into this folder."

# 4. Patch ZeroClaw config
echo ""
echo "[ 4/4 ] Patching ZeroClaw config..."
python3 "$SBT_DIR/zeroclaw_patch.py"

# Create a handy sbt command
cat > /usr/local/bin/sbt << 'SCRIPT'
#!/bin/bash
# sbt — Second Brain T helper
# Usage:
#   sbt build      — build / rebuild the knowledge base
#   sbt status     — show last build info
#   sbt search X   — search the KB for a keyword

SBT="/root/.zeroclaw/workspace/second-brain-t"
KB="/root/.zeroclaw/workspace/knowledge"

case "${1:-}" in
  build)
    echo "Building knowledge base from $KB ..."
    python3 "$SBT/build.py" "$KB" --update
    ;;
  status)
    if [ -f "$SBT/output/freshness.json" ]; then
        cat "$SBT/output/freshness.json"
    else
        echo "Not built yet. Run: sbt build"
    fi
    ;;
  search)
    if [ -z "${2:-}" ]; then echo "Usage: sbt search <keyword>"; exit 1; fi
    grep -ri "$2" "$SBT/output/tiers/" 2>/dev/null || echo "No results."
    ;;
  *)
    echo "Usage: sbt build | sbt status | sbt search <keyword>"
    ;;
esac
SCRIPT
chmod +x /usr/local/bin/sbt

echo ""
echo "========================================"
echo "  Setup complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo ""
echo "  1. Put your files in:"
echo "       $KB_DIR"
echo ""
echo "  2. Build your knowledge base:"
echo "       sbt build"
echo ""
echo "  3. Restart ZeroClaw to load the new agent:"
echo "       zeroclaw service restart"
echo ""
echo "  4. From Telegram, talk to your bot:"
echo "       'search for climate change'"
echo "       'summarise my knowledge base'"
echo "       'what topics do I have?'"
echo "       'rebuild my knowledge base'"
echo "       '@SecondBrain search for X'"
echo ""
