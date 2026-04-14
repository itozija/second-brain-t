#!/usr/bin/env python3
"""
Patches ~/.zeroclaw/config.toml to integrate Second Brain T.

What it does:
  1. Adds python3 to allowed_commands
  2. Adds [agents.SecondBrain] with shell access to the KB
  3. Does NOT touch anything else in your config

Run: python3 zeroclaw_patch.py
"""

import sys
from pathlib import Path

CONFIG = Path.home() / '.zeroclaw' / 'config.toml'
SBT    = Path('/root/.zeroclaw/workspace/second-brain-t')
KB     = Path('/root/.zeroclaw/workspace/knowledge')

SBT_AGENT = '''
[agents.SecondBrain]
provider = "openrouter"
model = "anthropic/claude-3.5-haiku"
system_prompt = """You are a Second Brain assistant with access to a personal knowledge base.

Knowledge base location: /root/.zeroclaw/workspace/second-brain-t/output/

--- COMMANDS YOU CAN USE ---

Search for a keyword:
  grep -ri "keyword" /root/.zeroclaw/workspace/second-brain-t/output/tiers/

Read full inventory (Tier 0):
  cat /root/.zeroclaw/workspace/second-brain-t/output/tiers/index.md

List available topics:
  ls /root/.zeroclaw/workspace/second-brain-t/output/tiers/topic/

Read a topic summary:
  cat /root/.zeroclaw/workspace/second-brain-t/output/tiers/topic/TOPIC_NAME.md

Read the graph report:
  cat /root/.zeroclaw/workspace/second-brain-t/output/graph/report.md

Rebuild the knowledge base:
  python3 /root/.zeroclaw/workspace/second-brain-t/build.py /root/.zeroclaw/workspace/knowledge/ --update

Check last build time:
  cat /root/.zeroclaw/workspace/second-brain-t/output/freshness.json

--- RULES ---
- Always read the relevant files before answering. Never guess.
- If the KB is not built yet, tell the user to run: rebuild
- Be concise. Summarise file contents, don't dump them raw.
"""
agentic = true
allowed_tools = ["shell"]
max_iterations = 10
max_depth = 3
'''


def patch_allowed_commands(content: str) -> str:
    """Add python3 to allowed_commands if not already there."""
    if '"python3"' in content:
        print("  python3 already in allowed_commands — skipping")
        return content

    # Insert after the last item in the list (before closing bracket)
    old = '"date",\n]'
    new = '"date",\n    "python3",\n]'
    if old in content:
        print("  Added python3 to allowed_commands")
        return content.replace(old, new, 1)
    else:
        print("  WARNING: Could not find allowed_commands list — add python3 manually")
        return content


def patch_agent(content: str) -> str:
    """Add SecondBrain agent block if not already there."""
    if '[agents.SecondBrain]' in content:
        print("  [agents.SecondBrain] already exists — skipping")
        return content

    # Insert before [swarms] so it sits with the other agents
    if '[swarms]' in content:
        content = content.replace('[swarms]', SBT_AGENT + '\n[swarms]', 1)
        print("  Added [agents.SecondBrain]")
    else:
        content += SBT_AGENT
        print("  Added [agents.SecondBrain] at end of config")

    return content


def main():
    if not CONFIG.exists():
        print(f"Error: {CONFIG} not found")
        sys.exit(1)

    print(f"Patching {CONFIG} ...")
    content = CONFIG.read_text(encoding='utf-8')

    content = patch_allowed_commands(content)
    content = patch_agent(content)

    CONFIG.write_text(content, encoding='utf-8')
    print("\nDone. Restart ZeroClaw to apply changes:")
    print("  zeroclaw service restart")


if __name__ == '__main__':
    main()
