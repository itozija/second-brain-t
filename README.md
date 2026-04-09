# Second Brain T

Turn any folder into a structured knowledge base — summaries, a visual graph, and a wiki, all linked together.

## About

Second Brain T is a local knowledge base builder. Drop any folder into it — research papers, notes, code, or documents — and it builds you a structured map of everything inside.

It gives you three ways to explore your knowledge:

- A **visual graph** showing how files connect to each other
- A **wiki** you can browse page by page in Obsidian
- **Tiered summaries** optimized for querying with AI

Everything runs on your computer. No cloud, no subscription, no data leaves your machine.

Built for students, researchers, writers, and anyone who works with large amounts of information and wants to understand it faster.

## What it does

Point it at any folder and it gives you:

- **Knowledge graph** — interactive visual map showing how files connect
- **Wiki** — one page per file, organized by topic, with links between related pages
- **Tiered context packs** — compressed summaries optimized for AI consumption
- **Dashboard** — one place to access everything

## Getting Started

### Step 1 — Install Python

Check if you already have it. Open a terminal and type:
```bash
python3 --version
```

If you see a version number — you're good. If not, download Python from [python.org](https://www.python.org/downloads/) and install it.

> **How to open a terminal:**
> - **Mac:** Press `Cmd + Space`, type `Terminal`, press Enter
> - **Windows:** Press `Win + R`, type `cmd`, press Enter

---

### Step 2 — Install PDF support

In your terminal, type:
```bash
pip3 install pdfplumber
```

This lets Second Brain T read PDF files automatically. Only needed once.

---

### Step 3 — Download Second Brain T

```bash
git clone https://github.com/itozija/second-brain-t
cd second-brain-t
```

Or download the ZIP from GitHub and unzip it anywhere on your computer.

---

### Step 4 — Find your folder path

Find the folder you want to analyze. To get its path:
- **Mac:** Right-click the folder → Hold `Option` → Click "Copy as Pathname"
- **Windows:** Hold `Shift` + Right-click the folder → "Copy as path"

---

### Step 5 — Run it

In your terminal, navigate to where you downloaded Second Brain T:
```bash
cd /path/to/second-brain-t
```

Then run:
```bash
python3 build.py /path/to/your/folder
```

Replace `/path/to/your/folder` with the path you copied in Step 4.

---

### Step 6 — Open your knowledge base

When it finishes, open this file in your browser:
```
second-brain-t/output/index.html
```

From there you can access the graph, wiki, and report.

---

### Optional — Browse the wiki in Obsidian

1. Download [Obsidian](https://obsidian.md) (free)
2. Open Obsidian → click **Open folder as vault**
3. Select `second-brain-t/output/wiki`

You'll get an interlinked wiki with a visual graph view.

---

## How to use

```bash
python3 build.py /your/folder
python3 build.py /your/folder --title "My KB"
python3 build.py /your/folder --no-cache   # force full rebuild
```

PDFs are detected and converted automatically — no extra step needed.

## What you get

```
output/
  index.html        ← open this in your browser
  graph/
    graph.html      ← interactive knowledge graph
    report.md       ← hub nodes, strongest connections, gaps
  wiki/             ← open this folder in Obsidian
    index.md        ← map of content
    {topic}/        ← one page per file
  tiers/
    index.md        ← Tier 0: full inventory
    topic/          ← Tier 1: one file per topic group
    entity/         ← Tier 2: deep context per file
```

## How it works

You point Second Brain T at any folder. It does 5 things automatically:

**1. Scans** — reads every file (markdown, code, PDFs)

**2. Extracts** — pulls out keywords, topics, and code structure (functions, imports, classes)

**3. Connects** — finds relationships between files based on shared concepts, imports, and mentions

**4. Clusters** — groups related files into communities automatically

**5. Builds** — generates the wiki, graph, tiers, report, and dashboard — all cross-linked

## How everything connects

```
Your files
    ↓
build.py scans + analyzes
    ↓
┌─────────────────────────────┐
│         index.html          │  ← start here
│         (Dashboard)         │
└──────┬──────────────────────┘
       │
       ├── graph/graph.html    ← visual map
       │     click node → wiki page
       │     click node → deep context
       │
       ├── wiki/               ← browse in Obsidian
       │     each page → view in graph
       │     each page → deep context
       │
       ├── tiers/              ← feed to Claude
       │     index.md          (Tier 0 — what exists)
       │     topic/            (Tier 1 — by theme)
       │     entity/           (Tier 2 — per file)
       │
       └── graph/report.md    ← read before asking Claude
```

## Use cases

**📚 Studying**
Run it on your course readings folder. Before each lecture, ask Claude:
> *"What do I already know about urban governance?"*

Claude reads the tiers — not all 30 papers — and answers in seconds.

**🔬 Research**
Run it on a literature review folder. The graph shows which papers share concepts. The report tells you which paper is most central to the debate.

**💻 Codebase**
Run it on a project you just joined. The graph maps file dependencies. The wiki explains each module. Ask Claude:
> *"How does auth connect to the API layer?"*

**🧠 Personal Notes**
Run it on your notes folder. Discover connections between ideas you wrote months apart. Browse in Obsidian with the graph view.

**💼 Work**
Run it on a project folder with meeting notes, reports, and docs. Ask:
> *"What decisions have we made about X?"*

## Works on

- Research papers (PDFs auto-converted)
- Markdown notes
- Code projects (Python + TypeScript AST parsing)
- Any mix of the above

## Requirements

- Python 3.8+
- `pip3 install pdfplumber` — only if you want PDF support

No other dependencies. Everything runs locally.

## Features

- **AST parsing** — understands actual code structure (imports, functions, classes) for Python and TypeScript/JavaScript
- **SHA256 caching** — skips unchanged files on re-runs, fast incremental updates
- **Community detection** — automatically groups related files into clusters
- **Edge confidence** — tags connections as EXTRACTED (from code), INFERRED (strong semantic), or AMBIGUOUS (weak signal)
- **Obsidian compatible** — wiki opens directly as an Obsidian vault with graph coloring
- **Claude skill** — auto-installs `/sbt` command for querying the KB

## License

MIT
