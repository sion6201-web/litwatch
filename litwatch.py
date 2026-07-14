#!/usr/bin/env python3
"""
litwatch — 한 번에 PubMed E-utilities + bioRxiv API + Europe PMC를 때려
관심 분야 키워드셋에 대한 신규 문헌을 표로 뽑는다.

출력 컬럼: date / original(원논문 여부) / relevance(직접 관련성) / preprint /
          field / source / journal / title / doi / url / matched_keywords

사용:
  python litwatch.py                 # config.yaml, 최근 since_days일
  python litwatch.py --since 14      # 최근 14일
  python litwatch.py --config x.yaml --out output/
"""
import argparse, csv, datetime as dt, html, json, re, sys, time, urllib.parse
from pathlib import Path

import requests
import yaml

UA = {"User-Agent": "litwatch/1.0 (research literature monitor)"}
TIMEOUT = 40


# ─────────────────────────── helpers ───────────────────────────
def phrase(kw: str) -> str:
    """여러 단어면 따옴표로 감싼다."""
    return f'"{kw}"' if " " in kw.strip() else kw.strip()


def norm_doi(doi):
    if not doi:
        return ""
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", str(doi).strip().lower())


def norm_title(t):
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


def matched_kws(text, keywords):
    t = (text or "").lower()
    return [k for k in keywords if k.lower() in t]


def classify(rec, keywords):
    """relevance 티어 + original 여부."""
    title_hit = matched_kws(rec["title"], keywords)
    abs_hit = matched_kws(rec.get("abstract", ""), keywords)
    allm = sorted(set(title_hit) | set(abs_hit))
    if title_hit:
        rel = "high"
    elif len(abs_hit) >= 2:
        rel = "high"
    elif abs_hit:
        rel = "medium"
    else:
        rel = "low"  # 쿼리엔 걸렸으나 반환 텍스트에 표면적으론 없음
    pts = " ".join(rec.get("pubtypes", [])).lower()
    is_review = any(w in pts for w in ["review", "editorial", "comment", "news", "erratum", "retract"])
    rec["relevance"] = rel
    rec["direct"] = "Y" if rel in ("high",) else ("~" if rel == "medium" else "n")
    rec["original"] = "review/other" if is_review else "original"
    rec["matched"] = ", ".join(allm)
    return rec


# ─────────────────────────── Europe PMC ───────────────────────────
def fetch_europepmc(kw_or, d0, d1, field, cap):
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    q = f"({kw_or}) AND (FIRST_PDATE:[{d0} TO {d1}])"
    out, cursor = [], "*"
    while len(out) < cap:
        params = dict(query=q, format="json", pageSize=100, resultType="core",
                      cursorMark=cursor)
        r = requests.get(url, params=params, headers=UA, timeout=TIMEOUT)
        r.raise_for_status()
        j = r.json()
        for a in j.get("resultList", {}).get("result", []):
            pts = [p for p in (a.get("pubTypeList", {}) or {}).get("pubType", []) if p]
            src = a.get("source", "")
            is_pre = src == "PPR" or any("preprint" in p.lower() for p in pts)
            jt = ((a.get("journalInfo", {}) or {}).get("journal", {}) or {}).get("title", "") \
                or a.get("bookOrReportDetails", {}).get("publisher", "") or ("preprint" if is_pre else "")
            doi = norm_doi(a.get("doi"))
            pmid = a.get("pmid", "")
            link = f"https://doi.org/{doi}" if doi else (
                f"https://europepmc.org/article/{src}/{a.get('id','')}")
            out.append(dict(
                date=a.get("firstPublicationDate", "") or a.get("pubYear", ""),
                title=html.unescape(a.get("title", "") or "").rstrip("."),
                abstract=html.unescape(a.get("abstractText", "") or ""),
                journal=jt, source="EuropePMC", doi=doi, pmid=pmid, url=link,
                preprint="Y" if is_pre else "n", pubtypes=pts, field=field))
        nxt = j.get("nextCursorMark")
        if not nxt or nxt == cursor or not j.get("resultList", {}).get("result"):
            break
        cursor = nxt
        time.sleep(0.34)
    return out


# ─────────────────────────── PubMed E-utilities ───────────────────────────
def fetch_pubmed(kw_or, d0, d1, field, cap, api_key, email):
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    common = {"db": "pubmed", "retmode": "json"}
    if api_key:
        common["api_key"] = api_key
    if email:
        common["email"] = email
    delay = 0.11 if api_key else 0.36
    term = f"({kw_or}) AND ({d0.replace('-','/')}[PDAT] : {d1.replace('-','/')}[PDAT])"
    es = requests.get(f"{base}/esearch.fcgi", headers=UA, timeout=TIMEOUT,
                      params={**common, "term": term, "retmax": cap, "datetype": "pdat"})
    es.raise_for_status()
    ids = es.json().get("esearchresult", {}).get("idlist", [])
    time.sleep(delay)
    out = []
    for i in range(0, len(ids), 100):
        chunk = ids[i:i + 100]
        su = requests.get(f"{base}/esummary.fcgi", headers=UA, timeout=TIMEOUT,
                          params={**common, "id": ",".join(chunk)})
        su.raise_for_status()
        res = su.json().get("result", {})
        for uid in res.get("uids", []):
            a = res.get(uid, {})
            doi = ""
            for aid in a.get("articleids", []):
                if aid.get("idtype") == "doi":
                    doi = norm_doi(aid.get("value"))
            pts = a.get("pubtype", []) or []
            out.append(dict(
                date=a.get("sortpubdate", "")[:10] or a.get("pubdate", ""),
                title=html.unescape(a.get("title", "") or "").rstrip("."),
                abstract="",  # esummary엔 abstract 없음 (제목 기반 relevance)
                journal=a.get("source", ""), source="PubMed", doi=doi, pmid=uid,
                url=f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
                preprint="n", pubtypes=pts, field=field))
        time.sleep(delay)
    return out


# ─────────────────────────── bioRxiv / medRxiv ───────────────────────────
def fetch_biorxiv(servers, keywords, d0, d1, field, cap):
    out = []
    kws = [k.lower() for k in keywords]
    for server in servers:
        cursor, got = 0, 0
        while got < cap:
            u = f"https://api.biorxiv.org/details/{server}/{d0}/{d1}/{cursor}/json"
            try:
                r = requests.get(u, headers=UA, timeout=TIMEOUT)
                r.raise_for_status()
                j = r.json()
            except Exception:
                break
            coll = j.get("collection", [])
            if not coll:
                break
            for a in coll:
                blob = f"{a.get('title','')} {a.get('category','')} {a.get('authors','')}".lower()
                if any(k in blob for k in kws):
                    doi = norm_doi(a.get("doi"))
                    out.append(dict(
                        date=a.get("date", ""),
                        title=html.unescape(a.get("title", "") or "").rstrip("."),
                        abstract=html.unescape(a.get("abstract", "") or ""),  # 보통 비어있음
                        journal=f"{server} (preprint)", source="bioRxiv-API", doi=doi,
                        pmid="", url=f"https://doi.org/{doi}" if doi else "",
                        preprint="Y", pubtypes=["preprint"], field=field))
            got += len(coll)
            total = int(j.get("messages", [{}])[0].get("total", 0) or 0)
            cursor += len(coll)
            if cursor >= total or len(coll) < 100:
                break
            time.sleep(0.3)
    return out


# ─────────────────────────── main ───────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(Path(__file__).parent / "config.yaml"))
    ap.add_argument("--since", type=int, default=None, help="최근 N일 (config 덮어씀)")
    ap.add_argument("--out", default=str(Path(__file__).parent / "output"))
    args = ap.parse_args()

    cfg = yaml.safe_load(open(args.config, encoding="utf-8"))
    since = args.since or cfg.get("since_days", 7)
    today = dt.date.today()
    d0, d1 = (today - dt.timedelta(days=since)).isoformat(), today.isoformat()
    outdir = Path(args.out); outdir.mkdir(parents=True, exist_ok=True)
    srcs = cfg.get("sources", {})

    print(f"[litwatch] {d0} ~ {d1} ({since}d) | fields={len(cfg['fields'])} "
          f"| sources={[k for k,v in srcs.items() if v]}", file=sys.stderr)

    records = []
    for f in cfg["fields"]:
        name, kws = f["name"], f["keywords"]
        kw_or = " OR ".join(phrase(k) for k in kws)
        got = 0
        try:
            if srcs.get("europepmc"):
                r = fetch_europepmc(kw_or, d0, d1, name, cfg["max_per_source"])
                records += r; got += len(r)
        except Exception as e:
            print(f"  ! EuropePMC[{name}] {e}", file=sys.stderr)
        try:
            if srcs.get("pubmed"):
                r = fetch_pubmed(kw_or, d0, d1, name, cfg["max_per_source"],
                                 cfg.get("ncbi_api_key"), cfg.get("ncbi_email"))
                records += r; got += len(r)
        except Exception as e:
            print(f"  ! PubMed[{name}] {e}", file=sys.stderr)
        try:
            if srcs.get("biorxiv"):
                r = fetch_biorxiv(cfg.get("preprint_servers", ["biorxiv"]), kws,
                                  d0, d1, name, cfg["max_per_source"])
                records += r; got += len(r)
        except Exception as e:
            print(f"  ! bioRxiv[{name}] {e}", file=sys.stderr)
        print(f"  · {name}: {got} raw hits", file=sys.stderr)

    # dedup (doi 우선, 없으면 정규화 제목) — abstract 있는 레코드를 우선 보존
    field_kw = {f["name"]: f["keywords"] for f in cfg["fields"]}
    best = {}
    for rec in records:
        key = rec["doi"] or norm_title(rec["title"])
        if not key:
            continue
        cur = best.get(key)
        if cur is None:
            best[key] = rec
        else:
            # 병합: field 합치고, abstract 있는 쪽 선호
            cur["field"] = "; ".join(sorted(set(cur["field"].split("; ")) | {rec["field"]}))
            if not cur.get("abstract") and rec.get("abstract"):
                rec["field"] = cur["field"]
                best[key] = rec

    rows = []
    for rec in best.values():
        kws = []
        for fn in rec["field"].split("; "):
            kws += field_kw.get(fn, [])
        rows.append(classify(rec, sorted(set(kws))))

    rel_rank = {"high": 0, "medium": 1, "low": 2}
    rows.sort(key=lambda r: (rel_rank.get(r["relevance"], 3), r["date"]), reverse=False)
    rows.sort(key=lambda r: r["date"], reverse=True)

    cols = ["date", "original", "relevance", "direct", "preprint", "field",
            "source", "journal", "title", "doi", "url", "matched"]
    stamp = today.isoformat()
    csv_path = outdir / f"litwatch_{stamp}.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    # Markdown (report_min_relevance 이상만 표시; CSV엔 전량 저장됨)
    min_rel = cfg.get("report_min_relevance", "medium")
    thr = rel_rank.get(min_rel, 1)
    shown = [r for r in rows if rel_rank.get(r["relevance"], 3) <= thr]
    md_path = outdir / f"litwatch_{stamp}.md"
    hi = [r for r in rows if r["relevance"] == "high"]
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(f"# litwatch {stamp}  ({d0}~{d1})\n\n")
        fh.write(f"- 전체 {len(rows)}건 · 표시 {len(shown)}건(≥{min_rel}) · "
                 f"high {len(hi)} · preprint {sum(1 for r in rows if r['preprint']=='Y')} · "
                 f"original {sum(1 for r in rows if r['original']=='original')}\n\n")
        fh.write("| date | orig | rel | pre | field | title | source | doi |\n")
        fh.write("|---|---|---|---|---|---|---|---|\n")
        for r in shown:
            t = r["title"][:90].replace("|", "/")
            link = f"[{t}]({r['url']})" if r["url"] else t
            fh.write(f"| {r['date'][:10]} | {'O' if r['original']=='original' else 'r'} "
                     f"| {r['relevance'][:1].upper()} | {'P' if r['preprint']=='Y' else ''} "
                     f"| {r['field'][:24]} | {link} | {r['source']} | {r['doi']} |\n")

    print(f"\n[litwatch] {len(rows)} unique records "
          f"(shown≥{min_rel}={len(shown)}, high={len(hi)}, "
          f"preprint={sum(1 for r in rows if r['preprint']=='Y')})")
    print(f"  CSV: {csv_path}\n  MD : {md_path}")
    # 콘솔 요약 (표시 대상 상위 15)
    print("\n date       orig  rel pre field                     title")
    for r in shown[:15]:
        print(f" {r['date'][:10]:10} {('O' if r['original']=='original' else 'r'):4} "
              f"{r['relevance'][:1].upper():3} {('P' if r['preprint']=='Y' else ' '):3} "
              f"{r['field'][:24]:24} {r['title'][:60]}")


if __name__ == "__main__":
    main()
