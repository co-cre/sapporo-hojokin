"""jGrants 公開API（デジタル庁）。認証不要。ポータルHTMLは robots.txt で禁止なのでAPIだけ使う。

keyword は2文字以上が必須で、一致した制度しか返らない。複数語で叩いて合わせる。
対象地域は「北海道」を含むもの（全国の制度も都道府県を列挙して北海道を含む）と「全国」の両方を取る。
"""
import re
import urllib.parse

from .common import fetch_json, record

API = "https://api.jgrants-portal.go.jp/exp/v1/public/subsidies"
KEYWORDS = ["補助", "助成", "支援", "事業", "交付", "給付"]
AREAS = ["北海道", "全国"]
# 「小樽市〇〇補助金」のような他の市町村の制度は札幌の事業者が使えないので落とす
OTHER_TOWN = re.compile(r"^(?!札幌市)[^\s（(「都]{1,6}?[市町村](?![場民街])")


def _level(item):
    """全国（または多くの都道府県）向けなら国、北海道を含む少数の地域向けなら道とみなす。"""
    areas = [a.strip() for a in (item.get("target_area_search") or "").split("/")]
    return "国" if "全国" in areas or len(areas) >= 10 else "道"


def collect():
    seen = {}
    for kw in KEYWORDS:
        for area in AREAS:
            q = urllib.parse.urlencode({
                "keyword": kw, "sort": "acceptance_end_datetime", "order": "ASC",
                "acceptance": 1, "target_area_search": area,
            })
            for it in fetch_json(f"{API}?{q}").get("result", []):
                seen[it["id"]] = it
    out = []
    for it in seen.values():
        if OTHER_TOWN.match(it.get("title") or ""):
            continue
        out.append(record(
            source="jgrants", level=_level(it), id=it["id"],
            title=it.get("title") or it.get("name", ""),
            org=it.get("institution_name") or "",
            max_amount=it.get("subsidy_max_limit") or None,
            start=it.get("acceptance_start_datetime"),
            end=it.get("acceptance_end_datetime"),
            url=f"https://www.jgrants-portal.go.jp/subsidy/{it['id']}",
            note=it.get("target_number_of_employees") or "",
        ))
    return out
