#!/usr/bin/env python3
"""和歌ぱんだチャンネルのRSSから最新動画リストを data/videos.json に書き出す。

GitHub Actions が毎日実行する。手元でも `python3 scripts/update_videos.py` で動く。
2026-11-24: RSSは新しい15本しか出ず、ほとんどショートになるので、
  ・ショートかどうかを "short" に記録(RSSのリンクが /shorts/ ならショート)
  ・前回までのリストと合わせて、横の動画は新しい12本・ショートは新しい6本を残す(横がたまっていく)
"""
import json
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

CHANNEL_ID = "UCfALH0tKUgs-XsL-Xhwvj6A"
FEED_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "videos.json"
MAX_LONG = 12   # 横の動画
MAX_SHORT = 6   # ショート
ARCHIVE_PATH = OUT_PATH.parent / "archive.json"

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "yt": "http://www.youtube.com/xml/schemas/2015",
}


def is_alive(video_id: str) -> bool:
    """oEmbedで公開中か確かめる(404/401/403=非公開・削除)。通信エラーのときは残す。"""
    url = "https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(
        f"https://www.youtube.com/watch?v={video_id}")
    try:
        urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "wakapanda-site-updater"}), timeout=20)
        return True
    except urllib.error.HTTPError as e:
        return e.code not in (401, 403, 404)
    except Exception:
        return True


def main() -> None:
    req = urllib.request.Request(FEED_URL, headers={"User-Agent": "wakapanda-site-updater"})
    with urllib.request.urlopen(req, timeout=30) as res:
        root = ET.fromstring(res.read())

    videos = []
    for entry in root.findall("atom:entry", NS):
        video_id = entry.findtext("yt:videoId", default="", namespaces=NS)
        title = entry.findtext("atom:title", default="", namespaces=NS)
        published = entry.findtext("atom:published", default="", namespaces=NS)
        link = entry.find("atom:link", NS)
        href = link.get("href", "") if link is not None else ""
        if video_id and title:
            videos.append({"id": video_id, "title": title, "published": published[:10],
                           "short": "/shorts/" in href})

    if not videos:
        # フィードが空・取得失敗のときは既存ファイルを守る(fail soft)
        raise SystemExit("フィードから動画を取得できなかったため、videos.json は更新しません")

    # 前回までのリストと合わせる(RSSにある方を正とする)
    seen = {v["id"] for v in videos}
    old = []
    if OUT_PATH.exists():
        old = json.loads(OUT_PATH.read_text(encoding="utf-8"))
    short_ids = set()
    if ARCHIVE_PATH.exists():
        short_ids = {a["id"] for a in json.loads(ARCHIVE_PATH.read_text(encoding="utf-8")) if a.get("type") == "ショート"}
    for v in old:
        if v["id"] in seen:
            continue
        if not is_alive(v["id"]):
            print(f"非公開・削除のため外しました: {v['id']}")
            continue
        v.setdefault("short", v["id"] in short_ids)
        videos.append(v)
        seen.add(v["id"])

    videos.sort(key=lambda v: v["published"], reverse=True)
    longs = [v for v in videos if not v["short"]][:MAX_LONG]
    shorts = [v for v in videos if v["short"]][:MAX_SHORT]
    videos = sorted(longs + shorts, key=lambda v: v["published"], reverse=True)

    OUT_PATH.write_text(
        json.dumps(videos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"{len(videos)}本を書き出しました → {OUT_PATH}")


if __name__ == "__main__":
    main()
