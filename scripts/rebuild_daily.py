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
    "APP 優惠": 8,
    "PCM": 9,
    "本地新聞": 10,
}
NML_LISTS = [
    "https://www.newmobilelife.com/category/featured/",
    "https://www.newmobilelife.com/category/featured/page/2/",
    "https://www.newmobilelife.com/category/apps-%e6%83%85%e5%a0%b1/%e9%99%90%e6%99%82%e5%85%8d%e8%b2%bb%e6%83%85%e5%a0%b1/",
    "https://www.newmobilelife.com/category/apps-%e6%83%85%e5%a0%b1/%e9%99%90%e6%99%82%e5%85%8d%e8%b2%bb%e6%83%85%e5%a0%b1/page/2/",
]
WIRE_LABEL = "今日要聞"
APP_LABEL = "APP 優惠"
APP_MAX = 40
APP_PROMO = re.compile(
    r"限時免費|限時免费|《[^》]{1,48}》.*(?:免費|免费|兌換碼|兑换码)|【\s*PC\s*】",
    re.I,
)
PCM_LABEL = "PCM"
PCM_MAX = 40
PCM_FEEDS = [
    "https://www.pcmarket.com.hk/feed/",
    "https://www.pcmarket.com.hk/feed/?paged=2",
    "https://www.pcmarket.com.hk/category/tech/feed/",
    "https://www.pcmarket.com.hk/category/buyer-guide/feed/",
    "https://www.pcmarket.com.hk/category/artificial-intelligence/feed/",
    "https://www.pcmarket.com.hk/category/biz-it/feed/",
    "https://www.pcmarket.com.hk/category/how-to/feed/",
    "https://www.pcmarket.com.hk/category/reviews/feed/",
]
LOCAL_FEEDS = [
    ("RTHK 本地", "https://rthk.hk/rthk/news/rss/c_expressnews_clocal.xml"),
    ("Yahoo 港聞", "https://hk.news.yahoo.com/rss/hong-kong"),
    ("星島頭條", "https://www.stheadline.com/rss"),
    ("東網", "https://orientaldaily.on.cc/rss/news.xml"),
    ("巴士的報", "https://www.bastillepost.com/hongkong/feed"),
    ("政府新聞公報", "https://www.info.gov.hk/gia/rss/general_zh.xml"),
    ("法庭線", "https://thewitnesshk.com/feed/"),
    ("Google 港聞", "https://news.google.com/rss/headlines/section/topic/NATION?hl=zh-Hant&gl=HK&ceid=HK:zh-Hant"),
    (
        "Google 港媒",
        "https://news.google.com/rss/search?q=site:hk01.com+OR+site:mingpao.com+OR+site:on.cc"
        "+OR+site:rthk.hk+OR+site:stheadline.com+OR+site:am730.com.hk+OR+site:hket.com"
        "+OR+site:bastillepost.com+OR+site:881903.com+when:1d&hl=zh-Hant&gl=HK&ceid=HK:zh-Hant",
    ),
]
WIRE_MAX = 48
WIRE_HOURS = 36
WIRE_SKIP_TITLE = re.compile(r"招聘啟事|誠聘以下|廣告主|sponsored", re.I)
PCM_FOOTER = re.compile(r"這篇文章\s*.*?最早出現於\s*.*?。?\s*$", re.S)
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
AI_INDUSTRY_MAX = 18
AI_INDUSTRY_HOURS = 72
AI_INDUSTRY_RX = re.compile(
    r"人工智能|人工智慧|生成式|大模型|大語言模型|語言模型|智能體|具身|"
    r"OpenAI|ChatGPT|Claude|Gemini|Anthropic|DeepSeek|深度求索|"
    r"英偉達|英伟达|輝達|NVIDIA|算力|Sora|Copilot|通義|文心|豆包|Kimi|"
    r"智譜|MiniMax|Grok|Perplexity|(?<![A-Za-z])AI(?![A-Za-z])",
    re.I,
)
AI_INDUSTRY_FEEDS = [
    (
        "Google AI",
        "https://news.google.com/rss/search?q="
        "(AI+OR+%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD+OR+%E5%A4%A7%E6%A8%A1%E5%9E%8B"
        "+OR+OpenAI+OR+ChatGPT+OR+DeepSeek)+when:2d"
        "&hl=zh-Hant&gl=HK&ceid=HK:zh-Hant",
    ),
    ("量子位", "https://www.qbitai.com/feed"),
    ("IT之家", "https://www.ithome.com/rss/"),
    ("愛范兒", "https://www.ifanr.com/feed"),
    ("極客公園", "https://www.geekpark.net/rss"),
    ("Solidot", "https://www.solidot.org/index.rss"),
    ("雷峰網", "https://www.leiphone.com/feed"),
    ("鈦媒體", "https://www.tmtpost.com/rss.xml"),
    ("InfoQ", "https://www.infoq.cn/feed"),
    ("cnBeta", "https://www.cnbeta.com.tw/backend.php"),
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
    "pcmarket.com.hk": "PCM",
    "www.pcmarket.com.hk": "PCM",
    "pcm": "PCM",
    "bastillepost.com": "巴士的報",
    "www.bastillepost.com": "巴士的報",
    "巴士的報": "巴士的報",
    "orientaldaily.on.cc": "東網",
    "thewitnesshk.com": "法庭線",
    "info.gov.hk": "政府新聞公報",
    "www.info.gov.hk": "政府新聞公報",
    "政府新聞公報": "政府新聞公報",
    "stheadline.com": "星島頭條",
    "www.stheadline.com": "星島頭條",
}
ARTICLE_TPL = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>__TITLE__</title>
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
<h1>__TITLE__</h1>
__BODY__
<p><a href="__URL__" target="_blank" rel="noopener noreferrer">查看原文 ↗</a></p>
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
DROP_CLASS = (
    "featured-posts",
    "related-posts",
    "sharedaddy",
    "jp-relatedposts",
    "cs-custom-content",
    "td-a-ad",
    "td-adspot-title",
    "code-block",
)
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
_GNEWS_CACHE: dict[str, str] = {}
_OV_USED: set[str] = set()
_GARTURLREQ_CTX = [
    ["X", "X", ["X", "X"], None, None, 1, 1, "US:en", None, 1, None, None, None, None, None, 0, 1],
    "X",
    "X",
    1,
    [1, 1, 1],
    1,
    1,
    None,
    0,
    0,
    None,
    0,
]
ARTICLE_CLASS_TOKENS = [
    "itemFullText",
    "module-article-body",
    "caas-body",
    "article-content",
    "article__content",
    "article-body",
    "article_content",
    "story-body",
    "td-post-content",
    "post-content",
    "entry-content",
    "news-content",
    "longText",
    "artibody",
    "content-body",
    "RichTextArticleBody",
]


def encode_url(url: str) -> str:
    """Percent-encode non-ASCII path/query so urllib can open Chinese URLs."""
    if not url or not url.startswith("http"):
        return url
    parts = urllib.parse.urlsplit(url)
    path = urllib.parse.quote(urllib.parse.unquote(parts.path), safe="/:@-._~!$&'()*+,;=")
    query = urllib.parse.quote(urllib.parse.unquote(parts.query), safe="=&%@:/?-._~!$'()*+,;")
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, path, query, parts.fragment))


def fetch(url: str, timeout: int = 45) -> str:
    req = urllib.request.Request(
        encode_url(url),
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
        encode_url(url),
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


def gnews_article_id(url: str) -> str:
    try:
        parts = urllib.parse.urlparse(url or "").path.split("/")
        if len(parts) > 1 and parts[-2] in ("articles", "read"):
            return parts[-1] or ""
    except Exception:
        return ""
    return ""


def _gnews_signature(html: str) -> tuple[str, str]:
    sg = re.search(r'data-n-a-sg="([^"]+)"', html or "")
    ts = re.search(r'data-n-a-ts="([^"]+)"', html or "")
    if sg and ts:
        return sg.group(1), ts.group(1)
    return "", ""


def _gnews_parse_batch(text: str) -> dict[str, str]:
    body = text or ""
    if "\n\n" in body:
        body = body.split("\n\n", 1)[1]
    body = body.lstrip()
    if body.startswith(")]}'"):
        body = body.split("\n", 1)[1] if "\n" in body else body[4:]
        body = body.lstrip()
    try:
        rows = json.loads(body)
    except Exception:
        return {}
    if rows and isinstance(rows[-1], list) and rows[-1] and rows[-1][0] == "di":
        rows = rows[:-1]
    if rows and isinstance(rows[-1], list) and rows[-1] and rows[-1][0] == "e":
        rows = rows[:-1]
    out: dict[str, str] = {}
    for row in rows:
        if not (isinstance(row, list) and len(row) >= 3):
            continue
        payload = row[2]
        if row[0] == "wrb.fr" or row[1] == "Fbv4je":
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except Exception:
                    continue
            if isinstance(payload, list) and len(payload) > 1 and payload[0] == "garturlres":
                dest = payload[1]
                req_id = None
                for cell in reversed(row[3:]):
                    if cell is not None:
                        req_id = str(cell)
                        break
                if req_id and isinstance(dest, str) and dest.startswith("http"):
                    out[req_id] = dest
    return out


def unwrap_google_urls(urls: list[str]) -> dict[str, str]:
    """Turn news.google.com/rss/articles/... links into publisher URLs."""
    pending: list[tuple[str, str, str, str]] = []
    seen_ids: set[str] = set()
    for url in urls:
        if not is_google_news(url):
            continue
        if url in _GNEWS_CACHE:
            continue
        art_id = gnews_article_id(url)
        if not art_id or art_id in seen_ids:
            continue
        seen_ids.add(art_id)
        page = (
            f"https://news.google.com/rss/articles/{art_id}"
            f"?hl=zh-Hant&gl=HK&ceid=HK:zh-Hant"
        )
        try:
            html = fetch(page, timeout=12)
            sg, ts = _gnews_signature(html)
            if sg and ts:
                pending.append((url, art_id, ts, sg))
        except Exception as e:
            print("gnews params fail", art_id[:24], e)
        time.sleep(0.04)
    for i in range(0, len(pending), 12):
        chunk = pending[i : i + 12]
        envelopes = []
        for idx, (_url, art_id, ts, sg) in enumerate(chunk):
            inner = [
                "garturlreq",
                _GARTURLREQ_CTX,
                art_id,
                int(ts) if str(ts).isdigit() else ts,
                sg,
            ]
            envelopes.append(
                ["Fbv4je", json.dumps(inner, separators=(",", ":")), None, str(idx)]
            )
        body = (
            "f.req="
            + urllib.parse.quote(json.dumps([envelopes], separators=(",", ":")))
        ).encode()
        req = urllib.request.Request(
            "https://news.google.com/_/DotsSplashUi/data/batchexecute",
            data=body,
            headers={
                "User-Agent": UA,
                "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                pairs = _gnews_parse_batch(r.read().decode("utf-8", "replace"))
        except Exception as e:
            print("gnews decode fail", e)
            pairs = {}
        for idx, (url, _art_id, _ts, _sg) in enumerate(chunk):
            dest = pairs.get(str(idx), "")
            if dest:
                _GNEWS_CACHE[url] = dest
    return dict(_GNEWS_CACHE)


def unwrap_url(url: str) -> str:
    if is_google_news(url):
        if url not in _GNEWS_CACHE:
            unwrap_google_urls([url])
        return _GNEWS_CACHE.get(url) or url
    return url


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


def is_app_promo(item: dict) -> bool:
    """限時免費 App / 兌換碼宣傳，從限時情報王拆到 APP 優惠。"""
    title = item.get("title") or ""
    return bool(APP_PROMO.search(title))


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


def inner_html_by_id(html: str, id_token: str) -> str:
    rx = re.compile(
        r"<([a-zA-Z0-9]+)([^>]*\bid=(['\"])"
        + re.escape(id_token)
        + r"\3[^>]*)>",
        re.I,
    )
    m = rx.search(html or "")
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


def inner_html_by_tag(html: str, tag: str) -> str:
    m = re.search(rf"<{re.escape(tag)}\b[^>]*>", html or "", re.I)
    if not m:
        return ""
    start = m.end()
    close = re.search(rf"</{re.escape(tag)}\s*>", html[start:], re.I)
    return html[start : start + close.start()] if close else html[start:]


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
        inner = inner_html_by_class(page, "m-detail-html") or inner_html_by_class(page, "dt-article")
        if inner and re.search(r"仅提供摘要|僅提供摘要", inner):
            lead = inner_html_by_class(page, "m-detail-summary-text") or inner_html_by_class(
                page, "dt-summary-text"
            )
            reason = inner_html_by_class(page, "m-detail-reason-text")
            bits = []
            if lead:
                bits.append(f"<p>{lead}</p>")
            if reason:
                bits.append(f"<p>{reason}</p>")
            return "".join(bits)
        return inner
    if "pcmarket.com.hk" in host:
        inner = (
            inner_html_by_class(page, "td-post-content")
            or inner_html_by_class(page, "post-content")
            or inner_html_by_class(page, "entry-content")
        )
        if inner:
            cut = re.search(
                r'<div[^>]*class="[^"]*(?:td-post-source-tags|td-post-next-prev|td-related|'
                r'related-posts|td-a-rec)',
                inner,
                re.I,
            )
            if cut:
                inner = inner[: cut.start()]
            inner = PCM_FOOTER.sub("", inner)
        return inner
    return inner_html_by_class(page, "entry-content") or inner_html_by_class(page, "post-content")


PARA_JUNK = re.compile(
    r"跳過此內容|其他人也在看|你可能也想看|延伸閱讀|熱門點擊|點擊收看|"
    r"登入\s*首頁|首頁\s*新聞|觀看\s*分類|圖像來源|Getty Images|"
    r"AI重點|文章重點整理|重點[一二三四五六七八九十][：:]|"
    r"更新時間|發佈時間|字體大小|即時國際|即時港聞|相關新聞|"
    r"加入首選來源|Google 偏好|將 Yahoo |另開新視窗|"
    r"^編輯[：:︰]|^記者[：:]",
    re.I,
)
# Site chrome that is not the story: HKEJ print calendar, footer disclaimer, promos.
SITE_CHROME = re.compile(
    r"印刷版出報日|休刊日|信報簡介\s*[\|｜]|服務條款\s*[\|｜]|"
    r"概不構成任何投資意見|股票及指數資料由|期貨指數資料由|"
    r"版權所有，不得轉載|訂戶登入|（節錄）|原文刊於|"
    r"如欲投稿|支持\s*EJ\s*Tech|最早出現於",
    re.I,
)


def _cjk_count(text: str) -> int:
    return sum(1 for ch in text or "" if "\u4e00" <= ch <= "\u9fff")


def is_site_chrome(text: str) -> bool:
    return bool(SITE_CHROME.search(text or ""))


def is_good_para(text: str) -> bool:
    t = (text or "").strip()
    if not t or PARA_JUNK.search(t) or is_site_chrome(t):
        return False
    cjk = _cjk_count(t)
    if cjk < 18 or len(t) < 22:
        return False
    if cjk / max(len(t), 1) < 0.28:
        return False
    return True


def paras_from_chunk(chunk: str) -> list[str]:
    parts = re.split(
        r"</p>|</h[1-6]>|</figcaption>|</blockquote>|<br\s*/?>\s*<br\s*/?>|\n{2,}",
        chunk or "",
        flags=re.I,
    )
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


def strip_noise_html(html: str) -> str:
    html = re.sub(r"<script\b[^>]*>.*?</script>", "", html or "", flags=re.S | re.I)
    html = re.sub(r"<style\b[^>]*>.*?</style>", "", html, flags=re.S | re.I)
    html = re.split(r'id="recommended-article-stream"', html, maxsplit=1)[0]
    return html


def paras_match_title(title: str, paras: list[str]) -> list[str]:
    """Drop leading chrome and trailing related-news; keep the article body."""
    head = _norm_headline(title or "")
    if len(head) < 4 or not paras:
        return paras
    keys = {head[i : i + 2] for i in range(len(head) - 1)}
    kept: list[str] = []
    miss = 0
    for p in paras:
        pn = _norm_headline(p)
        grams = {pn[j : j + 2] for j in range(max(0, len(pn) - 1))}
        hit = len(keys & grams)
        long_p = _cjk_count(p) >= 28
        if hit >= 1 or (kept and long_p):
            kept.append(p)
            miss = 0
            continue
        if not kept:
            continue
        miss += 1
        if miss >= 2:
            break
    if kept:
        return kept
    # A list of unrelated headlines shares no title bigram and is not the story.
    # Real copy that simply doesn't repeat the headline is still kept.
    prose = [
        p
        for p in paras
        if p.count("。") >= 1 and _cjk_count(p) >= 36 and not is_site_chrome(p)
    ]
    return prose[:8]


def _blocks_from_html(chunk: str) -> list[str]:
    """Turn loose article text (not only <p>) into paragraphs, dropping chrome."""
    if not chunk:
        return []
    chunk = re.split(
        r'id=["\'](?:login-message-wrapper|next-article-wrapper|footer)',
        chunk,
        maxsplit=1,
    )[0]
    chunk = re.split(r"支持\s*EJ\s*Tech|如欲投稿", chunk, maxsplit=1, flags=re.I)[0]
    chunk = re.sub(r"<script\b[^>]*>.*?</script>", " ", chunk, flags=re.S | re.I)
    chunk = re.sub(r"</(p|div|h[1-6]|li|blockquote|figcaption|tr)>", "\n", chunk, flags=re.I)
    chunk = re.sub(r"<br\s*/?>", "\n", chunk, flags=re.I)
    out: list[str] = []
    for line in re.split(r"\n+", chunk):
        t = to_hant(re.sub(r"\s+", " ", strip_tags(line)).strip())
        t = re.sub(r"(?:\s*[.．…]){1,}\s*$", "", t).strip()
        if is_good_para(t):
            out.append(t)
    return out


def hkej_paragraphs(html: str) -> list[str]:
    """HKEJ article pages put the story in #article-detail-wrapper and the
    print calendar / other headlines in the footer. Never treat the footer as copy.
    """
    wrapper = inner_html_by_id(html or "", "article-detail-wrapper")
    paras = _blocks_from_html(wrapper)
    if paras:
        return paras[:24]
    for blob in re.findall(r"<script[^>]*ld\+json[^>]*>(.*?)</script>", html or "", re.S | re.I):
        try:
            obj = json.loads(blob)
        except Exception:
            continue
        for node in _ld_walk(obj):
            body = node.get("articleBody") or ""
            if isinstance(body, str) and _cjk_count(body) >= 24:
                got = _blocks_from_html(body) or paras_from_chunk(body)
                if got:
                    return got[:24]
    return []


def extract_paragraphs(html: str, url: str) -> list[str]:
    host = urllib.parse.urlparse(url).netloc.lower()
    inner = ""
    if "ejtech.ai" in host or host.endswith("ejtech.hkej.com"):
        inner = inner_html_by_id(html, "content-area")
        inner = re.split(r"支持\s*EJ\s*Tech|如欲投稿", inner, maxsplit=1, flags=re.I)[0]
    elif "hkej.com" in host:
        # Paywalled pages still include a short excerpt. Footer <p> tags are not the story.
        return hkej_paragraphs(html)
    elif "rthk.hk" in host:
        inner = inner_html_by_class(html, "itemFullText") or inner_html_by_class(html, "itemBody")
    elif "yahoo." in host:
        inner = inner_html_by_tag(html, "article") or inner_html_by_class(
            html, "module-article-body"
        ) or inner_html_by_class(html, "caas-body")
    elif "newmobilelife.com" in host or "aihot.virxact.com" in host or "pcmarket.com.hk" in host:
        inner = extract_source_html(html, url)
    if not inner or len(strip_tags(inner)) < 80:
        for tok in ARTICLE_CLASS_TOKENS:
            chunk = inner_html_by_class(html, tok)
            if chunk and len(strip_tags(chunk)) > len(strip_tags(inner)):
                inner = chunk
    if not inner or len(strip_tags(inner)) < 80:
        art = inner_html_by_tag(html, "article")
        if art and len(strip_tags(art)) > len(strip_tags(inner)):
            inner = art
    if inner:
        inner = strip_noise_html(inner)
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
        src = inner if inner else (html or "")
        for p in re.findall(r"<p\b[^>]*>(.*?)</p>", src, re.S | re.I):
            t = to_hant(re.sub(r"\s+", " ", strip_tags(p)))
            if is_good_para(t):
                extras.append(t)
            if len(extras) >= 24:
                break
        if len(extras) > len(paras):
            paras = extras
    return paras[:24]


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
        html = fetch_prefix(url, timeout=14, nbytes=2_000_000)
        img = parse_og_image(html, url) or first_img_in_html(html, url)
        bits["img"] = img if looks_like_photo(img) else ""
        bits["paras"] = extract_paragraphs(html, url)
    except Exception as e:
        print("article bits fail", url[:80], e)
    _PAGE_CACHE[url] = bits
    _IMG_CACHE[url] = bits["img"]
    return bits


_EJTECH_POSTS: list[dict] | None = None


def _without_kicker(title: str) -> str:
    """Drop a short section kicker such as 'Deel調查｜' or '惠普AI電腦｜'."""
    stripped = re.sub(r"^[^｜|]{1,16}[｜|]\s*", "", title or "").strip()
    return stripped or (title or "")


def titles_same_piece(a: str, b: str) -> bool:
    keys_a = {_norm_headline(a or ""), _norm_headline(_without_kicker(a or ""))}
    keys_b = {_norm_headline(b or ""), _norm_headline(_without_kicker(b or ""))}
    keys_a.discard("")
    keys_b.discard("")
    for x in keys_a:
        for y in keys_b:
            if len(x) >= 8 and len(y) >= 8 and (x in y or y in x):
                return True
            if headlines_similar(x, y) or same_story(x, y):
                return True
    return False


def ejtech_posts() -> list[dict]:
    """Recent EJ Tech posts. HKEJ often paywalls the same CEO AI piece."""
    global _EJTECH_POSTS
    if _EJTECH_POSTS is not None:
        return _EJTECH_POSTS
    _EJTECH_POSTS = []
    try:
        raw = fetch(
            "https://www.ejtech.ai/wp-json/wp/v2/posts?per_page=20&_fields=link,title,content",
            timeout=15,
        )
        rows = json.loads(raw)
    except Exception as e:
        print("ejtech list fail", e)
        return _EJTECH_POSTS
    for row in rows if isinstance(rows, list) else []:
        title = row.get("title") or {}
        if isinstance(title, dict):
            title = title.get("rendered") or ""
        content = row.get("content") or {}
        if isinstance(content, dict):
            content = content.get("rendered") or ""
        title = to_hant(unescape(strip_tags(str(title))))
        html = re.split(r"支持\s*EJ\s*Tech|如欲投稿", str(content), maxsplit=1, flags=re.I)[0]
        paras = [p for p in paras_from_chunk(html) if not is_site_chrome(p)]
        if title and paras:
            _EJTECH_POSTS.append({"title": title, "url": row.get("link") or "", "paras": paras})
    return _EJTECH_POSTS


def ejtech_match(title: str) -> dict | None:
    best: dict | None = None
    best_score = 0
    for post in ejtech_posts():
        if not titles_same_piece(title, post.get("title") or ""):
            continue
        paras = paras_match_title(title, post.get("paras") or []) or list(post.get("paras") or [])
        score = sum(_cjk_count(p) for p in paras)
        if score > best_score:
            best = {"title": post.get("title") or "", "url": post.get("url") or "", "paras": paras}
            best_score = score
    return best


def fill_item_copy(item: dict, extra_urls: list[str] | None = None) -> None:
    urls: list[str] = []
    for u in list(extra_urls or []) + [item.get("sourceUrl") or ""]:
        if is_google_news(u):
            u = unwrap_url(u)
        if u and is_article_url(u) and u not in urls:
            urls.append(u)
    best: list[str] = []
    best_score = 0
    for u in urls[:8]:
        bits = fetch_article_bits(u)
        time.sleep(0.06)
        paras = bits.get("paras") or []
        score = sum(_cjk_count(p) for p in paras)
        if score > best_score:
            best = paras
            best_score = score
            if bits.get("img") and not looks_like_photo(item.get("img") or ""):
                item["img"] = bits["img"]
    title = item.get("title") or ""
    if best:
        matched = paras_match_title(title, best)
        if matched:
            best = matched
            best_score = sum(_cjk_count(p) for p in best)
        else:
            best = []
            best_score = 0
    hkejish = any("hkej.com" in urllib.parse.urlparse(u).netloc.lower() for u in urls)
    if hkejish:
        alt = ejtech_match(title)
        alt_paras = (alt or {}).get("paras") or []
        alt_score = sum(_cjk_count(p) for p in alt_paras)
        if alt and alt_score > best_score + 40:
            best = alt_paras
            best_score = alt_score
            url = alt.get("url") or ""
            if url:
                rel = item.setdefault("related", [])
                if isinstance(rel, list) and not any(
                    isinstance(r, dict) and r.get("url") == url for r in rel
                ):
                    rel.append({"title": alt.get("title") or title, "url": url, "source": "EJ Tech"})
    if best and (best_score >= 80 or (hkejish and best_score >= 36)):
        item["_paras"] = best[:24]
        lead = best[0]
        if len(best) > 1:
            lead = best[0] + best[1]
        cur = item.get("summary") or ""
        # A headline restated with the site name is not a lead.
        thin = cur.count("。") == 0 and _cjk_count(cur) < 36
        off = (
            not cur
            or thin
            or is_dump_summary(cur)
            or "均有報道" in cur
            or is_site_chrome(cur)
            or not paras_match_title(title, [cur])
        )
        if off:
            item["summary"] = to_hant(lead[:420])
        item["keypoints"] = make_keypoints(*best)
        return
    cur = item.get("summary") or ""
    if is_dump_summary(cur) or "均有報道" in cur or is_site_chrome(cur):
        item["keypoints"] = []
        if is_site_chrome(cur):
            item["summary"] = ""
        return
    kps = make_keypoints(cur)
    if kps:
        item["keypoints"] = kps
    elif item.get("keypoints") and all(len(k) < 24 and "。" not in k for k in item["keypoints"]):
        item["keypoints"] = []


def can_extract(url: str) -> bool:
    host = urllib.parse.urlparse(url).netloc.lower()
    return (
        "newmobilelife.com" in host
        or "aihot.virxact.com" in host
        or "pcmarket.com.hk" in host
    )


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


def aihot_item_url(item: dict) -> str:
    if item.get("itemUrl"):
        return item["itemUrl"]
    aid = item.get("articleId") or ""
    if aid:
        return f"https://aihot.virxact.com/items/{aid}"
    return ""


def fetch_aihot_item_body(item: dict) -> str:
    """Build reader HTML from the AI HOT item page (导读 / 推荐理由 / 译文正文)."""
    item_url = aihot_item_url(item)
    page = ""
    if item_url:
        try:
            page = fetch(item_url, timeout=20)
        except Exception as e:
            print("aihot item fail", item_url, e)
    chunks: list[str] = []
    lead = inner_html_by_class(page, "m-detail-summary-text") or inner_html_by_class(
        page, "dt-summary-text"
    )
    if lead and strip_tags(lead).strip():
        chunks.append("<h3>AI 導讀</h3>" + sanitize_body(f"<p>{lead}</p>"))
    reason = inner_html_by_class(page, "m-detail-reason-text")
    if reason and strip_tags(reason).strip():
        chunks.append("<h3>推薦理由</h3>" + sanitize_body(f"<p>{reason}</p>"))
    article = inner_html_by_class(page, "m-detail-html")
    if article and not re.search(r"仅提供摘要|僅提供摘要", article):
        raw = sanitize_body(article)
        if len(strip_tags(raw)) >= MIN_BODY_CHARS:
            chunks.append("<h3>正文</h3>" + raw)
    html = normalize_territory(to_hant("".join(chunks)))
    if len(strip_tags(html)) < 40:
        sum_ = (item.get("summary") or item.get("embedded") or "").strip()
        if sum_:
            html = f"<h3>重點內容</h3><p>{escape(to_hant(sum_))}</p>"
        else:
            return ""
    orig = item.get("sourceUrl") or item_url
    notice = source_notice(zh_source(item.get("sourceName") or "AIHOT"))
    cover = item.get("img") or parse_og_image(page, item_url)
    hero = f'<p><img src="{escape(cover, True)}" alt=""></p>' if cover else ""
    link = (
        f'<p><a href="{escape(orig, True)}" target="_blank" rel="noopener noreferrer">'
        f"查看原文 ↗</a></p>"
        if orig
        else ""
    )
    return notice + hero + html + link


def zh_date(d: date) -> str:
    return f"{d.month}月{d.day}日 周{WEEK[d.weekday()]}"


def zh_long(d: date, hm: str) -> str:
    return f"{d.year}年{d.month}月{d.day}日 周{WEEK[d.weekday()]} {hm}（北京時間）"


def slug_from_url(url: str) -> str:
    part = urllib.parse.unquote(urllib.parse.urlparse(url).path.rstrip("/").split("/")[-1] or "item")
    part = re.sub(r"[^a-zA-Z0-9\-]+", "-", part).strip("-").lower()
    return (part or "item")[:80]


def _aihot_card(
    lab: str,
    iso: str,
    d: date,
    title: str,
    summary: str,
    source_name: str,
    source_url: str,
    aid: str,
    img: str,
    item_url: str = "",
) -> dict:
    show = AIHOT_SHOW.get(lab, to_hant(lab))
    return {
        "title": title,
        "summary": summary,
        "sourceName": source_name,
        "sourceUrl": source_url,
        "itemUrl": item_url,
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


def parse_aihot_report_stories(html: str, iso: str) -> dict[str, list[dict]]:
    """Current AI HOT daily markup (report-story cards)."""
    out: dict[str, list[dict]] = {k: [] for k in AIHOT_LABELS}
    d = date.fromisoformat(iso)
    for block in re.findall(
        r'<article class="report-story"[^>]*>(.*?)</article>', html or "", re.S
    ):
        lab_m = re.search(r'class="report-story-meta"[^>]*>\s*<span>([^<]+)</span>', block)
        tm = re.search(
            r'class="report-story-title"[^>]*>\s*<a href="([^"]+)">(.*?)</a>',
            block,
            re.S,
        )
        if not lab_m or not tm:
            continue
        lab = lab_m.group(1).strip()
        if lab not in out:
            continue
        href, title = tm.group(1), to_hant(strip_tags(tm.group(2)))
        item_url = ("https://aihot.virxact.com" + href) if href.startswith("/") else href
        orig = re.search(
            r'class="report-story-sources"[^>]*>\s*<a href="(https?://[^"]+)"',
            block,
        )
        source_url = orig.group(1) if orig else item_url
        src_m = re.search(r'class="report-source-name"[^>]*>([^<]+)', block)
        source_name = zh_source(src_m.group(1) if src_m else "AIHOT")
        sm = re.search(r'class="report-story-summary"[^>]*>(.*?)</p>', block, re.S)
        summary = to_hant(strip_tags(sm.group(1))[:400] if sm else "")
        aid_m = re.search(r"/items/([^/?#]+)", href)
        aid = slug_from_url(aid_m.group(1) if aid_m else item_url)
        img = rss_image(block) or first_img_in_html(block, "https://aihot.virxact.com")
        if img.startswith("data:"):
            img = ""
        out[lab].append(
            _aihot_card(
                lab, iso, d, title, summary, source_name, source_url, aid, img, item_url
            )
        )
    return out


def parse_aihot_legacy(html: str, iso: str) -> dict[str, list[dict]]:
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
            img = rss_image(block) or first_img_in_html(block, "https://aihot.virxact.com")
            out[lab].append(
                _aihot_card(lab, iso, d, title, summary, source_name, source_url, aid, img, source_url)
            )
    return out


def parse_aihot(html: str, iso: str) -> dict[str, list[dict]]:
    stories = parse_aihot_report_stories(html, iso)
    if sum(len(v) for v in stories.values()):
        return stories
    return parse_aihot_legacy(html, iso)


def aihot_from_existing(data: dict) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {k: [] for k in AIHOT_LABELS}
    aliases = {}
    for k, v in AIHOT_SHOW.items():
        aliases[k] = k
        aliases[v] = k
    for sec in data.get("sections") or []:
        if sec.get("kind") != "aihot":
            continue
        lab = aliases.get(sec.get("label") or "")
        if lab:
            out[lab] = list(sec.get("items") or [])
    return out


def clean_pcm_summary(text: str) -> str:
    text = to_hant(re.sub(r"\s+", " ", strip_tags(text or "")).strip())
    text = PCM_FOOTER.sub("", text).strip()
    return text[:280]


def parse_pcm_feed(xml: str, today: date) -> list[dict]:
    items: list[dict] = []
    for block in re.findall(r"<item\b[^>]*>(.*?)</item>", xml or "", re.S | re.I):
        title = clean_headline(to_hant(_rss_text(block, "title")))
        link = _rss_text(block, "link")
        if not title or not link or "pcmarket.com.hk" not in link:
            continue
        desc = _rss_text(block, "description") or _rss_text(block, "content:encoded")
        summary = clean_pcm_summary(desc)
        if is_dump_summary(summary):
            summary = ""
        pd = _rss_text(block, "pubDate") or _rss_text(block, "dc:date")
        d = today
        iso = today.isoformat()
        if pd:
            try:
                raw_dt = parsedate_to_datetime(pd)
                if raw_dt.tzinfo is None:
                    raw_dt = raw_dt.replace(tzinfo=TZ)
                d = raw_dt.astimezone(TZ).date()
                iso = d.isoformat()
            except Exception:
                try:
                    d = datetime.fromisoformat(pd.replace("Z", "+00:00")).astimezone(TZ).date()
                    iso = d.isoformat()
                except Exception:
                    pass
        img = rss_image(block) or rss_image(desc)
        if img:
            img = upgrade_wp_img(img)
        aid = slug_from_url(link)
        items.append(
            {
                "title": title,
                "summary": summary,
                "sourceName": "PCM",
                "sourceUrl": link,
                "img": img,
                "imgKind": "og" if img else "",
                "imgCreator": "",
                "imgLicense": "",
                "imgSource": link if img else "",
                "date": zh_date(d),
                "isoDate": iso,
                "ci": CI[PCM_LABEL],
                "kind": "pcm",
                "isNew": iso == today.isoformat(),
                "_sec_label": PCM_LABEL,
                "articleId": aid,
                "articleUrl": f"articles/{aid}.html",
                "embedded": summary,
            }
        )
    return items


def build_pcm_items(today: date) -> list[dict]:
    raw: list[dict] = []
    for url in PCM_FEEDS:
        try:
            xml = fetch(url, timeout=20)
            got = parse_pcm_feed(xml, today)
            print("pcm", url.split("pcmarket.com.hk")[-1] or "/", len(got))
            raw.extend(got)
            time.sleep(0.08)
        except Exception as e:
            print("pcm fetch fail", url, e)
    uniq: list[dict] = []
    seen: set[str] = set()
    for it in raw:
        u = it.get("sourceUrl") or ""
        if not u or u in seen:
            continue
        seen.add(u)
        uniq.append(it)
    uniq.sort(key=lambda x: x.get("isoDate") or "", reverse=True)
    out = uniq[:PCM_MAX]
    for it in out:
        fill_item_photo(it)
        if not it.get("keypoints"):
            it["keypoints"] = make_keypoints(it.get("summary") or "")
        time.sleep(0.06)
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


def story_key(title: str) -> str:
    t = title or ""
    t = re.sub(r"\s*[-–—|｜]\s*[^|-–—｜]{1,30}$", "", t)
    t = re.sub(r"playstation\s*6", "ps6", t, flags=re.I)
    t = re.sub(r"playstation", "ps", t, flags=re.I)
    t = t.replace("恒指", "港股").replace("低開", "開跌").replace("記憶體", "ram")
    t = t.lower()
    t = re.sub(r"[「」『』《》【】()（）\[\]\s\-—:：,，.。!！?？、·0-9０-９%％$＄￥¥]+", "", t)
    return t


def _lcs_span(a: str, b: str) -> str:
    best = ""
    for i in range(len(a)):
        for j in range(len(b)):
            k = 0
            while i + k < len(a) and j + k < len(b) and a[i + k] == b[j + k]:
                k += 1
                if k > len(best):
                    best = a[i : i + k]
    return best


def _cov(short: str, long: str) -> float:
    if len(short) < 2 or len(long) < 2:
        return 0.0
    gs = {short[i : i + 2] for i in range(len(short) - 1)}
    gl = {long[i : i + 2] for i in range(len(long) - 1)}
    return len(gs & gl) / len(gs) if gs else 0.0


def same_story(a: str, b: str) -> bool:
    """True when two headlines are the same event, not merely the same product."""
    ra = re.match(r"【([^】]{1,8})】", a or "")
    rb = re.match(r"【([^】]{1,8})】", b or "")
    if ra and rb and ra.group(1) != rb.group(1):
        return False
    sa, sb = story_key(a), story_key(b)
    if len(sa) < 8 or len(sb) < 8:
        return False
    short, long = (sa, sb) if len(sa) <= len(sb) else (sb, sa)
    if sa == sb or (len(short) >= 12 and short in long):
        return True
    full = _cov(short, long)
    frag = _lcs_span(sa, sb)
    sa2 = sa.replace(frag, "", 1) if frag else sa
    sb2 = sb.replace(frag, "", 1) if frag else sb
    s2, l2 = (sa2, sb2) if len(sa2) <= len(sb2) else (sb2, sa2)
    after = _cov(s2, l2)
    latin = bool(frag) and bool(re.fullmatch(r"[a-z0-9]+", frag))
    if full >= 0.70 and len(short) >= 10:
        return True
    if after >= 0.35 and len(frag) >= 6 and len(s2) >= 6 and not latin:
        return True
    if after >= 0.55 and len(frag) >= 6 and len(s2) >= 6:
        return True
    nums_a = {n for n in re.findall(r"\d{3,}", a or "") if not n.startswith("202")}
    nums_b = {n for n in re.findall(r"\d{3,}", b or "") if not n.startswith("202")}
    if nums_a & nums_b and full >= 0.40 and len(frag) >= 5:
        return True
    return False


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
        parts.append("<h3>正文</h3>")
        for p in paras[:24]:
            parts.append(f"<p>{escape(p)}</p>")
    else:
        summary = item.get("summary") or ""
        if summary:
            parts.append(f"<h3>正文</h3><p>{escape(summary)}</p>")
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


def build_clustered_news(
    today: date,
    feeds: list[tuple[str, str]],
    *,
    label: str,
    kind: str,
    aid_prefix: str,
    max_items: int,
    hours: int,
    log_name: str,
    title_ok=None,
) -> tuple[list[dict], dict[str, str]]:
    """Fetch RSS feeds, merge same-event headlines, build cards + reader bodies."""
    raw: list[dict] = []
    for name, url in feeds:
        try:
            xml = fetch(url, timeout=20)
            items = parse_rss_feed(xml, name)
            if title_ok:
                items = [it for it in items if title_ok(it.get("title") or "")]
            print(log_name, name, len(items))
            raw.extend(items)
        except Exception as e:
            print(f"{log_name} fetch fail", name, e)
    clusters: list[dict] = []
    for it in raw:
        placed = False
        for c in clusters:
            if headlines_similar(it["title"], c["title"]) or same_story(it["title"], c["title"]):
                c["members"].append(it)
                for s in it["sources"]:
                    if s and s not in c["sources"]:
                        c["sources"].append(s)
                have = {x.get("url") for x in c["related"]}
                for r in it["related"]:
                    if r.get("url") not in have:
                        c["related"].append(r)
                        have.add(r.get("url"))
                if (
                    it.get("summary")
                    and not is_dump_summary(it["summary"])
                    and summary_score(it["summary"]) > summary_score(c.get("summary") or "")
                ):
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
    cut = datetime.now(TZ) - timedelta(hours=hours)
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
    _take(with_art, max_items)
    _take(fresh, max_items)
    chosen = chosen[:max_items]
    g_urls: list[str] = []
    for c in chosen:
        rows = list(c.get("related") or []) + list(c.get("members") or [])
        rows.sort(
            key=lambda r: (
                2
                if "rthk" in (r.get("source") or "").lower()
                or "香港電台" in (r.get("source") or "")
                else 0
            )
        )
        n = 0
        for r in rows:
            u = (r.get("url") if isinstance(r, dict) else "") or ""
            if is_google_news(u):
                g_urls.append(u)
                n += 1
                if n >= 6:
                    break
    print(f"{log_name} gnews unwrap", len(g_urls))
    unwrap_google_urls(g_urls)
    for c in chosen:
        for bucket in (c.get("related") or [], c.get("members") or []):
            for r in bucket:
                if not isinstance(r, dict):
                    continue
                dest = _GNEWS_CACHE.get(r.get("url") or "")
                if dest:
                    r["url"] = dest
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
        aid = f"{aid_prefix}-{digest}"
        if aid in used_ids:
            aid = (
                f"{aid_prefix}-"
                + hashlib.sha1((c["title"] + dt.strftime("%H%M")).encode("utf-8")).hexdigest()[:12]
            )
        used_ids.add(aid)
        src_label = " · ".join(sources[:4]) if sources else label
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
            "ci": CI[label],
            "kind": kind,
            "isNew": d == today,
            "_sec_label": label,
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


def news_feeds() -> list[tuple[str, str]]:
    """今日要聞 = 國際／兩岸要聞 + 香港本地媒體，同一 URL 只抓一次。"""
    seen: set[str] = set()
    out: list[tuple[str, str]] = []
    for name, url in list(WIRE_FEEDS) + list(LOCAL_FEEDS):
        if url in seen:
            continue
        seen.add(url)
        out.append((name, url))
    return out


def is_ai_industry_title(title: str) -> bool:
    return bool(AI_INDUSTRY_RX.search(title or ""))


_AI_ENTITY = re.compile(
    r"DeepSeek|OpenAI|Anthropic|Gemini|Claude|英偉達|英伟达|NVIDIA|ChatGPT|MiniMax",
    re.I,
)
_AI_BAN = re.compile(r"禁|移除")


def ai_industry_dup(a: str, b: str) -> bool:
    if same_story(a, b) or headlines_similar(a, b):
        return True
    ea = {m.group(0).lower() for m in _AI_ENTITY.finditer(a or "")}
    eb = {m.group(0).lower() for m in _AI_ENTITY.finditer(b or "")}
    if ea & eb and _AI_BAN.search(a or "") and _AI_BAN.search(b or ""):
        return True
    return False


def supplement_ai_industry(aihot: dict[str, list[dict]], today: date) -> dict[str, str]:
    """Fill 行業動態 from other AI sites when AI HOT itself is thin."""
    items, bodies = build_clustered_news(
        today,
        AI_INDUSTRY_FEEDS,
        label="行业动态",
        kind="aihot",
        aid_prefix="aiind",
        max_items=AI_INDUSTRY_MAX,
        hours=AI_INDUSTRY_HOURS,
        log_name="aiind",
        title_ok=is_ai_industry_title,
    )
    have = [it.get("title") or "" for rows in aihot.values() for it in rows]
    added: list[dict] = []
    for it in items:
        title = it.get("title") or ""
        if any(ai_industry_dup(title, prev) for prev in have if prev):
            continue
        it["kind"] = "aihot"
        it["ci"] = CI["行业动态"]
        it["_sec_label"] = AIHOT_SHOW["行业动态"]
        added.append(it)
        have.append(title)
    folded: list[dict] = []
    for it in added:
        hit = next((c for c in folded if ai_industry_dup(c.get("title") or "", it.get("title") or "")), None)
        if not hit:
            folded.append(it)
            continue
        names = []
        for part in ((hit.get("sourceName") or "") + " · " + (it.get("sourceName") or "")).split("·"):
            part = re.sub(r"等\d+家", "", part).strip()
            if part and part not in names:
                names.append(part)
        hit["sourceName"] = " · ".join(names[:4]) + (f" 等{len(names)}家" if len(names) > 4 else "")
        extra = bodies.get(it.get("articleId") or "")
        if extra and hit.get("articleId") in bodies:
            bodies[hit["articleId"]] += "<h3>同一事件的其他報道</h3>" + extra
        if (it.get("summary") or "") and len(it.get("summary") or "") > len(hit.get("summary") or ""):
            hit["summary"] = it["summary"]
    aihot["行业动态"] = list(aihot.get("行业动态") or []) + folded
    print("ai industry extra", len(folded), "total", len(aihot["行业动态"]))
    return {it["articleId"]: bodies[it["articleId"]] for it in folded if it.get("articleId") in bodies}


def build_wire_items(today: date) -> tuple[list[dict], dict[str, str]]:
    return build_clustered_news(
        today,
        news_feeds(),
        label=WIRE_LABEL,
        kind="wire",
        aid_prefix="wire",
        max_items=WIRE_MAX,
        hours=WIRE_HOURS,
        log_name="wire",
    )


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
    # Do not use str.format: article CSS and body text both contain `{...}`.
    p.write_text(
        ARTICLE_TPL.replace("__TITLE__", title)
        .replace("__BODY__", body)
        .replace("__URL__", item["sourceUrl"]),
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

    try:
        aihot_html = fetch(f"https://aihot.virxact.com/daily/{iso}")
        aihot = parse_aihot(aihot_html, iso)
    except Exception as e:
        print("aihot fetch fail", e)
        aihot = {k: [] for k in AIHOT_LABELS}
    aihot_n = sum(len(v) for v in aihot.values())
    if aihot_n == 0:
        print(f"AI HOT {iso} parsed 0 articles, keeping previous AI HOT cards")
        aihot = aihot_from_existing(data)
        aihot_n = sum(len(v) for v in aihot.values())
    else:
        for items in aihot.values():
            for it in items:
                fill_item_photo(it)
                fill_item_copy(it, [aihot_item_url(it), it.get("sourceUrl") or ""])

    industry_bodies: dict[str, str] = {}
    try:
        industry_bodies = supplement_ai_industry(aihot, today)
        aihot_n = sum(len(v) for v in aihot.values())
    except Exception as e:
        print("ai industry fail", e)

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
    app_items = [it for it in uniq if is_app_promo(it)][:APP_MAX]
    nml40 = [it for it in uniq if not is_app_promo(it)][:40]
    if not nml40 and not app_items:
        raise SystemExit("NML parsed 0 articles")
    for it in app_items:
        it["ci"] = CI[APP_LABEL]
        it["kind"] = "app"
        it["_sec_label"] = APP_LABEL
    for it in nml40 + app_items:
        it["isNew"] = it["isoDate"] == iso
        if not it.get("keypoints"):
            it["keypoints"] = make_keypoints(it.get("summary") or "")
    new_count = sum(1 for it in nml40 if it["isNew"])
    added = sum(1 for it in nml40 + app_items if it["sourceUrl"] not in prev_nml_urls)

    wire_items: list[dict] = []
    wire_bodies: dict[str, str] = {}
    try:
        wire_items, wire_bodies = build_wire_items(today)
    except Exception as e:
        print("wire fail", e)

    pcm_items: list[dict] = []
    try:
        pcm_items = build_pcm_items(today)
    except Exception as e:
        print("pcm fail", e)

    deals = next(s for s in data["sections"] if s.get("kind") == "deals")
    deals["label"] = to_hant(deals.get("label") or "熱門優惠")
    for it in deals.get("items") or []:
        hantify_item(it)

    keep = {it["sourceUrl"] for it in nml40}
    keep.update(it["sourceUrl"] for it in app_items)
    keep.update(it["sourceUrl"] for it in pcm_items)
    for items in aihot.values():
        keep.update(it["sourceUrl"] for it in items)
    keep.update(it["sourceUrl"] for it in deals["items"])
    keep.update(it["sourceUrl"] for it in wire_items)

    old = [hantify_item(it) for it in (data.get("old") or [])]
    old_urls = {it.get("sourceUrl") for it in old}
    for sec in data["sections"]:
        if sec.get("kind") in ("deals", "wire", "local"):
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
    for it in old:
        if is_app_promo(it):
            it["board"] = APP_LABEL
            it["ci"] = CI[APP_LABEL]
            it["kind"] = "app"
        elif it.get("kind") == "pcm" or "pcmarket.com.hk" in (it.get("sourceUrl") or ""):
            it["board"] = PCM_LABEL
            it["ci"] = CI[PCM_LABEL]
            it["kind"] = "pcm"

    sections = []
    if nml40:
        sections.append({"label": "限時情報王", "items": nml40, "kind": "external", "ci": 5})
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
    if pcm_items:
        sections.append({"label": PCM_LABEL, "items": pcm_items, "kind": "pcm", "ci": CI[PCM_LABEL]})
    if app_items:
        sections.append({"label": APP_LABEL, "items": app_items, "kind": "app", "ci": CI[APP_LABEL]})

    def _item_day(it: dict) -> date | None:
        raw = (it.get("isoDate") or "")[:10]
        try:
            return date.fromisoformat(raw)
        except Exception:
            return None

    kept_sections = []
    moved = 0
    for sec in sections:
        if sec.get("kind") == "deals":
            kept_sections.append(sec)
            continue
        fresh, aged = [], []
        for it in sec.get("items") or []:
            day = _item_day(it)
            if day is not None and day < today:
                aged.append(it)
            else:
                fresh.append(it)
        for it in aged:
            u = it.get("sourceUrl")
            if u and u in old_urls:
                continue
            rec = {k: it.get(k) for k in (
                "title", "summary", "sourceName", "sourceUrl", "img", "imgKind",
                "imgCreator", "imgLicense", "imgSource", "date", "isoDate",
                "articleId", "articleUrl", "ci", "kind",
            )}
            rec["board"] = sec.get("label") or "其他"
            rec["keypoints"] = it.get("keypoints") or []
            hantify_item(rec)
            old.insert(0, rec)
            if u:
                old_urls.add(u)
            moved += 1
        if fresh:
            sec = dict(sec)
            sec["items"] = fresh
            kept_sections.append(sec)
    sections = kept_sections
    print("moved to old", moved, "before", iso)

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

    nml_today = next((len(s["items"]) for s in sections if s.get("kind") == "external"), 0)
    nml_js = "const NML = {total:%d, shown:%d, newCount:%d};" % (
        old_total + added, nml_today, new_count
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
        if it.get("kind") in ("wire", "local"):
            body = wire_bodies.get(aid)
            if body:
                articles[aid] = body
                if it in flat:
                    write_article(it, body)
            elif aid not in articles:
                articles[aid] = notice_html(it["sourceUrl"])
            continue
        if aid in industry_bodies:
            articles[aid] = industry_bodies[aid]
            if it in flat:
                write_article(it, industry_bodies[aid])
            ok += 1
            continue
        cur = articles.get(aid, "")
        filled_now = False
        if not is_stub(cur):
            cover = it.get("img") or ""
            if cover and "<img" not in cur:
                cur = f'<p><img src="{escape(cover, True)}" alt=""></p>' + cur
                articles[aid] = cur
            skip += 1
        elif it.get("kind") == "aihot":
            live = bool(it.get("itemUrl")) or (aid or "").startswith("cmt")
            if not live:
                if not cur:
                    articles.setdefault(aid, notice_html(it.get("sourceUrl") or ""))
                    kept += 1
            else:
                body = fetch_aihot_item_body(it)
                time.sleep(0.12)
                if body:
                    articles[aid] = body
                    ok += 1
                    filled_now = True
                else:
                    articles.setdefault(aid, notice_html(it.get("sourceUrl") or aihot_item_url(it)))
                    fail += 1
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
          "aihot", sum(1 for v in aihot.values() for it in v if it.get("img")),
          "pcm", sum(1 for it in pcm_items if it.get("img")))
    print("keypoints wire", sum(1 for it in wire_items if (it.get("keypoints") or [""])[0:1] and len((it.get("keypoints") or [""])[0]) > 18),
          "/", len(wire_items))
    print("flat", len(flat), "old", len(old), "added", added, "wire", len(wire_items),
          "pcm", len(pcm_items))
    print("bodies filled", ok, "fail", fail, "already", skip, "notice", kept)


if __name__ == "__main__":
    main()
