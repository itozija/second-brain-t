#!/usr/bin/env python3
"""
Second Brain T — Telegram Bot
Interact with your knowledge base from Telegram.

Setup:
    pip3 install pyTelegramBotAPI

Configure:
    Create a .env file in this folder:
        BOT_TOKEN=your_token_here
        FOLDER_PATH=/path/to/your/folder

Run:
    python3 telegram_bot.py
"""

import os
import json
import subprocess
import sys
from pathlib import Path

try:
    import telebot
except ImportError:
    print("Missing dependency. Run: pip3 install pyTelegramBotAPI")
    sys.exit(1)

# ── Config ────────────────────────────────────────────────────────────────────

BASE_DIR  = Path(__file__).parent
OUT_DIR   = BASE_DIR / 'output'
TIERS_DIR = OUT_DIR / 'tiers'


def load_env():
    """Load variables from .env file into os.environ."""
    env_file = BASE_DIR / '.env'
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())


def get_config():
    load_env()
    token = os.environ.get('BOT_TOKEN')
    folder = os.environ.get('FOLDER_PATH')

    if not token:
        print("Error: BOT_TOKEN not set.")
        print("  Create a .env file with: BOT_TOKEN=your_token")
        sys.exit(1)

    return token, Path(folder) if folder else None


# ── Helpers ───────────────────────────────────────────────────────────────────

MAX_MSG = 4000  # Telegram message limit is 4096


def send_long(bot, chat_id, text: str):
    """Send text, splitting into chunks if it exceeds Telegram's limit."""
    while len(text) > MAX_MSG:
        split_at = text.rfind('\n', 0, MAX_MSG)
        if split_at == -1:
            split_at = MAX_MSG
        bot.send_message(chat_id, text[:split_at])
        text = text[split_at:].lstrip('\n')
    if text.strip():
        bot.send_message(chat_id, text)


def read_file(path: Path) -> str | None:
    if path.exists():
        return path.read_text(encoding='utf-8')
    return None


def kb_ready() -> bool:
    return (TIERS_DIR / 'index.md').exists()


def list_topics() -> list[str]:
    topic_dir = TIERS_DIR / 'topic'
    if not topic_dir.exists():
        return []
    return sorted(p.stem for p in topic_dir.glob('*.md'))


def search_tiers(query: str) -> list[tuple[str, str]]:
    """Search all tier markdown files. Returns (label, matched_line) per file."""
    query_lower = query.lower()
    results = []
    for md_file in TIERS_DIR.rglob('*.md'):
        try:
            text = md_file.read_text(encoding='utf-8')
        except Exception:
            continue
        for line in text.splitlines():
            if query_lower in line.lower():
                label = md_file.stem.replace('-', ' ').title()
                results.append((label, line.strip()))
                break  # one hit per file
    return results[:20]


# ── Bot setup ─────────────────────────────────────────────────────────────────

def make_bot(token: str, folder: Path | None):
    bot = telebot.TeleBot(token)

    HELP_TEXT = (
        "Second Brain T Bot\n\n"
        "Commands:\n"
        "/status   — last build info\n"
        "/build    — rebuild knowledge base\n"
        "/summary  — full inventory (Tier 0)\n"
        "/topics   — list topic groups\n"
        "/topic research  — Tier 1 for a topic\n"
        "/search climate  — keyword search\n"
        "/report   — graph analysis report\n"
        "/help     — show this message"
    )

    # /start
    @bot.message_handler(commands=['start', 'help'])
    def handle_start(msg):
        bot.send_message(msg.chat.id, HELP_TEXT)

    # /status
    @bot.message_handler(commands=['status'])
    def handle_status(msg):
        freshness = OUT_DIR / 'freshness.json'
        if not freshness.exists():
            bot.send_message(msg.chat.id, "No knowledge base found yet.\nRun /build to create one.")
            return

        data = json.loads(freshness.read_text())
        topics = list_topics()
        entity_dir = TIERS_DIR / 'entity'
        entity_count = len(list(entity_dir.glob('*.md'))) if entity_dir.exists() else 0
        compiled_at = data.get('compiled_at', 'unknown')[:19].replace('T', ' ')

        bot.send_message(msg.chat.id,
            f"Knowledge Base Status\n\n"
            f"Last built:  {compiled_at}\n"
            f"Entities:    {data.get('entities', '?')}\n"
            f"Connections: {data.get('edges', '?')}\n"
            f"Topics:      {len(topics)}\n"
            f"Files:       {entity_count}"
        )

    # /build
    @bot.message_handler(commands=['build'])
    def handle_build(msg):
        f = folder or (Path(os.environ.get('FOLDER_PATH', '')) if os.environ.get('FOLDER_PATH') else None)
        if not f or not f.exists():
            bot.send_message(msg.chat.id,
                "FOLDER_PATH not set or doesn't exist.\n"
                "Add it to your .env file:\n  FOLDER_PATH=/your/folder"
            )
            return

        bot.send_message(msg.chat.id, f"Building knowledge base from:\n{f}\n\nThis may take a moment...")

        try:
            result = subprocess.run(
                [sys.executable, str(BASE_DIR / 'build.py'), str(f), '--update'],
                capture_output=True, text=True, timeout=300
            )
            if result.returncode == 0:
                output = result.stdout.strip()[-2000:] if result.stdout else ''
                bot.send_message(msg.chat.id, f"Build complete!\n\n{output}")
            else:
                err = result.stderr.strip()[-2000:] if result.stderr else 'Unknown error'
                bot.send_message(msg.chat.id, f"Build failed:\n\n{err}")
        except subprocess.TimeoutExpired:
            bot.send_message(msg.chat.id, "Build timed out (5 min limit). Try a smaller folder.")
        except Exception as e:
            bot.send_message(msg.chat.id, f"Error: {e}")

    # /summary
    @bot.message_handler(commands=['summary'])
    def handle_summary(msg):
        if not kb_ready():
            bot.send_message(msg.chat.id, "No knowledge base found. Run /build first.")
            return
        text = read_file(TIERS_DIR / 'index.md')
        if text:
            send_long(bot, msg.chat.id, text)
        else:
            bot.send_message(msg.chat.id, "Summary file not found.")

    # /topics
    @bot.message_handler(commands=['topics'])
    def handle_topics(msg):
        if not kb_ready():
            bot.send_message(msg.chat.id, "No knowledge base found. Run /build first.")
            return
        topics = list_topics()
        if not topics:
            bot.send_message(msg.chat.id, "No topics found.")
            return
        lines = ["Available Topics:\n"]
        for t in topics:
            lines.append(f"  /topic {t}")
        bot.send_message(msg.chat.id, '\n'.join(lines))

    # /topic <name>
    @bot.message_handler(commands=['topic'])
    def handle_topic(msg):
        if not kb_ready():
            bot.send_message(msg.chat.id, "No knowledge base found. Run /build first.")
            return

        parts = msg.text.split(maxsplit=1)
        if len(parts) < 2:
            topics = list_topics()
            bot.send_message(msg.chat.id,
                "Usage: /topic <name>\n\nAvailable:\n" + '\n'.join(f"  {t}" for t in topics)
            )
            return

        name = parts[1].strip().lower().replace(' ', '-')
        topic_file = TIERS_DIR / 'topic' / f'{name}.md'

        if not topic_file.exists():
            topics = list_topics()
            matches = [t for t in topics if name in t or t in name]
            if len(matches) == 1:
                topic_file = TIERS_DIR / 'topic' / f'{matches[0]}.md'
            elif len(matches) > 1:
                bot.send_message(msg.chat.id,
                    f"Multiple matches: {', '.join(matches)}\nBe more specific."
                )
                return
            else:
                bot.send_message(msg.chat.id,
                    f"Topic '{name}' not found.\nUse /topics to see all available."
                )
                return

        text = read_file(topic_file)
        if text:
            send_long(bot, msg.chat.id, text)
        else:
            bot.send_message(msg.chat.id, "Topic file is empty.")

    # /search <query>
    @bot.message_handler(commands=['search'])
    def handle_search(msg):
        if not kb_ready():
            bot.send_message(msg.chat.id, "No knowledge base found. Run /build first.")
            return

        parts = msg.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.send_message(msg.chat.id, "Usage: /search <keyword>")
            return

        query = parts[1].strip()
        bot.send_message(msg.chat.id, f"Searching for '{query}'...")

        results = search_tiers(query)
        if not results:
            bot.send_message(msg.chat.id, f"No results found for '{query}'.")
            return

        lines = [f"Results for '{query}' ({len(results)} files found):\n"]
        for label, line in results:
            snippet = line[:120] + ('...' if len(line) > 120 else '')
            lines.append(f"{label}\n  {snippet}\n")

        send_long(bot, msg.chat.id, '\n'.join(lines))

    # /report
    @bot.message_handler(commands=['report'])
    def handle_report(msg):
        report_file = OUT_DIR / 'graph' / 'report.md'
        if not report_file.exists():
            bot.send_message(msg.chat.id, "Report not found. Run /build first.")
            return
        text = read_file(report_file)
        if text:
            send_long(bot, msg.chat.id, text)
        else:
            bot.send_message(msg.chat.id, "Report file is empty.")

    return bot


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    token, folder = get_config()

    if folder:
        print(f"Folder: {folder}")
    else:
        print("Note: FOLDER_PATH not set — /build will be unavailable until you add it to .env")

    print("Bot is running. Press Ctrl+C to stop.")
    bot = make_bot(token, folder)
    bot.infinity_polling()


if __name__ == '__main__':
    main()
