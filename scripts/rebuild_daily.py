#!/usr/bin/env python3
"""Rebuild index.html from today's AI HOT daily + NewMobileLife listings.

Used by .github/workflows/daily.yml so GitHub Pages (main) updates without
Windows Task Scheduler or an unmerged Cursor PR.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html import escape, unescape
from html.parser import HTMLParser
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
    "今日要聞": 7,
}
NML_LISTS = [
    "https://www.newmobilelife.com/category/featured/",
    "https://www.newmobilelife.com/category/featured/page/2/",
    "https://www.newmobilelife.com/category/apps-%e6%83%85%e5%a0%b1/%e9%99%90%e6%99%82%e5%85%8d%e8%b2%bb%e6%83%85%e5%a0%b1/",
    "https://www.newmobilelife.com/category/apps-%e6%83%85%e5%a0%b1/%e9%99%90%e6%99%82%e5%85%8d%e8%b2%bb%e6%83%85%e5%a0%b1/page/2/",
]
WIRE_LABEL = "今日要聞"
WIRE_MAX = 24
WIRE_HOURS = 36
WIRE_SKIP_TITLE = re.compile(r"招聘啟事|誠聘以下|廣告主|sponsored", re.I)
WIRE_FEEDS = [
    ("Google 新聞 香港", "https://news.google.com/rss?hl=zh-Hant&gl=HK&ceid=HK:zh-Hant"),
    ("Google 新聞 台灣", "https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant"),
    ("Google 新聞 國際", "https://news.google.com/rss/headlines/section/topic/WORLD?hl=zh-Hant&gl=HK&ceid=HK:zh-Hant"),
    ("BBC 中文", "https://feeds.bbci.co.uk/zhongwen/trad/rss.xml"),
    ("RTHK 本地", "https://rthk.hk/rthk/news/rss/c_expressnews_clocal.xml"),
    ("RTHK 國際", "https://rthk.hk/rthk/news/rss/c_expressnews_cinternational.xml"),
    ("Yahoo 新聞", "https://hk.news.yahoo.com/rss"),
    ("德國之聲", "https://rss.dw.com/rdf/rss-chi-all"),
    ("新浪國際", "https://rss.sina.com.cn/news/world/focus15.xml"),
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
{body}
<p><a href="{url}" target="_blank" rel="noopener noreferrer">查看原文 ↗</a></p>
</body>
</html>
"""
VOID_TAGS = {"br", "img", "hr"}
SKIP_TAGS = {"script", "style", "noscript", "iframe", "svg", "form", "button", "nav", "aside"}
KEEP_TAGS = {
    "p", "h2", "h3", "h4", "ul", "ol", "li", "blockquote", "pre", "code",
    "strong", "em", "b", "i", "br", "img", "a",
}
DROP_CLASS = ("featured-posts", "related-posts", "sharedaddy", "jp-relatedposts", "cs-custom-content")
STUB_MARKERS = ("無法擷取全文", "未提供本地譯文", "已略去翻譯步驟")
MIN_BODY_CHARS = 80


def fetch(url: str, timeout: int = 45) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "zh-TW,zh;q=0.9"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", unescape(s)).strip()


def inner_html_by_class(html: str, class_token: str) -> str:
    rx = re.compile(
        r"<([a-zA-Z0-9]+)([^>]*\bclass=(['\"])[^'\"]*\b"
        + re.escape(class_token)
        + r"\b[^'\"]*\3[^>]*)>",
        re.I,
    )
    m = rx.search(html)
    if not m:
        return ""
    tag = m.group(1).lower()
    start = m.end()
    depth = 1
    i = start
    open_rx = re.compile(rf"<{tag}\b", re.I)
    close_rx = re.compile(rf"</{tag}\s*>", re.I)
    while i < len(html) and depth:
        om = open_rx.search(html, i)
        cm = close_rx.search(html, i)
        if not cm:
            return html[start:]
        opos = om.start() if om else 10**12
        cpos = cm.start()
        if opos < cpos:
            depth += 1
            i = om.end()
        else:
            depth -= 1
            if depth == 0:
                return html[start:cpos]
            i = cm.end()
    return html[start:]


class BodyCleaner(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip = 0
        self.stack: list[str] = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        ad = dict(attrs)
        cls = ad.get("class", "")
        if self.skip:
            if tag not in VOID_TAGS:
                self.skip += 1
            return
        if tag in SKIP_TAGS or any(tok in cls for tok in DROP_CLASS):
            if tag not in VOID_TAGS:
                self.skip += 1
            return
        mapped = "h3" if tag == "h2" else tag
        if mapped not in KEEP_TAGS and mapped != "h3":
            return
        if mapped == "img":
            src = ad.get("data-lazy-src") or ad.get("data-src") or ad.get("src") or ""
            if not src.startswith("http"):
                return
            alt = escape(ad.get("alt") or "", quote=True)
            self.parts.append(f'<img src="{escape(src, True)}" alt="{alt}">')
            return
        if mapped == "br":
            self.parts.append("<br>")
            return
        if mapped == "a":
            href = ad.get("href") or ""
            if href.startswith("//"):
                href = "https:" + href
            if not href.startswith("http"):
                return
            self.parts.append(
                f'<a href="{escape(href, True)}" target="_blank" rel="noopener noreferrer">'
            )
            self.stack.append("a")
            return
        self.parts.append(f"<{mapped}>")
        self.stack.append(mapped)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if self.skip:
            if tag not in VOID_TAGS:
                self.skip = max(0, self.skip - 1)
            return
        mapped = "h3" if tag == "h2" else tag
        if self.stack and self.stack[-1] == mapped:
            self.stack.pop()
            self.parts.append(f"</{mapped}>")

    def handle_data(self, data):
        if self.skip or not data:
            return
        self.parts.append(escape(data))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def result(self) -> str:
        html = "".join(self.parts)
        html = re.sub(r"<p>\s*</p>", "", html)
        html = re.sub(r">\s+<", "><", html)
        return html.strip()


def sanitize_body(raw: str) -> str:
    c = BodyCleaner()
    try:
        c.feed(raw)
        c.close()
    except Exception:
        return ""
    return c.result()


def normalize_territory(text: str) -> str:
    if not text:
        return text
    for src in ("中國台灣", "中国台湾", "中國香港", "中国香港", "中國澳門", "中国澳门"):
        key = "TW" if src.endswith(("灣", "湾")) else ("HK" if src.endswith("港") else "MO")
        text = text.replace(src, f"\x00{key}\x00")
    text = text.replace("臺灣", "\x00TW\x00").replace("台灣", "\x00TW\x00").replace("台湾", "\x00TW\x00")
    text = text.replace("香港", "\x00HK\x00")
    text = text.replace("澳門", "\x00MO\x00").replace("澳门", "\x00MO\x00")
    return text.replace("\x00TW\x00", "中國台灣").replace("\x00HK\x00", "中國香港").replace("\x00MO\x00", "中國澳門")


def extract_source_html(page: str, url: str) -> str:
    host = urllib.parse.urlparse(url).netloc.lower()
    if "newmobilelife.com" in host:
        inner = inner_html_by_class(page, "entry-content")
        cut = re.search(r'<div[^>]*class="[^"]*related-posts', inner)
        if cut:
            inner = inner[: cut.start()]
        return inner
    if "aihot.virxact.com" in host:
        return inner_html_by_class(page, "m-detail-html") or inner_html_by_class(page, "dt-article")
    return inner_html_by_class(page, "entry-content") or inner_html_by_class(page, "post-content")


def can_extract(url: str) -> bool:
    host = urllib.parse.urlparse(url).netloc.lower()
    return "newmobilelife.com" in host or "aihot.virxact.com" in host


def is_stub(body: str) -> bool:
    if not body:
        return True
    return any(s in body for s in STUB_MARKERS)


def source_notice(source_name: str) -> str:
    name = (source_name or "第三方媒體").replace("<", "")
    return f'<div class="notice">內容機器翻譯自第三方媒體（{name}），僅供參考，以原文為準。</div>'


def fetch_article_body(url: str, source_name: str) -> str:
    try:
        page = fetch(url, timeout=20)
    except Exception as e:
        print("article fetch fail", url, e)
        return ""
    raw = sanitize_body(extract_source_html(page, url))
    raw = normalize_territory(raw)
    if len(strip_tags(raw)) < MIN_BODY_CHARS:
        return ""
    return source_notice(source_name) + raw


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


def _rss_text(block: str, name: str) -> str:
    m = re.search(rf"<{name}(?:\s[^>]*)?>(.*?)</{name}>", block, re.S | re.I)
    if not m:
        return ""
    s = m.group(1).strip()
    cm = re.match(r"<!\[CDATA\[(.*)\]\]>$", s, re.S)
    return unescape(cm.group(1) if cm else s).strip()


def _norm_headline(title: str) -> str:
    title = re.sub(r"\s*[-–—|｜]\s*[^|-–—｜]{1,20}$", "", title)
    title = re.sub(r"[「」『』《》【】()（）\[\]\s\-—:：,，.。!！?？、·]+", "", title)
    return title.lower()


def _headline_grams(title: str) -> set[str]:
    s = _norm_headline(title)
    if len(s) < 2:
        return set(s)
    return {s[i : i + 2] for i in range(len(s) - 1)}


def headlines_similar(a: str, b: str) -> bool:
    ga, gb = _headline_grams(a), _headline_grams(b)
    if not ga or not gb:
        return False
    inter = len(ga & gb)
    if inter >= 4 and inter / len(ga | gb) >= 0.38:
        return True
    sa, sb = _norm_headline(a), _norm_headline(b)
    if len(sa) >= 8 and len(sb) >= 8 and (sa[:8] in sb or sb[:8] in sa):
        return True
    return False


def parse_rss_feed(xml: str, default_source: str) -> list[dict]:
    out = []
    for block in re.findall(r"<item\b[^>]*>(.*?)</item>", xml, re.S | re.I):
        title = _rss_text(block, "title")
        if not title or WIRE_SKIP_TITLE.search(title):
            continue
        src_m = re.search(r"<source[^>]*>(.*?)</source>", block, re.S | re.I)
        source = unescape(re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", src_m.group(1)).strip()) if src_m else default_source
        source = source or default_source
        title_clean = re.sub(r"\s*[-–—]\s*" + re.escape(source) + r"\s*$", "", title).strip() or title
        link = _rss_text(block, "link")
        desc = _rss_text(block, "description")
        pd = _rss_text(block, "pubDate") or _rss_text(block, "dc:date")
        dt = None
        if pd:
            try:
                raw_dt = parsedate_to_datetime(pd)
                if raw_dt.tzinfo is None:
                    raw_dt = raw_dt.replace(tzinfo=TZ)
                dt = raw_dt.astimezone(TZ)
            except Exception:
                try:
                    dt = datetime.fromisoformat(pd.replace("Z", "+00:00")).astimezone(TZ)
                except Exception:
                    dt = None
        desc_html = unescape(desc)
        related = []
        for href, ht, font in re.findall(
            r'<a href="([^"]+)"[^>]*>([^<]+)</a>\s*(?:&nbsp;|\xa0|\s)*<font[^>]*>([^<]+)</font>',
            desc_html,
        ):
            if "查看更多" in ht:
                continue
            related.append(
                {
                    "title": unescape(ht).strip(),
                    "url": href,
                    "source": unescape(font).strip(),
                }
            )
        if not related:
            related = [{"title": title_clean, "url": link, "source": source}]
        sources = list(dict.fromkeys([source] + [r["source"] for r in related if r.get("source")]))
        summary = re.sub(r"\s+", " ", strip_tags(desc_html))[:280]
        if "查看更多頭條" in summary:
            summary = ""
        out.append(
            {
                "title": title_clean,
                "source": source,
                "url": link,
                "summary": summary,
                "dt": dt,
                "related": related,
                "sources": sources,
            }
        )
    return out


def wire_body_html(item: dict) -> str:
    names = item.get("sourceName") or WIRE_LABEL
    parts = [source_notice(names)]
    summary = item.get("summary") or ""
    if summary:
        parts.append(f"<p>{escape(summary)}</p>")
    related = item.get("related") or []
    if related:
        parts.append("<h3>各方報道</h3><ul>")
        seen = set()
        for r in related:
            url = r.get("url") or ""
            src = r.get("source") or ""
            key = url or (src + r.get("title", ""))
            if not src or key in seen:
                continue
            seen.add(key)
            href = escape(url, True) if url.startswith("http") else ""
            label = escape(src)
            tit = escape(r.get("title") or "")
            if href:
                parts.append(f'<li><a href="{href}" target="_blank" rel="noopener noreferrer">{label}</a>：{tit}</li>')
            else:
                parts.append(f"<li>{label}：{tit}</li>")
        parts.append("</ul>")
    return "".join(parts)


def build_wire_items(today: date) -> tuple[list[dict], dict[str, str]]:
    raw: list[dict] = []
    for name, url in WIRE_FEEDS:
        try:
            xml = fetch(url, timeout=20)
            items = parse_rss_feed(xml, name)
            print("wire", name, len(items))
            raw.extend(items)
        except Exception as e:
            print("wire fetch fail", name, e)
    clusters: list[dict] = []
    for it in raw:
        placed = False
        for c in clusters:
            if headlines_similar(it["title"], c["title"]):
                c["members"].append(it)
                for s in it["sources"]:
                    if s and s not in c["sources"]:
                        c["sources"].append(s)
                have = {x.get("url") for x in c["related"]}
                for r in it["related"]:
                    if r.get("url") not in have:
                        c["related"].append(r)
                        have.add(r.get("url"))
                if it.get("summary") and len(it["summary"]) > len(c.get("summary") or ""):
                    c["summary"] = it["summary"]
                placed = True
                break
        if not placed:
            clusters.append(
                {
                    "title": it["title"],
                    "members": [it],
                    "sources": list(it["sources"]),
                    "related": list(it["related"]),
                    "summary": it.get("summary") or "",
                    "dt": it.get("dt"),
                }
            )
    cut = datetime.now(TZ) - timedelta(hours=WIRE_HOURS)
    fresh = []
    for c in clusters:
        dts = [m["dt"] for m in c["members"] if m.get("dt")]
        c["dt"] = max(dts) if dts else None
        if c["dt"] and c["dt"] < cut:
            continue
        if WIRE_SKIP_TITLE.search(c["title"] or ""):
            continue
        fresh.append(c)
    fresh.sort(key=lambda c: (-len(c["sources"]), -(c["dt"].timestamp() if c["dt"] else 0)))
    chosen = fresh[:WIRE_MAX]
    items = []
    bodies: dict[str, str] = {}
    used_ids: set[str] = set()
    for c in chosen:
        sources = [s for s in c["sources"] if s][:8]
        related = c["related"][:10]
        primary = next((r for r in related if (r.get("url") or "").startswith("http")), {})
        url = primary.get("url") or (c["members"][0].get("url") if c["members"] else "")
        if not url:
            continue
        dt = c["dt"] or datetime.now(TZ)
        d = dt.date()
        digest = hashlib.sha1((c["title"] or url).encode("utf-8")).hexdigest()[:12]
        aid = "wire-" + digest
        if aid in used_ids:
            aid = "wire-" + hashlib.sha1((c["title"] + dt.strftime("%H%M")).encode("utf-8")).hexdigest()[:12]
        used_ids.add(aid)
        src_label = " · ".join(sources[:4]) if sources else WIRE_LABEL
        if len(sources) > 4:
            src_label += f" 等{len(sources)}家"
        summary = (c.get("summary") or "").strip()
        if not summary:
            summary = "、".join(sources[:6]) + " 均有報道。"
        kps = []
        for r in related:
            s = (r.get("source") or "").strip()
            if s and s not in kps:
                kps.append(s)
        item = {
            "title": c["title"],
            "summary": summary[:280],
            "sourceName": src_label,
            "sourceUrl": url,
            "img": "",
            "imgKind": "",
            "imgCreator": "",
            "imgLicense": "",
            "imgSource": "",
            "date": zh_date(d),
            "isoDate": d.isoformat(),
            "ci": CI[WIRE_LABEL],
            "kind": "wire",
            "isNew": d == today,
            "_sec_label": WIRE_LABEL,
            "articleId": aid,
            "articleUrl": f"articles/{aid}.html",
            "embedded": summary[:280],
            "keypoints": kps[:8],
            "related": related,
        }
        bodies[aid] = wire_body_html(item)
        item.pop("related", None)
        items.append(item)
    return items, bodies


def notice_html(url: str) -> str:
    safe = url.replace('"', "&quot;")
    return (
        f'<div class="notice">原文頁面無法擷取全文，請<a href="{safe}" '
        'target="_blank" rel="noopener noreferrer">點此查看原文 ↗</a>。</div>'
    )


def write_article(item: dict, body_html: str) -> None:
    p = ROOT / "articles" / f"{item['articleId']}.html"
    title = item["title"].replace("<", "")
    body = body_html or f"<p>{escape(item.get('summary') or item.get('embedded') or '')}</p>"
    p.write_text(
        ARTICLE_TPL.format(title=title, body=body, url=item["sourceUrl"]),
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

    wire_items: list[dict] = []
    wire_bodies: dict[str, str] = {}
    try:
        wire_items, wire_bodies = build_wire_items(today)
    except Exception as e:
        print("wire fail", e)

    deals = next(s for s in data["sections"] if s.get("kind") == "deals")

    keep = {it["sourceUrl"] for it in nml40}
    for items in aihot.values():
        keep.update(it["sourceUrl"] for it in items)
    keep.update(it["sourceUrl"] for it in deals["items"])
    keep.update(it["sourceUrl"] for it in wire_items)

    old = [it for it in (data.get("old") or []) if it.get("kind") != "wire"]
    old_urls = {it.get("sourceUrl") for it in old}
    for sec in data["sections"]:
        if sec.get("kind") in ("deals", "wire"):
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
    if wire_items:
        sections.append({"label": WIRE_LABEL, "items": wire_items, "kind": "wire", "ci": CI[WIRE_LABEL]})
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
    ok = fail = skip = kept = 0
    seen_aids: set[str] = set()
    fill_items = []
    for it in list(flat) + list(old):
        if it.get("kind") == "deals":
            continue
        aid = it.get("articleId")
        if not aid or aid in seen_aids:
            continue
        seen_aids.add(aid)
        fill_items.append(it)
    for it in fill_items:
        aid = it["articleId"]
        if it.get("kind") == "wire":
            body = wire_bodies.get(aid)
            if body:
                articles[aid] = body
                if it in flat:
                    write_article(it, body)
            elif aid not in articles:
                articles[aid] = notice_html(it["sourceUrl"])
            continue
        cur = articles.get(aid, "")
        filled_now = False
        if not is_stub(cur):
            skip += 1
        elif can_extract(it["sourceUrl"]):
            body = fetch_article_body(it["sourceUrl"], it.get("sourceName") or "")
            time.sleep(0.12)
            if body:
                articles[aid] = body
                ok += 1
                filled_now = True
            else:
                articles.setdefault(aid, notice_html(it["sourceUrl"]))
                fail += 1
        else:
            articles.setdefault(aid, notice_html(it["sourceUrl"]))
            kept += 1
        if it in flat or filled_now:
            write_article(it, articles.get(aid, ""))
    aj_path.write_text(
        "window.ARTICLES = " + json.dumps(articles, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )

    print(nml_js)
    print("AIHOT", iso, aihot_n, {k: len(v) for k, v in aihot.items() if v})
    print("flat", len(flat), "old", len(old), "added", added, "wire", len(wire_items))
    print("bodies filled", ok, "fail", fail, "already", skip, "notice", kept)


if __name__ == "__main__":
    main()
