"""情報源から集めて data/subsidies.json を更新する。

  python3 collect.py              # 全情報源
  python3 collect.py --only jnet21  # 1時間ごとの J-Net21 だけ

前回のデータと合わせる:
- 初めて見た日（first_seen）と最後に確認した日（checked）を持つ
- 締切が過ぎたものは落とす。締切の無いもの（RSS由来）は初見から KEEP_DAYS 日で落とす
- 取得に失敗した情報源（いつもあるはずが0件のときも）は前回分を残し、終了コード1で知らせる（古いまま黙って出し続けない）
"""
import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

from collectors import hokkaido, jgrants, jnet21, sapporo
from collectors.common import JST, now_jst

SOURCES = {"jgrants": jgrants, "sapporo": sapporo, "hokkaido": hokkaido, "jnet21": jnet21}
# いつも何件かあるはずの情報源。0件ならページ構成の変更などを疑い、失敗として前回分を残す
# （札幌市・J-Net21 は新着が無い日に0件が普通なので含めない）
NEVER_EMPTY = {"jgrants", "hokkaido"}
DATA = Path(__file__).parent / "data" / "subsidies.json"
KEEP_DAYS = 60


def _parse(ts):
    if not ts:
        return None
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(JST)


def _alive(item, now):
    end = _parse(item.get("end"))
    if end:
        return end >= now
    first = _parse(item.get("first_seen"))
    return first is None or now - first <= timedelta(days=KEEP_DAYS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=SOURCES.keys())
    args = ap.parse_args()

    now = now_jst()
    prev = json.loads(DATA.read_text()) if DATA.exists() else {"items": [], "sources": {}}
    prev_items = {it["id"]: it for it in prev["items"]}
    targets = [args.only] if args.only else list(SOURCES)

    fresh, status, failed = {}, dict(prev.get("sources", {})), []
    for name in targets:
        try:
            got = SOURCES[name].collect()
            if not got and name in NEVER_EMPTY:
                raise RuntimeError("0件だった（ページ構成が変わった可能性）")
            status[name] = {"ok": True, "count": len(got), "at": now.isoformat(timespec="seconds")}
            for it in got:
                fresh[it["id"]] = it
        except Exception as e:
            failed.append(name)
            status[name] = {**status.get(name, {}), "ok": False, "error": str(e)[:300],
                            "failed_at": now.isoformat(timespec="seconds")}

    merged = {}
    for id_, it in prev_items.items():
        # 今回取りに行った情報源のうち、取れたものは今回の結果で置き換える
        if it["source"] in targets and it["source"] not in failed and it["source"] != "jnet21":
            continue
        merged[id_] = it
    for id_, it in fresh.items():
        old = prev_items.get(id_, {})
        merged[id_] = {**it, "first_seen": old.get("first_seen") or now.isoformat(timespec="seconds"),
                       "checked": now.isoformat(timespec="seconds")}

    items = sorted((it for it in merged.values() if _alive(it, now)),
                   key=lambda it: (it.get("end") or "9999", it["title"]))
    out = {"updated": now.isoformat(timespec="seconds"), "sources": status, "items": items}
    if [i["id"] for i in items] != [i["id"] for i in prev["items"]] or not args.only:
        DATA.parent.mkdir(exist_ok=True)
        DATA.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")

    counts = {s: sum(1 for i in items if i["source"] == s) for s in SOURCES}
    print(f"{len(items)}件 {counts}" + (f" 失敗: {failed}" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
