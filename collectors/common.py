"""収集の共通部品。標準ライブラリだけで動かす（Actionsで依存を入れない）。"""
import json
import time
import urllib.request
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))
UA = "sapporo-hojokin-bot/0.1 (+https://github.com/co-cre/sapporo-hojokin)"


def now_jst():
    return datetime.now(JST)


def fetch(url, timeout=30, retries=2):
    last = None
    for i in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:  # 一時的な失敗だけ再試行する
            last = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"取得失敗: {url}: {last}")


def fetch_json(url):
    return json.loads(fetch(url))


def record(*, source, level, id, title, url, org="", max_amount=None, rate="",
           start=None, end=None, published=None, note=""):
    """制度1件の共通形。end が None のものは締切不明として扱う。"""
    return {
        "id": f"{source}:{id}",
        "source": source,
        "level": level,  # 国 / 道 / 市 / その他
        "title": title.strip(),
        "org": org.strip(),
        "max_amount": max_amount,
        "rate": rate,
        "start": start,
        "end": end,
        "published": published,
        "url": url,
        "note": note,
    }
