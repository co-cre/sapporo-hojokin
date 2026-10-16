"""data/subsidies.json から public/index.html を作る。1枚のHTMLにデータを埋め込み、絞り込みはブラウザで行う。"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).parent
SOURCE_LABEL = {
    "jgrants": ("jGrants（デジタル庁）", "https://www.jgrants-portal.go.jp/"),
    "hokkaido": ("北海道 中小企業課（CC BY 4.0）", "https://www.pref.hokkaido.lg.jp/kz/csk/a0009/b0006/"),
    "sapporo": ("札幌市 新着情報", "https://www.city.sapporo.jp/new/index.html"),
    "jnet21": ("J-Net21（中小機構）", "https://j-net21.smrj.go.jp/snavi/support/"),
}


def main():
    cfg = json.loads((ROOT / "config.json").read_text())
    data = json.loads((ROOT / "data" / "subsidies.json").read_text())
    items = [{k: it.get(k) for k in ("level", "source", "title", "org", "max_amount", "end", "published", "url", "checked")}
             for it in data["items"]]
    line = ""
    if cfg.get("line_url"):
        line = (f'<p class="line"><a href="{html.escape(cfg["line_url"])}" rel="noopener">'
                f'{html.escape(cfg["line_text"])}</a></p>')
    sources = "".join(
        f'<li><a href="{u}" rel="noopener">{html.escape(n)}</a></li>' for n, u in SOURCE_LABEL.values())
    page = (ROOT / "template.html").read_text()
    page = (page.replace("__SITE_NAME__", html.escape(cfg["site_name"]))
                .replace("__LEAD__", html.escape(cfg["lead"]))
                .replace("__LINE__", line)
                .replace("__SOURCES__", sources)
                .replace("__OPERATOR__", html.escape(cfg["operator"]))
                .replace("__UPDATED__", data["updated"][:16].replace("T", " "))
                .replace("__DATA__", json.dumps(items, ensure_ascii=False).replace("</", "<\\/")))
    out = ROOT / "public"
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(page)
    print(f"public/index.html {len(items)}件")


if __name__ == "__main__":
    main()
