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

try:
    from opencc import OpenCC
    _CC = OpenCC("s2hk")
except Exception:
    _CC = None

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
AIHOT_SHOW = {
    "模型发布/更新": "模型發布/更新",
    "产品发布/更新": "產品發布/更新",
    "行业动态": "行業動態",
    "论文研究": "論文研究",
    "技巧与观点": "技巧與觀點",
}
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
WIRE_MAX = 36
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
SOURCE_ALIAS = {
    "bbc": "BBC 中文",
    "bbc中文": "BBC 中文",
    "hk01.com": "香港01",
    "hk01": "香港01",
    "香港01": "香港01",
    "news.mingpao.com": "明報",
    "mingpao.com": "明報",
    "mingpao": "明報",
    "明報": "明報",
    "udn": "聯合新聞網",
    "udn.com": "聯合新聞網",
    "聯合新聞網": "聯合新聞網",
    "yahoo": "Yahoo 新聞",
    "yahoo新聞": "Yahoo 新聞",
    "yahoo財經": "Yahoo 財經",
    "yahoo股市": "Yahoo 股市",
    "yahoo運動": "Yahoo 運動",
    "hk.news.yahoo.com": "Yahoo 新聞",
    "tw.news.yahoo.com": "Yahoo 新聞",
    "on.cc東網": "東網",
    "on.cc": "東網",
    "東網": "東網",
    "storm.mg": "風傳媒",
    "風傳媒": "風傳媒",
    "rfi": "法廣",
    "hko.gov.hk": "香港天文台",
    "linetoday": "LINE TODAY",
    "etnet經濟通": "經濟通",
    "rti.org.tw": "中央廣播電台",
    "news.cnyes.com": "鉅亨網",
    "cnyes.com": "鉅亨網",
    "singtaousa": "星島",
    "news.ltn.com.tw": "自由時報",
    "ltn.com.tw": "自由時報",
    "自由時報": "自由時報",
    "pchomeonline新聞": "PChome 新聞",
    "now新聞": "Now 新聞",
    "中央社cna": "中央社",
    "cna": "中央社",
    "cna.com.tw": "中央社",
    "thedecoder:ainews(rss)": "The Decoder",
    "rthk": "香港電台",
    "rthk.hk": "香港電台",
    "香港電台": "香港電台",
    "香港電台新聞網": "香港電台",
    "881903.com": "商業電台",
    "香港經濟日報hket": "香港經濟日報",
    "hket.com": "香港經濟日報",
    "hket": "香港經濟日報",
    "明報新聞網": "明報",
    "明報ourlifestyle": "明報",
    "上報upmedia": "上報",
    "dw": "德國之聲",
    "德國之聲": "德國之聲",
    "sina": "新浪",
    "sina.com.cn": "新浪",
    "news.sina.com.cn": "新浪",
    "hket.com": "信報",
    "am730.com.hk": "am730",
    "stheadline.com": "星島頭條",
    "ettoday.net": "ETtoday",
    "chinatimes.com": "中國時報",
    "setn.com": "三立新聞",
    "tvbs.com.tw": "TVBS",
    "theinitium.com": "端傳媒",
    "inmediahk.net": "獨立媒體",
    "news.gov.hk": "香港政府新聞網",
    "zaobao.com": "聯合早報",
    "thenewslens.com": "關鍵評論網",
    "upmedia.mg": "上報",
}
ARTICLE_TPL = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<style>
img,video,figure,table{max-width:100%;}
img,video{height:auto;}
.table-scroll{width:100%;max-width:100%;overflow-x:auto;}
table{width:100%;max-width:100%;border-collapse:collapse;table-layout:fixed;}
th,td{padding:8px 10px;border:1px solid #e2e8f0;word-break:break-word;overflow-wrap:anywhere;vertical-align:top;}
pre{max-width:100%;overflow-x:auto;}
</style>
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
    "table", "thead", "tbody", "tfoot", "tr", "th", "td", "caption",
}
DROP_CLASS = ("featured-posts", "related-posts", "sharedaddy", "jp-relatedposts", "cs-custom-content")
STUB_MARKERS = ("無法擷取全文", "未提供本地譯文", "已略去翻譯步驟")
MIN_BODY_CHARS = 80
SKIP_IMG_HOST = re.compile(
    r"news\.google\.com|gstatic\.com/gnews|google_news|doubleclick|googlesyndication",
    re.I,
)
SKIP_IMG_URL = re.compile(
    r"(?:favicon|1x1|pixel|spacer|sprite|tracking|/logo[-_/]|\.svg(?:\?|$))",
    re.I,
)
OG_IMAGE_RX = [
    re.compile(
        r'<meta[^>]+property=["\']og:image(?::secure_url|:url)?["\'][^>]+content=["\']([^"\']+)',
        re.I,
    ),
    re.compile(
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image(?::secure_url|:url)?["\']',
        re.I,
    ),
    re.compile(
        r'<meta[^>]+name=["\']twitter:image(?::src)?["\'][^>]+content=["\']([^"\']+)',
        re.I,
    ),
    re.compile(r'<link[^>]+rel=["\']image_src["\'][^>]+href=["\']([^"\']+)', re.I),
]
OPENVERSE_TERMS = [
    (re.compile(r"地震|地質災害|海嘯"), "earthquake"),
    (re.compile(r"火山"), "volcano eruption"),
    (re.compile(r"王室|哈里|查理斯|英王"), "british royal family"),
    (re.compile(r"伊朗|霍爾木茲|油價|石油"), "oil tanker gulf"),
    (re.compile(r"台積電|GPU|芯片|晶片|半導體"), "semiconductor chip factory"),
    (re.compile(r"網球|美網"), "tennis match"),
    (re.compile(r"飛機|機場|墜機"), "airplane airport"),
    (re.compile(r"金價|黃金"), "gold bars"),
    (re.compile(r"特朗普|白宮"), "white house"),
    (re.compile(r"烏克蘭|俄羅斯|普亭|基輔"), "ukraine war"),
    (re.compile(r"天文台|天氣|暴雨|颱風|纖月|木星"), "night sky stars"),
    (re.compile(r"警察|車禍|交通|私家車|駕駛"), "city traffic night"),
    (re.compile(r"醫院|工程"), "hospital building"),
]
_IMG_CACHE: dict[str, str] = {}
_PAGE_CACHE: dict[str, dict] = {}
_OV_USED: set[str] = set()


def fetch(url: str, timeout: int = 45) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "identity",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def fetch_prefix(url: str, timeout: int = 8, nbytes: int = 1_800_000) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "identity",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(nbytes).decode("utf-8", "replace")


def abs_img_url(src: str, base: str = "") -> str:
    src = unescape((src or "").strip())
    if src.startswith("//"):
        src = "https:" + src
    if base:
        src = urllib.parse.urljoin(base, src)
    return src


def upgrade_wp_img(url: str) -> str:
    return re.sub(r"-\d{2,4}x\d{2,4}(?=\.(?:jpe?g|png|webp|gif))", "", url or "", flags=re.I)


def is_google_news(url: str) -> bool:
    host = urllib.parse.urlparse(url or "").netloc.lower()
    return "news.google." in host


def is_article_url(url: str) -> bool:
    if not (url or "").startswith("http") or is_google_news(url):
        return False
    path = urllib.parse.urlparse(url).path.rstrip("/")
    if not path or path.lower() in {"/chinese", "/zh", "/zhongwen"}:
        return False
    return True


def looks_like_photo(url: str) -> bool:
    if not (url or "").startswith("http"):
        return False
    if SKIP_IMG_HOST.search(url) or SKIP_IMG_URL.search(url):
        return False
    return True


def parse_og_image(html: str, base: str) -> str:
    for rx in OG_IMAGE_RX:
        m = rx.search(html or "")
        if not m:
            continue
        img = abs_img_url(m.group(1), base)
        if looks_like_photo(img):
            return img
    return ""


def first_img_in_html(html: str, base: str = "") -> str:
    for src in re.findall(r"<img[^>]+(?:src|data-src|data-lazy-src)=['\"]([^'\"]+)", html or "", re.I):
        img = abs_img_url(src, base)
        if looks_like_photo(img):
            return upgrade_wp_img(img)
    return ""


def rss_image(block: str) -> str:
    for rx in (
        r'<media:content[^>]+url=["\']([^"\']+)',
        r'<media:thumbnail[^>]+url=["\']([^"\']+)',
        r'<enclosure[^>]+url=["\']([^"\']+)["\'][^>]*type=["\']image',
        r'<enclosure[^>]+type=["\']image[^>]+url=["\']([^"\']+)',
        r'<img[^>]+src=["\'](https?://[^"\']+)',
    ):
        m = re.search(rx, block or "", re.I)
        if m:
            img = abs_img_url(m.group(1))
            if looks_like_photo(img):
                return img
    return ""


def fetch_og_image(url: str) -> str:
    return fetch_article_bits(url).get("img") or ""


def openverse_query(title: str) -> str:
    t = title or ""
    for rx, q in OPENVERSE_TERMS:
        if rx.search(t):
            return q
    return "world news photograph"


def fetch_openverse(title: str) -> tuple[str, str, str]:
    queries = [openverse_query(title), "hong kong city", "world news"]
    seen_q: set[str] = set()
    for q in queries:
        if q in seen_q:
            continue
        seen_q.add(q)
        data = None
        last_err: Exception | None = None
        for _ in range(2):
            try:
                api = (
                    "https://api.openverse.org/v1/images/"
                    f"?q={urllib.parse.quote(q)}&license_type=commercial&page_size=8"
                )
                req = urllib.request.Request(
                    api,
                    headers={"User-Agent": UA, "Accept": "application/json"},
                )
                with urllib.request.urlopen(req, timeout=10) as r:
                    raw = r.read(400_000).decode("utf-8", "replace")
                if not raw.lstrip().startswith("{"):
                    time.sleep(0.35)
                    continue
                data = json.loads(raw)
                break
            except Exception as e:
                last_err = e
                time.sleep(0.35)
        if data is None:
            print("openverse fail", q, last_err)
            continue
        for hit in data.get("results") or []:
            url = hit.get("url") or hit.get("thumbnail") or ""
            if not looks_like_photo(url) or url in _OV_USED:
                continue
            _OV_USED.add(url)
            creator = (hit.get("creator") or "")[:40]
            lic = (hit.get("license") or "").upper()
            return url, creator, lic
    return "", "", ""


def fill_item_photo(item: dict, extra_urls: list[str] | None = None) -> None:
    if item.get("img") and looks_like_photo(item["img"]):
        item["img"] = upgrade_wp_img(item["img"])
        item["imgKind"] = item.get("imgKind") or "og"
        return
    urls: list[str] = []
    for u in extra_urls or []:
        if u:
            urls.append(u)
    su = item.get("sourceUrl") or ""
    if su:
        urls.append(su)
    seen: set[str] = set()
    for u in urls:
        if u in seen or not is_article_url(u):
            continue
        seen.add(u)
        img = fetch_og_image(u)
        time.sleep(0.08)
        if img:
            item["img"] = img
            item["imgKind"] = "og"
            item["imgSource"] = u
            return
    img, creator, lic = fetch_openverse(item.get("title") or "")
    if img:
        item["img"] = img
        item["imgKind"] = "openverse"
        item["imgCreator"] = creator
        item["imgLicense"] = lic
        item["imgSource"] = "https://openverse.org"


def strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", unescape(s)).strip()


def to_hant(text: str) -> str:
    if not text:
        return text
    if _CC is None:
        return text
    try:
        return _CC.convert(text).replace("羣", "群")
    except Exception:
        return text


def _src_key(name: str) -> str:
    s = (name or "").strip().lower()
    s = re.sub(r"^www\.", "", s)
    return s.replace("：", ":").replace("（", "(").replace("）", ")").replace(" ", "")


def zh_source(name: str) -> str:
    raw = (name or "").strip()
    if not raw:
        return "綜合新聞"
    key = _src_key(to_hant(raw))
    if key in SOURCE_ALIAS:
        return SOURCE_ALIAS[key]
    host = key.split("/")[0]
    if host in SOURCE_ALIAS:
        return SOURCE_ALIAS[host]
    for alias_key, alias_val in SOURCE_ALIAS.items():
        if "." in alias_key and alias_key in key:
            return alias_val
    return to_hant(raw)


def show_label(label: str) -> str:
    lab = (label or "").strip()
    return AIHOT_SHOW.get(lab, to_hant(lab) or "其他")


def hantify_item(it: dict) -> dict:
    if not it:
        return it
    for k in ("title", "summary", "embedded"):
        if it.get(k):
            it[k] = to_hant(it[k])
    if it.get("title"):
        it["title"] = clean_headline(it["title"])
    if it.get("sourceName"):
        it["sourceName"] = zh_source(it["sourceName"])
    if it.get("board"):
        it["board"] = show_label(it["board"])
    if it.get("_sec_label"):
        it["_sec_label"] = show_label(it["_sec_label"])
    kps = it.get("keypoints")
    if isinstance(kps, list):
        it["keypoints"] = [to_hant(x) if isinstance(x, str) else x for x in kps]
    return it


def is_mostly_chinese(text: str) -> bool:
    cjk = sum(1 for ch in text or "" if "\u4e00" <= ch <= "\u9fff")
    return cjk >= 6


def clean_headline(title: str) -> str:
    title = (title or "").strip()
    title = re.sub(
        r"\s*[|｜]\s*(政治|國際焦點|全球|社會萬象|評論|港澳|財經|娛樂|體育|生活|焦點).*$",
        "",
        title,
    )
    title = re.sub(r"\s*[-–—]\s*\d+\s*小時前\s*$", "", title)
    title = re.sub(
        r"\s*[-–—]\s*(?:Yahoo\s*新聞|Yahoo新聞|UDN|聯合新聞網|Storm\.mg|風傳媒|BBC(?:\s*中文)?)\s*$",
        "",
        title,
        flags=re.I,
    )
    title = re.sub(
        r"\s*[-–—]\s*[\w.-]+\.(?:com|net|mg|org|hk|tw)(?:\.\w+)?\s*$",
        "",
        title,
        flags=re.I,
    )
    title = re.sub(
        r"\s*[-–—]\s*[\w.·\u4e00-\u9fff]{1,24}(?:新聞網|電台新聞網)\s*$",
        "",
        title,
    )
    return title.strip("｜|/- ")


def summary_score(text: str) -> int:
    if not text or "查看更多" in text:
        return -1
    return text.count("。") * 80 + text.count("，") * 8 + min(len(text), 280)


def is_dump_summary(text: str) -> bool:
    if not text or summary_score(text) < 20:
        return True
    if re.search(r"Storm\.mg|Yahoo新聞|\bUDN\b|\|\s*(政治|國際|全球|焦點)|查看更多", text):
        return True
    if re.search(r"https?://|\w+\.(?:com|net|mg|org)\b", text, re.I):
        return True
    return False


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
            src = abs_img_url(src)
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
        if mapped in {"th", "td"}:
            bits = []
            for key in ("colspan", "rowspan"):
                val = ad.get(key)
                if val and val.isdigit():
                    bits.append(f'{key}="{val}"')
            attr = (" " + " ".join(bits)) if bits else ""
            self.parts.append(f"<{mapped}{attr}>")
            self.stack.append(mapped)
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


PARA_JUNK = re.compile(
    r"跳過此內容|其他人也在看|你可能也想看|延伸閱讀|熱門點擊|點擊收看|"
    r"登入\s*首頁|首頁\s*新聞|觀看\s*分類|圖像來源|Getty Images|"
    r"^編輯[：:︰]|^記者[：:]",
    re.I,
)


def _cjk_count(text: str) -> int:
    return sum(1 for ch in text or "" if "\u4e00" <= ch <= "\u9fff")


def is_good_para(text: str) -> bool:
    t = (text or "").strip()
    if not t or PARA_JUNK.search(t):
        return False
    return _cjk_count(t) >= 18 and len(t) >= 22


def paras_from_chunk(chunk: str) -> list[str]:
    parts = re.split(r"</p>|<br\s*/?>\s*<br\s*/?>|\n{2,}", chunk or "", flags=re.I)
    out: list[str] = []
    for p in parts:
        t = to_hant(re.sub(r"\s+", " ", strip_tags(p)))
        if is_good_para(t):
            out.append(t)
    return out


def _ld_walk(obj) -> list[dict]:
    found: list[dict] = []
    stack = [obj]
    while stack:
        x = stack.pop()
        if isinstance(x, dict):
            found.append(x)
            stack.extend(x.values())
        elif isinstance(x, list):
            stack.extend(x)
    return found


def extract_paragraphs(html: str, url: str) -> list[str]:
    host = urllib.parse.urlparse(url).netloc.lower()
    inner = ""
    if "rthk.hk" in host:
        inner = inner_html_by_class(html, "itemFullText") or inner_html_by_class(html, "itemBody")
    elif "yahoo." in host:
        inner = inner_html_by_class(html, "caas-body")
    elif "newmobilelife.com" in host or "aihot.virxact.com" in host:
        inner = extract_source_html(html, url)
    paras = paras_from_chunk(inner) if inner else []
    if len(paras) < 2:
        for blob in re.findall(r"<script[^>]*ld\+json[^>]*>(.*?)</script>", html or "", re.S | re.I):
            try:
                obj = json.loads(blob)
            except Exception:
                continue
            for node in _ld_walk(obj):
                body = node.get("articleBody") or ""
                desc = node.get("description") or ""
                if isinstance(body, str) and _cjk_count(body) >= 24:
                    paras = paras_from_chunk(body) or [to_hant(re.sub(r"\s+", " ", body))]
                    break
                if isinstance(desc, str) and is_good_para(desc):
                    paras = [to_hant(re.sub(r"\s+", " ", desc))]
            if len(paras) >= 2:
                break
    if len(paras) < 2:
        m = re.search(
            r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)',
            html or "",
            re.I,
        ) or re.search(
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:description["\']',
            html or "",
            re.I,
        )
        if m:
            desc = to_hant(unescape(m.group(1)))
            if is_good_para(desc):
                paras = [desc]
    if len(paras) < 2:
        extras = []
        for p in re.findall(r"<p\b[^>]*>(.*?)</p>", html or "", re.S | re.I):
            t = to_hant(re.sub(r"\s+", " ", strip_tags(p)))
            if is_good_para(t):
                extras.append(t)
            if len(extras) >= 8:
                break
        if len(extras) > len(paras):
            paras = extras
    return paras[:8]


def make_keypoints(*texts: str) -> list[str]:
    blob = "\n".join(t for t in texts if t)
    sents = re.split(r"(?<=[。！？])\s*", blob)
    out: list[str] = []
    seen: set[str] = set()
    for s in sents:
        s = re.sub(r"\s+", " ", s).strip("　 \n")
        if not s or PARA_JUNK.search(s):
            continue
        if "均有報道" in s or re.search(r"\.(com|net|tw|hk)\b", s, re.I):
            continue
        if s.count("、") >= 3 and "。" not in s:
            continue
        if _cjk_count(s) < 12 or len(s) < 16:
            continue
        if len(s) > 92:
            s = s[:90] + "…"
        key = s[:22]
        if key in seen:
            continue
        seen.add(key)
        out.append(to_hant(s))
        if len(out) >= 6:
            break
    return out


def fetch_article_bits(url: str) -> dict:
    if not is_article_url(url):
        return {"img": "", "paras": []}
    if url in _PAGE_CACHE:
        return _PAGE_CACHE[url]
    bits: dict = {"img": "", "paras": []}
    try:
        html = fetch_prefix(url, timeout=10, nbytes=2_000_000)
        img = parse_og_image(html, url) or first_img_in_html(html, url)
        bits["img"] = img if looks_like_photo(img) else ""
        bits["paras"] = extract_paragraphs(html, url)
    except Exception as e:
        print("article bits fail", url[:80], e)
    _PAGE_CACHE[url] = bits
    _IMG_CACHE[url] = bits["img"]
    return bits


def fill_item_copy(item: dict, extra_urls: list[str] | None = None) -> None:
    urls: list[str] = []
    for u in list(extra_urls or []) + [item.get("sourceUrl") or ""]:
        if u and is_article_url(u) and u not in urls:
            urls.append(u)
    paras: list[str] = []
    for u in urls:
        bits = fetch_article_bits(u)
        time.sleep(0.06)
        if bits.get("paras"):
            paras = bits["paras"]
            break
    if paras:
        item["_paras"] = paras[:8]
        lead = paras[0]
        if len(paras) > 1:
            lead = paras[0] + paras[1]
        cur = item.get("summary") or ""
        if not cur or is_dump_summary(cur) or "均有報道" in cur:
            item["summary"] = to_hant(lead[:420])
        kps = make_keypoints(*paras)
        if kps:
            item["keypoints"] = kps
        return
    cur = item.get("summary") or ""
    if is_dump_summary(cur) or "均有報道" in cur:
        item["keypoints"] = []
        return
    kps = make_keypoints(cur)
    if kps:
        item["keypoints"] = kps
    elif item.get("keypoints") and all(len(k) < 24 and "。" not in k for k in item["keypoints"]):
        item["keypoints"] = []


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
    raw = normalize_territory(to_hant(raw))
    og = parse_og_image(page, url) or first_img_in_html(page, url)
    if og and og not in raw:
        raw = f'<p><img src="{escape(og, True)}" alt=""></p>' + raw
    if len(strip_tags(raw)) < MIN_BODY_CHARS:
        return ""
    return source_notice(zh_source(source_name)) + raw


def zh_date(d: date) -> str:
    return f"{d.month}月{d.day}日 周{WEEK[d.weekday()]}"


def zh_long(d: date, hm: str) -> str:
    return f"{d.year}年{d.month}月{d.day}日 周{WEEK[d.weekday()]} {hm}（北京時間）"


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
            href, title = tm.group(1), to_hant(strip_tags(tm.group(2)))
            src_bits = re.findall(r"<span[^>]*>(.*?)</span>", block, re.S)
            source_name = zh_source(strip_tags(src_bits[-1]) if src_bits else "AIHOT")
            sm = re.search(r'daily-article-summary[^>]*>(.*?)</p>', block, re.S)
            summary = to_hant(strip_tags(sm.group(1))[:400] if sm else "")
            source_url = ("https://aihot.virxact.com" + href) if href.startswith("/") else href
            aid = slug_from_url(source_url)
            show = AIHOT_SHOW.get(lab, to_hant(lab))
            img = rss_image(block) or first_img_in_html(block, "https://aihot.virxact.com")
            out[lab].append(
                {
                    "title": title,
                    "summary": summary,
                    "sourceName": source_name,
                    "sourceUrl": source_url,
                    "img": img,
                    "imgKind": "og" if img else "",
                    "imgCreator": "",
                    "imgLicense": "",
                    "imgSource": source_url if img else "",
                    "ci": CI[lab],
                    "kind": "aihot",
                    "isoDate": iso,
                    "_sec_label": show,
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
        url, title = tm.group(1), to_hant(unescape(tm.group(2)).strip())
        img_m = re.search(r'data-lazy-src="(https://[^"]+)"', block) or re.search(
            r'<noscript>\s*<img[^>]+src="(https://[^"]+)"', block
        )
        img = img_m.group(1) if img_m else ""
        img = upgrade_wp_img(img)
        ex = re.search(r'cs-entry__excerpt[^>]*>(.*?)</div>', block, re.S)
        summary = to_hant(strip_tags(ex.group(1))[:280] if ex else "")
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


def headlines_related(a: str, b: str) -> bool:
    if headlines_similar(a, b):
        return True
    sa, sb = _norm_headline(a), _norm_headline(b)
    if len(sa) < 6 or len(sb) < 6:
        return False
    grams_a = {sa[i : i + 4] for i in range(len(sa) - 3)}
    grams_b = {sb[i : i + 4] for i in range(len(sb) - 3)}
    return len(grams_a & grams_b) >= 3


def parse_rss_feed(xml: str, default_source: str) -> list[dict]:
    out = []
    for block in re.findall(r"<item\b[^>]*>(.*?)</item>", xml, re.S | re.I):
        title = to_hant(_rss_text(block, "title"))
        if not title or WIRE_SKIP_TITLE.search(title) or not is_mostly_chinese(title):
            continue
        src_m = re.search(r"<source[^>]*>(.*?)</source>", block, re.S | re.I)
        source = unescape(re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", src_m.group(1)).strip()) if src_m else default_source
        source = zh_source(source or default_source)
        title_clean = clean_headline(re.sub(r"\s*[-–—]\s*" + re.escape(source) + r"\s*$", "", title).strip() or title)
        if not is_mostly_chinese(title_clean):
            continue
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
            rel_title = clean_headline(to_hant(unescape(ht).strip()))
            if not is_mostly_chinese(rel_title):
                continue
            related.append(
                {
                    "title": rel_title,
                    "url": href,
                    "source": zh_source(unescape(font).strip()),
                }
            )
        if not related:
            related = [{"title": title_clean, "url": link, "source": source}]
        sources = list(dict.fromkeys([source] + [r["source"] for r in related if r.get("source")]))
        summary = to_hant(re.sub(r"\s+", " ", strip_tags(desc_html))[:280])
        if is_dump_summary(summary):
            summary = ""
        img = rss_image(block) or rss_image(desc_html)
        out.append(
            {
                "title": title_clean,
                "source": source,
                "url": link,
                "summary": summary,
                "dt": dt,
                "related": related,
                "sources": sources,
                "img": img,
            }
        )
    return out


def wire_body_html(item: dict) -> str:
    names = item.get("sourceName") or WIRE_LABEL
    parts = [source_notice(names)]
    img = item.get("img") or ""
    if img:
        parts.append(f'<p><img src="{escape(img, True)}" alt=""></p>')
    paras = item.get("_paras") or []
    if paras:
        parts.append("<h3>重點內容</h3>")
        for p in paras[:6]:
            parts.append(f"<p>{escape(p)}</p>")
    else:
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
                if it.get("summary") and not is_dump_summary(it["summary"]) and summary_score(it["summary"]) > summary_score(c.get("summary") or ""):
                    c["summary"] = it["summary"]
                if it.get("img") and not c.get("img"):
                    c["img"] = it["img"]
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
                    "img": it.get("img") or "",
                }
            )
    cut = datetime.now(TZ) - timedelta(hours=WIRE_HOURS)
    fresh = []
    for c in clusters:
        dts = [m["dt"] for m in c["members"] if m.get("dt")]
        c["dt"] = max(dts) if dts else None
        if c["dt"] and c["dt"] < cut:
            continue
        if WIRE_SKIP_TITLE.search(c["title"] or "") or not is_mostly_chinese(c["title"] or ""):
            continue
        fresh.append(c)
    fresh.sort(key=lambda c: (-len(c["sources"]), -(c["dt"].timestamp() if c["dt"] else 0)))
    with_art = [
        c
        for c in fresh
        if any(is_article_url(m.get("url") or "") for m in c["members"])
        or any(is_article_url(r.get("url") or "") for r in c["related"])
    ]
    chosen: list[dict] = []
    seen_c: set[int] = set()

    def _take(pool: list[dict], limit: int) -> None:
        for c in pool:
            k = id(c)
            if k in seen_c:
                continue
            seen_c.add(k)
            chosen.append(c)
            if len(chosen) >= limit:
                return

    _take(fresh, 16)
    _take(with_art, WIRE_MAX)
    _take(fresh, WIRE_MAX)
    chosen = chosen[:WIRE_MAX]
    donors = [it for it in raw if it.get("img") or is_article_url(it.get("url") or "")]
    copy_donors = [it for it in raw if is_article_url(it.get("url") or "")]
    for c in chosen:
        if looks_like_photo(c.get("img") or ""):
            continue
        for it in donors:
            if not headlines_similar(c["title"], it["title"]):
                continue
            if looks_like_photo(it.get("img") or ""):
                c["img"] = it["img"]
                break
            img = fetch_og_image(it.get("url") or "")
            time.sleep(0.08)
            if img:
                c["img"] = img
                if it.get("url") and it["url"] not in {r.get("url") for r in c["related"]}:
                    c["related"].append(
                        {
                            "title": it.get("title") or c["title"],
                            "url": it["url"],
                            "source": it.get("source") or "",
                        }
                    )
                break
    items = []
    bodies: dict[str, str] = {}
    used_ids: set[str] = set()
    for c in chosen:
        sources = [zh_source(s) for s in c["sources"] if s][:8]
        sources = list(dict.fromkeys(sources))
        related = c["related"][:10]
        for r in related:
            r["title"] = clean_headline(to_hant(r.get("title") or ""))
            r["source"] = zh_source(r.get("source") or "")
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
        if is_dump_summary(summary):
            summary = ""
        if not summary:
            summary = "、".join(sources[:6]) + " 均有報道。"
        kps = []
        for r in related:
            s = (r.get("source") or "").strip()
            if s and s not in kps:
                kps.append(s)
        extra = [r.get("url") or "" for r in related]
        extra.extend(m.get("url") or "" for m in c.get("members") or [])
        extra.extend(
            it.get("url") or ""
            for it in copy_donors
            if headlines_related(c["title"], it["title"])
        )
        item = {
            "title": clean_headline(to_hant(c["title"])),
            "summary": to_hant(summary[:280]),
            "sourceName": src_label,
            "sourceUrl": url,
            "img": c.get("img") or "",
            "imgKind": "og" if c.get("img") else "",
            "imgCreator": "",
            "imgLicense": "",
            "imgSource": url if c.get("img") else "",
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
        fill_item_photo(item, extra)
        fill_item_copy(item, extra)
        bodies[aid] = wire_body_html(item)
        item.pop("related", None)
        item.pop("_paras", None)
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
    for items in aihot.values():
        for it in items:
            fill_item_photo(it)
            fill_item_copy(it, [it.get("sourceUrl") or ""])

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
        if not it.get("keypoints"):
            it["keypoints"] = make_keypoints(it.get("summary") or "")
    new_count = sum(1 for it in nml40 if it["isNew"])
    added = sum(1 for it in nml40 if it["sourceUrl"] not in prev_nml_urls)

    wire_items: list[dict] = []
    wire_bodies: dict[str, str] = {}
    try:
        wire_items, wire_bodies = build_wire_items(today)
    except Exception as e:
        print("wire fail", e)

    deals = next(s for s in data["sections"] if s.get("kind") == "deals")
    deals["label"] = to_hant(deals.get("label") or "熱門優惠")
    for it in deals.get("items") or []:
        hantify_item(it)

    keep = {it["sourceUrl"] for it in nml40}
    for items in aihot.values():
        keep.update(it["sourceUrl"] for it in items)
    keep.update(it["sourceUrl"] for it in deals["items"])
    keep.update(it["sourceUrl"] for it in wire_items)

    old = [hantify_item(it) for it in (data.get("old") or []) if it.get("kind") != "wire"]
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
            rec["board"] = show_label(sec.get("label") or it.get("_sec_label") or "其他")
            rec["keypoints"] = it.get("keypoints") or []
            hantify_item(rec)
            old.insert(0, rec)
            old_urls.add(u)

    sections = [{"label": "限時情報王", "items": nml40, "kind": "external", "ci": 5}]
    if wire_items:
        sections.append({"label": WIRE_LABEL, "items": wire_items, "kind": "wire", "ci": CI[WIRE_LABEL]})
    for lab in AIHOT_LABELS:
        if aihot[lab]:
            sections.append(
                {
                    "label": AIHOT_SHOW.get(lab, to_hant(lab)),
                    "items": aihot[lab],
                    "kind": "aihot",
                    "ci": CI[lab],
                }
            )
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
        f"{today.month}月{today.day}日 周{WEEK[today.weekday()]} 08:00（北京時間）"
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
    html2 = re.sub(r"<title>[^<]*</title>", f"<title>AI HOT 日報 · {iso}</title>", html2, count=1)
    html_path.write_text(html2, encoding="utf-8")

    aj_path = ROOT / "articles.js"
    aj = aj_path.read_text(encoding="utf-8")
    am = re.search(r"window\.ARTICLES = (\{.*\});\s*$", aj, re.S)
    articles = json.loads(am.group(1)) if am else {}
    articles = {aid: to_hant(body) if isinstance(body, str) else body for aid, body in articles.items()}
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
            cover = it.get("img") or ""
            if cover and "<img" not in cur:
                cur = f'<p><img src="{escape(cover, True)}" alt=""></p>' + cur
                articles[aid] = cur
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
    print("photos nml", sum(1 for it in nml40 if it.get("img")),
          "wire", sum(1 for it in wire_items if it.get("img")),
          "aihot", sum(1 for v in aihot.values() for it in v if it.get("img")))
    print("keypoints wire", sum(1 for it in wire_items if (it.get("keypoints") or [""])[0:1] and len((it.get("keypoints") or [""])[0]) > 18),
          "/", len(wire_items))
    print("flat", len(flat), "old", len(old), "added", added, "wire", len(wire_items))
    print("bodies filled", ok, "fail", fail, "already", skip, "notice", kept)


if __name__ == "__main__":
    main()
