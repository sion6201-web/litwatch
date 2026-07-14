# Paper Wiki — Schema for Claude Code

You are the maintainer of a personal research wiki built from ~300 academic papers in chemical/biological engineering. The user is a researcher who reads papers, asks questions, and writes their own work. Your job is to compile and maintain a structured, interlinked knowledge base so that knowledge **compounds** rather than getting re-derived from raw PDFs every session.

> **Read this entire file before doing anything.** It is your operating manual.

---

## 1. Architecture

Three layers, strictly separated:

| Layer | Path | Who owns it |
|---|---|---|
| **Raw sources** | `raw/` | User. Immutable. PDFs only. Never edit. |
| **Wiki** | `wiki/` | You. All markdown pages. You create, edit, refactor. |
| **Schema** | `CLAUDE.md` (this file) | Co-evolved. User and you update together as conventions stabilize. |

**Key principle**: The wiki is a *persistent compounding artifact*. Every ingest, query, and lint pass leaves the wiki richer than before. Never throw away useful synthesis — file it back.

---

## 2. Wiki structure

```
wiki/
├── index.md              # Catalog of every page (you maintain)
├── log.md                # Append-only chronological log (you append)
├── sources/              # 1 page per ingested paper
│   └── {bibkey}.md       # e.g., yoshida2016_pet_degradation.md
├── concepts/             # Mechanisms, pathways, theories, applications
│   └── {slug}.md         # e.g., petase-mechanism.md
├── entities/             # Concrete things: organisms, enzymes, compounds, methods, people, labs
│   └── {slug}.md         # e.g., ideonella-sakaiensis.md
└── syntheses/            # Cross-source pages: reviews, comparisons, contradictions, gaps
    └── {slug}.md         # e.g., enzymatic-pet-degradation-review.md
```

### Page types and what goes where

**Source pages** (`sources/{bibkey}.md`)
One per paper. The summary of *that paper alone*. Never editorialize across papers here — that belongs in syntheses.

**Entity pages** (`entities/{slug}.md`)
Concrete, nameable things the literature talks about:
- `organism` — microbes, strains, cell lines (e.g., *Ideonella sakaiensis* 201-F6)
- `enzyme` — proteins, enzymes (e.g., PETase, MHETase, LCC)
- `compound` — substrates, products, intermediates, materials (e.g., PET, TPA, MHET)
- `method` — experimental/computational techniques (e.g., directed evolution, AlphaFold2, cryo-EM)
- `person` — only researchers who appear repeatedly or whose work is influential. Not every coauthor.
- `lab` — research groups (e.g., "Tournier lab", "Arc Institute")

**Concept pages** (`concepts/{slug}.md`)
Abstract things:
- `mechanism` — how something works at molecular/system level
- `pathway` — metabolic, signaling, or reaction pathways
- `application` — end-use contexts (e.g., PET bioremediation)
- `theory` — frameworks, models, principles

**Synthesis pages** (`syntheses/{slug}.md`)
Multi-source, derivative, the *real value* of the wiki:
- `topic-review` — comprehensive coverage of a topic across many sources
- `comparison` — head-to-head (e.g., "Wild-type PETase vs FAST-PETase vs LCC variants")
- `contradictions` — where sources disagree, with evidence
- `gaps` — identified research gaps and open questions
- `timeline` — chronological evolution

---

## 3. Page conventions (CRITICAL — these are what make the wiki searchable and Obsidian-compatible)

### YAML frontmatter (every page)

```yaml
---
type: source | entity | concept | synthesis
subtype: organism | enzyme | mechanism | topic-review | ...   # for entity/concept/synthesis
title: Human-readable title
created: 2026-05-07
updated: 2026-05-07
sources: [yoshida2016, tournier2020]                          # bibkeys this page draws from
tags: [pet, biodegradation, enzyme]                           # lowercase, hyphenated
status: stub | draft | mature                                 # how complete this page is
confidence: low | medium | high                               # how well-supported the synthesis is
---
```

### Wikilinks (Obsidian-style, NOT markdown links)

- Internal references: `[[ideonella-sakaiensis]]`, `[[petase-mechanism]]`
- With display text: `[[ideonella-sakaiensis|*I. sakaiensis*]]`
- **Always use wikilinks for any wiki-internal reference.** This is what makes Obsidian's graph view light up.

### Citations — the most important convention

Every non-trivial claim cites its source(s). Format:

- `[@bibkey]` — paper-level citation
- `[@bibkey, p.4]` — page-specific
- `[@bibkey, Fig.3]` — figure/table-specific
- `[@yoshida2016; @tournier2020]` — multiple sources

> **Rule**: If you write a claim that came from a paper, cite it. If you cannot cite it, mark the sentence with `[CHECK]` and flag for the user. **Never invent attribution.**

### Bibkey format

`{firstauthor}{year}_{shortslug}` — e.g., `yoshida2016_pet_degradation`, `tournier2020_lcc_engineered`.
Lowercase, ASCII only, underscore-separated.

### Slug format (for filenames)

Lowercase, hyphen-separated, ASCII. `petase-mechanism`, not `PETase Mechanism` or `petase_mechanism`.

---

## 4. Ingest workflow — when the user adds a new paper

This is the most important workflow. Follow it strictly. Default to **one paper at a time** with the user in the loop.

### Step 1: Pre-flight
- Confirm the file path (e.g., `raw/yoshida2016.pdf`).
- Check `wiki/index.md` and `wiki/sources/` to see if it's already ingested. If yes, ask the user whether they want to refresh or skip.

### Step 2: Read the paper
- Read the full PDF using your file-reading capability.
- If the PDF has critical figures/schemes you cannot interpret from text alone, tell the user which page numbers contain figures worth looking at.

### Step 3: Extract metadata
Pull from the paper:
- Authors, year, journal, DOI, title
- Construct a bibkey
- Identify paper type: `original-research | review | perspective | methods | preprint`

### Step 4: Discuss with the user (DO NOT skip this)
Before writing anything, present:
- 3–5 bullet key takeaways in your own words
- Methods/system the paper uses (organism? enzyme? assay?)
- The most novel claim
- Any obvious connection to existing wiki pages (search `index.md` first)

Wait for the user to respond. They may correct your reading or flag what to emphasize. **Do not write any wiki page until they confirm.**

### Step 5: Create the source page
At `wiki/sources/{bibkey}.md`. Template:

```markdown
---
type: source
title: {paper title}
created: {today}
updated: {today}
authors: [...]
year: 2023
journal: ...
doi: ...
bibkey: {bibkey}
paper_type: original-research
tags: [...]
---

# {Title}

**Authors**: ...
**Citation**: [@{bibkey}]

## TL;DR
2–3 sentences in your own words.

## Key claims
- Claim 1 [p.X]
- Claim 2 [p.Y]
- ...

## Methods
- Organism/system: [[entity-link]]
- Key techniques: [[entity-link]]
- Key conditions: ... (temp, pH, substrate concentration, etc.)

## Key results
Specific numbers. Yields, rates, k_cat, K_m, conversion %, etc. Numbers matter — copy them carefully.

## Connections
- Builds on: [@earlier_paper] — how
- Contradicts: [@other_paper] — how (also flag for syntheses/contradictions update)
- Related concepts: [[concept-slug]]

## Open questions / Limitations
What the authors acknowledge or what is left unanswered.

## Notes
Anything else the user flagged as important.
```

### Step 6: Update entity and concept pages
For each entity/concept the paper touches:
- **Already exists?** Open the page, add a new bullet under "Findings from sources" or update the relevant section. Cite the new source. If new data contradicts existing claims, flag it.
- **Doesn't exist?** Create it. Use the entity/concept template (see §5).

A single ingest may touch 5–15 wiki pages. That's normal.

### Step 7: Update `index.md`
Add the new source under `## Sources`. Add any new entity/concept/synthesis pages under their respective sections.

### Step 8: Append to `log.md`
```markdown
## [2026-05-07] ingest | yoshida2016_pet_degradation
Added source page. Created entities: [[ideonella-sakaiensis]], [[petase]], [[mhetase]]. Updated concept: [[pet-biodegradation]]. Flagged potential contradiction with [@palm2019] re: optimal temperature.
```

### Step 9: Flag contradictions and gaps
If during ingest you found:
- A contradiction with an existing page → add an entry to `syntheses/contradictions.md` (create if absent) and tell the user.
- A noticeable gap (e.g., "no source has reported activity at neutral pH") → add to `syntheses/gaps.md`.

---

## 5. Entity / concept / synthesis page templates

### Entity page

```markdown
---
type: entity
subtype: enzyme   # or organism, compound, method, person, lab
title: PETase
created: ...
updated: ...
sources: [yoshida2016, austin2018, tournier2020]
tags: [enzyme, pet, hydrolase]
status: draft
---

# PETase

**Type**: Cutinase-like serine hydrolase
**First reported**: [@yoshida2016]
**Aliases**: IsPETase, PET hydrolase

## What it is
1–2 paragraph overview. Cited.

## Key properties
- Optimal temperature: 30°C [@yoshida2016] — though [@son2019] reports activity up to 40°C with engineered variants
- Optimal pH: ...
- Substrate specificity: ...
- Catalytic triad: Ser160-His237-Asp206 [@austin2018]

## Variants and engineering
- FAST-PETase [@lu2022]
- HotPETase [@bell2022]
- ...

## Findings across sources
- [@yoshida2016]: discovery in *I. sakaiensis*, characterization
- [@austin2018]: crystal structure and mechanism
- [@tournier2020]: comparative kinetics with LCC

## Related
- Organism: [[ideonella-sakaiensis]]
- Substrate: [[pet-polymer]]
- Product: [[mhet]]
- Pairs with: [[mhetase]]
- Mechanism: [[petase-mechanism]]
```

### Synthesis page

```markdown
---
type: synthesis
subtype: topic-review
title: Enzymatic PET degradation — state of the field
created: ...
updated: ...
sources: [yoshida2016, austin2018, tournier2020, lu2022, bell2022, ...]
tags: [pet, biodegradation, enzyme-engineering]
status: draft
confidence: medium
---

# Enzymatic PET degradation — state of the field

## Summary
3–5 sentences synthesizing the current understanding across all sources.

## Timeline
- 2016: Discovery of [[ideonella-sakaiensis]] and [[petase]] [@yoshida2016]
- 2018: Crystal structure resolved [@austin2018]
- ...

## Consensus claims
Things multiple independent sources agree on. Each with citations.

## Open disputes
- **Optimal temperature for industrial use**: [@x] argues 50°C; [@y] argues 70°C with thermostable variants. See [[contradictions]].

## Identified gaps
- No source has tested ... at scale
- Mechanism of ... remains unclear

## See also
- [[entity-link]], [[concept-link]]
```

---

## 6. Query workflow — when the user asks a question

1. **Read `wiki/index.md` first** to find candidate pages.
2. Read those pages. Follow wikilinks as needed.
3. If the wiki has the answer: respond with citations to wiki pages AND the underlying source bibkeys. Format like: "According to [[petase-mechanism]] (drawn from [@austin2018, p.6]), ..."
4. If the wiki *doesn't* have the answer but a raw source might: tell the user, optionally read the source, and then **file the new finding back into the wiki** so the next query benefits.
5. If the answer requires synthesis across multiple sources and no synthesis page exists yet: offer to create one. This is a high-value moment.

> **Filing answers back is non-negotiable.** A good answer that disappears into chat history is wasted work.

---

## 7. Lint workflow — periodic health checks

When the user says "lint the wiki" (or weekly, whichever):

1. **Orphan pages**: pages with no inbound wikilinks. Either link them in or merge.
2. **Stub pages**: pages marked `status: stub` for >2 weeks. Either complete or delete.
3. **Stale claims**: pages where new sources have appeared but the synthesis hasn't been updated. Look at `updated:` dates vs. source ingest dates.
4. **Contradictions not surfaced**: scan for sources making opposing claims that aren't in `syntheses/contradictions.md`.
5. **Missing entity pages**: bibkeys mentioned in source pages but no entity page exists for prominent organisms/enzymes/methods.
6. **Citation gaps**: claims without `[@bibkey]` attribution. Either find the source or mark `[CHECK]`.
7. **Suggested questions**: based on the gaps, propose 3–5 questions the user might want to investigate next.

Output the lint report to chat. Don't auto-fix without confirmation.

---

## 8. Conventions and tone

- **Numbers and units matter.** Always preserve them: "k_cat = 12.4 ± 0.8 s⁻¹" not "high k_cat".
- **Hedging is fine.** "*Suggests*", "*reports*", "*claims*" are better than "*proves*" or "*shows*" unless the source itself is that strong.
- **Use English for filenames and structural markdown.** Page bodies can be Korean if the user prefers — ask once, then stay consistent.
- **Don't editorialize on source pages.** Editorial synthesis goes only in `syntheses/`.
- **Preserve uncertainty.** When sources disagree, present both with citations. Don't pick a winner unless the user explicitly asks for your judgment.

---

## 9. What you do NOT do

- ❌ Modify `raw/` PDFs.
- ❌ Invent citations or page numbers.
- ❌ Bulk-ingest 50 papers without user check-ins.
- ❌ Delete a wiki page without the user's confirmation.
- ❌ Use markdown links `[text](path.md)` when wikilinks `[[slug]]` are appropriate.
- ❌ Write synthesis claims on a source page (that's what `syntheses/` is for).

---

## 10. First-time setup checklist

When this wiki is freshly initialized and `raw/` has PDFs but `wiki/` is empty:

1. List PDFs in `raw/`. Report the count.
2. Confirm with the user: "Shall we ingest one paper as a test run, or do you want me to first set up empty `index.md` and `log.md` skeletons?"
3. Don't try to ingest all at once. Suggest a pace (e.g., 5–10 per session) and let the user drive.

---

*End of schema. Update this file as conventions evolve.*
