#!/usr/bin/env python3
"""
data/source/全動画リスト_日付つき.csv から data/archive.json を生成する。

archive.json は「浜家の思い出、ぜんぶここに。」まとめサイトの本体データ。
既存の data/videos.json(RSSベースの最新動画15件・自動更新)とは別物なので触らない。
"""
import csv
import json
import re
from pathlib import Path

BASE = Path(__file__).parent.parent
SRC_CSV = BASE / "data" / "source" / "全動画リスト_日付つき.csv"
OUT_JSON = BASE / "data" / "archive.json"


PANDA_KEYWORDS = {
    "楓浜": ["楓浜", "ふうひん"],
    "彩浜": ["彩浜", "さいひん"],
    "結浜": ["結浜", "ゆいひん"],
    "良浜": ["良浜", "らうひん"],
    "桜浜": ["桜浜", "おうひん"],
    "桃浜": ["桃浜", "とうひん"],
    "永明": ["永明", "えいめい"],
}


def extract_id(url):
    m = re.search(r"v=([\w-]{11})", url)
    return m.group(1) if m else None


def detect_individuals(title):
    # 既存のCSV「個体」列はタイトル文字列から機械判定されたもので、
    # 検品したところ100%タイトル一致(手動判定の混入なし)だったので、
    # タイトル走査に一本化して「名前なし」1,201本のうち埋もれていた分も拾う
    return [name for name, keys in PANDA_KEYWORDS.items() if any(k in title for k in keys)]


def main():
    rows = list(csv.DictReader(open(SRC_CSV, encoding="utf-8-sig")))
    out = []
    for r in rows:
        vid = extract_id(r["URL"])
        if not vid:
            continue
        out.append({
            "id": vid,
            "title": r["タイトル"],
            "type": r["種別"],
            "views": int(r["再生回数"] or 0),
            "durationSec": int(r["長さ秒"] or 0),
            "individuals": detect_individuals(r["タイトル"]),
            "theme": r["テーマ"] if r["テーマ"] != "(その他)" else "",
            "publishDate": r["公開日"] or None,
            "shootDate": r["撮影日"] or None,
        })

    OUT_JSON.parent.mkdir(exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    print(f"出力: {OUT_JSON}")
    print(f"件数: {len(out)}")
    with_shoot = sum(1 for v in out if v["shootDate"])
    print(f"撮影日あり: {with_shoot}")

    # 個体別カウント(タグづけ済みのみ・複数出演は各個体でカウント)
    from collections import Counter
    c = Counter()
    for v in out:
        for name in v["individuals"]:
            c[name] += 1
    print("個体別(タグ済み・延べ):", dict(c.most_common()))


if __name__ == "__main__":
    main()
