# Ingest prompt templates

Copy-paste these into Claude Code when you want to perform common operations. They are intentionally short — `CLAUDE.md` does the heavy lifting.

---

## 1. Ingest a single paper (recommended default)

```
Ingest raw/{filename}.pdf following the workflow in CLAUDE.md §4.
Stop at Step 4 (discussion) and wait for me to confirm before writing any wiki pages.
```

---

## 2. Ingest a batch (when you trust the schema and have time)

```
Ingest the next 5 unprocessed PDFs in raw/ following CLAUDE.md §4.
For each: do Steps 1–3, give me a 3-bullet TL;DR, then proceed through Steps 5–9 without waiting for my confirmation.
After all 5 are done, give me a single summary of what was added/updated.
```

> ⚠️ Use sparingly. The interactive flow catches Claude's misreadings of methods/numbers. Batch mode is for when you've ingested 20+ already and trust the pattern.

---

## 3. Query the wiki

```
Using the wiki, answer: {your question}
Cite both the wiki pages you used and the underlying source bibkeys.
If no synthesis page exists for this topic and the answer touches 3+ sources, propose creating one.
```

---

## 4. Build a synthesis page

```
Create a topic-review synthesis page on: {topic}.
Use only sources already in the wiki — list the bibkeys you'll draw from before writing.
Follow the synthesis template in CLAUDE.md §5.
```

---

## 5. Build a comparison page

```
Create a comparison synthesis page comparing: {A} vs {B} vs {C}.
Source it from the wiki. Use a table for properties where applicable.
Follow CLAUDE.md §5 conventions, especially citations.
```

---

## 6. Find a citation for my own writing

```
I'm writing: "{sentence or claim}"
Find the strongest 1–3 wiki pages and underlying sources that support this.
Quote the relevant passages (with page numbers if you can extract them) and give me the bibkey for each.
If the claim is unsupported or contradicted by the wiki, tell me.
```

---

## 7. Lint the wiki

```
Run a lint pass on the wiki per CLAUDE.md §7.
Output a report — don't auto-fix anything.
End with 3–5 suggested questions I might want to investigate next.
```

---

## 8. Resume after a break

```
Read wiki/log.md and give me a 5-bullet summary of what's been done in the last 2 weeks.
What are the 3 most underdeveloped areas of the wiki right now?
```
