"""北海道庁 経済部中小企業課「補助金・助成金・支援金」一覧（CC BY）。

一覧のタイトルに【募集終了】【受付終了】などが付くので、終わったものは落とす。
"""
import html
import re
import urllib.parse

from .common import fetch, record

PAGE = "https://www.pref.hokkaido.lg.jp/kz/csk/a0009/b0006/"
ENDED = re.compile(r"終了|自主返還|効果検証|実施状況|実績報告|R[3-6]-|令和[3-6３-６]年度")


def collect():
    body = fetch(PAGE)
    out = []
    for href, text in re.findall(r'<a href="(/kz/csk/[^"]+\.html)">([^<]+)</a>', body):
        title = html.unescape(text).strip()
        if ENDED.search(title):
            continue
        url = urllib.parse.urljoin(PAGE, href)
        out.append(record(
            source="hokkaido", level="道", id=href, title=title, url=url,
            org="北海道 経済部地域経済局中小企業課",
        ))
    return out
