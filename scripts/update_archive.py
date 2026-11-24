#!/usr/bin/env python3
"""和歌ぱんだのRSSに出た新しい動画を、全動画リスト(CSV)に足して、一覧とページを作り直す。

GitHub Actions が毎朝 update_videos.py のあとに実行する。手元でも動く。
2026-11-24 追加: それまでは data/archive.json が 8/14 公開ぶんで止まっていて、
  7頭のアルバム・楓浜ものがたり・記念日カレンダー・テーマ別ページに新しい動画が出なかった。

- 足すのは「RSSにあって、CSVにまだない動画」だけ(公開中のものしかRSSには出ない)
- 公開日は日本時間に直す(RSSは世界標準時。朝8時公開だと前の日になるため)
- 撮影日は空欄(これまでどおり、ページでは公開日で並べる)
- 長さは動画のページから読む。読めなければ0(ページでは長さを出さない)
- RSSにある15本は、題名と再生回数を毎朝上書きする(題名を変えた・回数が伸びたのを反映)
- CSVと archive.json の動画がずれていたら(前回が途中で止まった等)、足す動画がなくても作り直す
- 何も変わらなかった日は、何も書きかえない
"""
import json
import csv
import datetime as dt
import re
import subprocess
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SRC_CSV = BASE / "data" / "source" / "全動画リスト_日付つき.csv"
CHANNEL_ID = "UCfALH0tKUgs-XsL-Xhwvj6A"
FEED_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
UA = {"User-Agent": "wakapanda-site-updater"}
JST = dt.timezone(dt.timedelta(hours=9))
NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "yt": "http://www.youtube.com/xml/schemas/2015",
    "media": "http://search.yahoo.com/mrss/",
}
# build_archive.py と同じ名前の見分け方(題名に名前があるか)
PANDA_KEYWORDS = {
    "楓浜": ["楓浜", "ふうひん"],
    "彩浜": ["彩浜", "さいひん"],
    "結浜": ["結浜", "ゆいひん"],
    "良浜": ["良浜", "らうひん"],
    "桜浜": ["桜浜", "おうひん"],
    "桃浜": ["桃浜", "とうひん"],
    "永明": ["永明", "えいめい"],
}
# アーカイブを使うページ(順番どおりに作り直す)
BUILDS = ["build_archive.py", "build_panda_pages.py", "build_fuuhin_story.py",
          "build_calendar.py", "build_highlights.py"]


def length_seconds(video_id: str) -> int:
    try:
        req = urllib.request.Request(f"https://www.youtube.com/watch?v={video_id}&hl=ja", headers=UA)
        html = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "ignore")
        m = re.search(r'"lengthSeconds":"(\d+)"', html)
        return int(m.group(1)) if m else 0
    except Exception:
        return 0


def main() -> None:
    with urllib.request.urlopen(urllib.request.Request(FEED_URL, headers=UA), timeout=30) as res:
        root = ET.fromstring(res.read())

    rows = list(csv.DictReader(open(SRC_CSV, encoding="utf-8-sig")))
    fields = list(rows[0].keys())
    known = {m.group(1) for r in rows if (m := re.search(r"v=([\w-]{11})", r["URL"]))}

    by_id = {m.group(1): r for r in rows if (m := re.search(r"v=([\w-]{11})", r["URL"]))}
    changed = False
    new = []
    for e in root.findall("atom:entry", NS):
        vid = e.findtext("yt:videoId", default="", namespaces=NS)
        title = e.findtext("atom:title", default="", namespaces=NS)
        published = e.findtext("atom:published", default="", namespaces=NS)
        if not vid or not title or not published:
            continue
        stats = e.find("media:group/media:community/media:statistics", NS)
        views = stats.get("views", "0") if stats is not None else "0"
        if vid in known:
            r = by_id[vid]
            if r["タイトル"] != title or (views != "0" and r["再生回数"] != views):
                r["タイトル"] = title
                if views != "0":
                    r["再生回数"] = views
                changed = True
            continue
        link = e.find("atom:link", NS)
        short = "/shorts/" in (link.get("href", "") if link is not None else "")
        pub_jst = dt.datetime.fromisoformat(published).astimezone(JST).strftime("%Y-%m-%d")
        names = [n for n, keys in PANDA_KEYWORDS.items() if any(k in title for k in keys)]
        new.append({
            "タイトル": title,
            "種別": "ショート" if short else "通常",
            "再生回数": views,
            "長さ秒": "0" if short else str(length_seconds(vid)),
            "個体": "・".join(names) if names else "(名前なし)",
            "テーマ": "(その他)",
            "URL": f"https://www.youtube.com/watch?v={vid}",
            "公開日": pub_jst,
            "撮影日": "",
        })

    archive_path = BASE / "data" / "archive.json"
    archive_ids = set()
    if archive_path.exists():
        archive_ids = {a["id"] for a in json.loads(archive_path.read_text(encoding="utf-8"))}
    out_of_sync = archive_ids != known

    if not new and not changed and not out_of_sync:
        print("新しい動画も変わったところもありません(何も書きかえません)")
        return

    new.sort(key=lambda r: r["公開日"])
    with open(SRC_CSV, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows + new)
    for r in new:
        print(f"足しました: {r['公開日']} {r['種別']} {r['タイトル'][:40]}")

    for script in BUILDS:
        subprocess.run([sys.executable, str(BASE / "scripts" / script)], check=True)


if __name__ == "__main__":
    main()
