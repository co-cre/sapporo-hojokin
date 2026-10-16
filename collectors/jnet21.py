"""J-Net21 支援情報ヘッドライン RSS。全国の新着が十数件しか載らないため1時間ごとに取って溜める。

中小機構の規程で本文の転載は不可。タイトルとリンクだけ持つ。北海道（JP-01）のものだけ残す。
"""
import html
import re

from .common import fetch, record

RSS = "https://j-net21.smrj.go.jp/snavi/support/support.xml"
SUBJECT = re.compile(r"補助金・助成金")
# 札幌の事業者が使えるのは札幌市と北海道全域のものだけ（他の市町村の制度は対象外）
PLACES = ("札幌市", "北海道")


def _tag(item, name):
    m = re.search(rf"<{name}>(.*?)</{name}>", item, re.S)
    return m.group(1).strip() if m else ""


def collect():
    xml = fetch(RSS)
    out = []
    for item in re.findall(r"<item>.*?</item>", xml, re.S):
        if "<rdf:value>JP-01</rdf:value>" not in item:
            continue
        if not SUBJECT.search(_tag(item, "dc:subject")):
            continue
        title = html.unescape(_tag(item, "title"))
        m = re.match(r"【(.+?)】", title)
        if not m or m.group(1) not in PLACES:
            continue
        out.append(record(
            source="jnet21", level="その他", id=_tag(item, "link"), title=title,
            url=_tag(item, "link"), org=m.group(1) if m else "",
            published=_tag(item, "dc:date"),
        ))
    return out
