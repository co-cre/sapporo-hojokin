"""札幌市 新着情報RSS。産業・ビジネス分野の補助・助成だけ拾う。

札幌市のページは要約の転載に許諾が要るので、タイトルとリンクだけ持つ。
"""
import re

from .common import fetch, record

RSS = "https://www.city.sapporo.jp/new/shinchaku.xml"
WORDS = re.compile(r"補助|助成|支援金|奨励金|給付金|交付金")
BIZ = "観光・産業・ビジネス"


def _tag(item, name):
    m = re.search(rf"<{name}>(.*?)</{name}>", item, re.S)
    return m.group(1).strip() if m else ""


def collect():
    xml = fetch(RSS)
    out = []
    for item in re.findall(r"<item .*?</item>", xml, re.S):
        title, link = _tag(item, "title"), _tag(item, "link")
        subject, creator = _tag(item, "dc:subject"), _tag(item, "dc:creator")
        if not WORDS.search(title):
            continue
        if not (subject.startswith(BIZ) or "経済観光局" in creator):
            continue
        out.append(record(
            source="sapporo", level="市", id=link, title=title, url=link,
            org=creator, published=_tag(item, "dc:date"),
        ))
    return out
