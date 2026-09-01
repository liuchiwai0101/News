#!/usr/bin/env python3
"""Rebuild index.html from today's AI HOT daily + NewMobileLife listings.

Used by .github/workflows/daily.yml so GitHub Pages (main) updates without
Windows Task Scheduler or an unmerged Cursor PR.
"""
from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
TZ = timezone(timedelta(hours=8))
WEEK = "一二三四五六日"
AIHOT_LABELS = [
    "模型发布/更新",
    "产品发布/更新",
    "行业动态",
    "论文研究",
    "技巧与观点",
]
CI = {
    "模型发布/更新": 0,
    "产品发布/更新": 1,
    "行业动态": 2,
    "论文研究": 3,
    "技巧与观点": 4,
    "限時情報王": 5,
    "熱門優惠": 6,
}
NML_LISTS = [
    "https://www.newmobilelife.com/category/featured/",
    "https://www.newmobilelife.com/category/featured/page/2/",
    "https://www.newmobilelife.com/category/apps-%e6%83%85%e5%a0%b1/%e9%99%90%e6%99%82%e5%85%8d%e8%b2%bb%e6%83%85%e5%a0%b1/",
    "https://www.newmobilelife.com/category/apps-%e6%83%85%e5%a0%b1/%e9%99%90%e6%99%82%e5%85%8d%e8%b2%bb%e6%83%85%e5%a0%b1/page/2/",
]
ARTICLE_TPL = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
</head>
<body>
<p><a href="../">← 返回日報</a></p>
<h1>{title}</h1>
<p>{summary}</p>
<p><a href="{url}" target="_blank" rel="noopener noreferrer">查看原文 ↗</a></p>
</body>
</html>
"""


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "zh-TW,zh;q=0.9"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8", "replace")


def strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", unescape(s)).strip()


def zh_date(d: date) -> str:
    return f"{d.month}月{d.day}日 周{WEEK[d.weekday()]}"


def zh_long(d: date, hm: str) -> str:
    return f"{d.year}年{d.month}月{d.day}日 周{WEEK[d.weekday()]} {hm}（北京时间）"


def slug_from_url(url: str) -> str:
    part = urllib.parse.unquote(urllib.parse.urlparse(url).path.rstrip("/").split("/")[-1] or "item")
    part = re.sub(r"[^a-zA-Z0-9\-]+", "-", part).strip("-").lower()
    return (part or "item")[:80]


def parse_aihot(html: str, iso: str) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {k: [] for k in AIHOT_LABELS}
    d = date.fromisoformat(iso)
    for p in re.split(r'<section class="daily-section', html)[1:]:
        lab_m = re.search(r'daily-section-title">([^<]+)', p)
        if not lab_m:
            continue
        lab = lab_m.group(1).strip()
        if lab not in out:
            continue
        for block in re.findall(r'<article class="daily-article[^"]*">(.*?)</article>', p, re.S):
            tm = re.search(r'daily-article-title[^>]*>\s*<a href="([^"]+)">(.*?)</a>', block, re.S)
            if not tm:
                continue
            href, title = tm.group(1), strip_tags(tm.group(2))
            src_bits = re.findall(r"<span[^>]*>(.*?)</span>", block, re.S)
            source_name = strip_tags(src_bits[-1]) if src_bits else "AIHOT"
            sm = re.search(r'daily-article-summary[^>]*>(.*?)</p>', block, re.S)
            summary = strip_tags(sm.group(1))[:400] if sm else ""
            source_url = ("https://aihot.virxact.com" + href) if href.startswith("/") else href
            aid = slug_from_url(source_url)
            out[lab].append(
                {
                    "title": title,
                    "summary": summary,
                    "sourceName": source_name,
                    "sourceUrl": source_url,
                    "img": "",
                    "imgKind": "",
                    "imgCreator": "",
                    "imgLicense": "",
                    "imgSource": "",
                    "ci": CI[lab],
                    "kind": "aihot",
                    "isoDate": iso,
                    "_sec_label": lab,
                    "date": zh_date(d),
                    "articleId": aid,
                    "articleUrl": f"articles/{aid}.html",
                    "embedded": summary,
                }
            )
    return out


def parse_nml(html: str, today: date) -> list[dict]:
    items = []
    for block in re.findall(r"<article\b[^>]*>(.*?)</article>", html, re.S):
        tm = re.search(r'<h2 class="cs-entry__title">\s*<a href="([^"]+)">([^<]+)</a>', block)
        if not tm:
            continue
        url, title = tm.group(1), unescape(tm.group(2)).strip()
        img_m = re.search(r'data-lazy-src="(https://[^"]+)"', block) or re.search(
            r'<noscript>\s*<img[^>]+src="(https://[^"]+)"', block
        )
        img = img_m.group(1) if img_m else ""
        ex = re.search(r'cs-entry__excerpt[^>]*>(.*?)</div>', block, re.S)
        summary = strip_tags(ex.group(1))[:280] if ex else ""
        dm = re.search(r"/(\d{4})/(\d{2})/(\d{2})/", url)
        if dm:
            iso = f"{dm.group(1)}-{dm.group(2)}-{dm.group(3)}"
            d = date.fromisoformat(iso)
        else:
            iso, d = today.isoformat(), today
        aid = slug_from_url(url)
        items.append(
            {
                "title": title,
                "summary": summary,
                "sourceName": "NewMobileLife 流動日報",
                "sourceUrl": url,
                "img": img,
                "imgKind": "og" if img else "",
                "imgCreator": "",
                "imgLicense": "",
                "imgSource": url if img else "",
                "date": zh_date(d),
                "isoDate": iso,
                "ci": 5,
                "kind": "external",
                "isNew": False,
                "_sec_label": "限時情報王",
                "articleId": aid,
                "articleUrl": f"articles/{aid}.html",
                "embedded": summary,
            }
        )
    return items


def notice_html(url: str) -> str:
    safe = url.replace('"', "&quot;")
    return (
        f'<div class="notice">原文頁面無法擷取全文，請<a href="{safe}" '
        'target="_blank" rel="noopener noreferrer">點此查看原文 ↗</a>。</div>'
    )


def write_article(item: dict) -> None:
    p = ROOT / "articles" / f"{item['articleId']}.html"
    if p.exists():
        return
    p.write_text(
        ARTICLE_TPL.format(
            title=item["title"].replace("<", ""),
            summary=item.get("summary") or item.get("embedded") or "",
            url=item["sourceUrl"],
        ),
        encoding="utf-8",
    )


def main() -> None:
    today = datetime.now(TZ).date()
    iso = today.isoformat()
    html_path = ROOT / "index.html"
    html = html_path.read_text(encoding="utf-8")
    m = re.search(r"const DATA = (\{.*?\});\n", html)
    if not m:
        raise SystemExit("const DATA not found in index.html")
    nml_m = re.search(r"const NML = \{total:(\d+), shown:(\d+), newCount:(\d+)\};", html)
    data = json.loads(m.group(1))
    old_total = int(nml_m.group(1)) if nml_m else 0

    prev_nml_urls = {
        it["sourceUrl"]
        for sec in data["sections"]
        if sec.get("kind") == "external"
        for it in sec.get("items", [])
    }

    aihot_html = fetch(f"https://aihot.virxact.com/daily/{iso}")
    aihot = parse_aihot(aihot_html, iso)
    aihot_n = sum(len(v) for v in aihot.values())
    if aihot_n == 0:
        raise SystemExit(f"AI HOT {iso} parsed 0 articles")

    nml_items: list[dict] = []
    for url in NML_LISTS:
        try:
            nml_items.extend(parse_nml(fetch(url), today))
        except Exception as e:
            print("nml fetch fail", url, e)

    uniq, seen = [], set()
    for it in nml_items:
        if it["sourceUrl"] in seen:
            continue
        seen.add(it["sourceUrl"])
        uniq.append(it)
    uniq.sort(key=lambda x: x["isoDate"], reverse=True)
    nml40 = uniq[:40]
    if not nml40:
        raise SystemExit("NML parsed 0 articles")
    for it in nml40:
        it["isNew"] = it["isoDate"] == iso
    new_count = sum(1 for it in nml40 if it["isNew"])
    added = sum(1 for it in nml40 if it["sourceUrl"] not in prev_nml_urls)

    deals = next(s for s in data["sections"] if s.get("kind") == "deals")

    keep = {it["sourceUrl"] for it in nml40}
    for items in aihot.values():
        keep.update(it["sourceUrl"] for it in items)
    keep.update(it["sourceUrl"] for it in deals["items"])

    old = list(data.get("old") or [])
    old_urls = {it.get("sourceUrl") for it in old}
    for sec in data["sections"]:
        if sec.get("kind") == "deals":
            continue
        for it in sec.get("items") or []:
            u = it.get("sourceUrl")
            if not u or u in keep or u in old_urls:
                continue
            rec = {k: it.get(k) for k in (
                "title", "summary", "sourceName", "sourceUrl", "img", "imgKind",
                "imgCreator", "imgLicense", "imgSource", "date", "isoDate",
                "articleId", "articleUrl", "ci", "kind",
            )}
            rec["board"] = sec.get("label") or it.get("_sec_label") or "其他"
            rec["keypoints"] = it.get("keypoints") or []
            old.insert(0, rec)
            old_urls.add(u)

    sections = [{"label": "限時情報王", "items": nml40, "kind": "external", "ci": 5}]
    for lab in AIHOT_LABELS:
        if aihot[lab]:
            sections.append({"label": lab, "items": aihot[lab], "kind": "aihot", "ci": CI[lab]})
    sections.append(deals)

    flat = []
    for sec in sections:
        for it in sec["items"]:
            row = dict(it)
            row["_sec_label"] = sec["label"]
            flat.append(row)

    yday = today - timedelta(days=1)
    data["reportHuman"] = f"{today.year}年{today.month}月{today.day}日 周{WEEK[today.weekday()]}"
    data["windowHuman"] = (
        f"{yday.month}月{yday.day}日 周{WEEK[yday.weekday()]} 08:00 — "
        f"{today.month}月{today.day}日 周{WEEK[today.weekday()]} 08:00（北京时间）"
    )
    data["generatedHuman"] = zh_long(today, "08:00")
    data["updatedHuman"] = zh_long(today, datetime.now(TZ).strftime("%H:%M"))
    data["cardDate"] = zh_date(today)
    data["source"] = "AIHOT"
    data["canonical"] = f"https://aihot.virxact.com/daily/{iso}"
    data["sections"] = sections
    data["flat"] = flat
    data["old"] = old

    nml_js = "const NML = {total:%d, shown:%d, newCount:%d};" % (
        old_total + added, len(nml40), new_count
    )
    html2 = html[: m.start()] + "const DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n" + html[m.end() :]
    html2 = re.sub(r"const NML = [^;]+;", nml_js, html2, count=1)
    html_path.write_text(html2, encoding="utf-8")

    aj_path = ROOT / "articles.js"
    aj = aj_path.read_text(encoding="utf-8")
    am = re.search(r"window\.ARTICLES = (\{.*\});\s*$", aj, re.S)
    articles = json.loads(am.group(1)) if am else {}
    for it in flat:
        if it.get("kind") == "deals":
            continue
        write_article(it)
        articles.setdefault(it["articleId"], notice_html(it["sourceUrl"]))
    aj_path.write_text(
        "window.ARTICLES = " + json.dumps(articles, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )

    print(nml_js)
    print("AIHOT", iso, aihot_n, {k: len(v) for k, v in aihot.items() if v})
    print("flat", len(flat), "old", len(old), "added", added)


if __name__ == "__main__":
    main()
