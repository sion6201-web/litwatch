# Paper Wiki

A living knowledge base built from research papers, maintained by Claude Code.
Based on Andrej Karpathy's [LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

## What this is

You drop papers into `raw/`. Claude reads them, extracts knowledge, and incrementally builds a structured wiki in `wiki/`. The wiki **compounds** — every new paper enriches existing pages, surfaces contradictions, and reveals gaps.

You ask questions. Claude answers using the wiki and files good answers back.
You write your own papers. The wiki gives you fast access to evidence and citations.

## Structure

- `raw/` — Source PDFs. **Read-only**, never modified.
- `wiki/` — Markdown pages, all written by Claude.
  - `index.md` — Catalog of every page.
  - `log.md` — Chronological record of ingest/query/lint actions.
  - `sources/` — One page per paper.
  - `entities/` — Organisms, enzymes, compounds, methods, people, labs.
  - `concepts/` — Mechanisms, pathways, theories, applications.
  - `syntheses/` — Cross-source reviews, comparisons, contradictions, gaps.
- `CLAUDE.md` — The schema. Tells Claude how to maintain everything.
- `prompts/` — Reusable prompt templates for common operations.

## Setup

1. Open this folder in Antigravity (or any Claude Code-compatible editor).
2. Make sure Claude Code is logged in (`/login`).
3. Drop your PDFs into `raw/`.
4. Run `/init` if Claude hasn't already loaded `CLAUDE.md`.
5. Start with: `Let's ingest raw/{filename}.pdf`. Claude will follow the workflow in `CLAUDE.md`.

## For Obsidian users

Open this folder as an Obsidian vault. The wiki uses `[[wikilinks]]` and YAML frontmatter, so:
- Graph view works out of the box.
- Dataview queries work if you install the plugin (e.g., list all enzymes by `type: entity, subtype: enzyme`).
- Backlinks are automatic.

## For lab members

Read `wiki/index.md` to see what's covered. Browse in Obsidian. Ask Claude questions about the wiki content — it will cite both wiki pages and underlying papers.

If you want to add new papers, drop them into `raw/` and ask Claude to ingest. Claude will discuss key takeaways with you before writing anything.

## Version control

This is just a folder of markdown files. Initialize git:

```bash
git init
git add .
git commit -m "Initial wiki setup"
```

Add `raw/` to `.gitignore` if PDFs are too large or you don't want them in version history.
