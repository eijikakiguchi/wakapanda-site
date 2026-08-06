#!/usr/bin/env python3
"""和歌ぱんだチャンネルのRSSから最新動画リストを data/videos.json に書き出す。

GitHub Actions が毎日実行する。手元でも `python3 scripts/update_videos.py` で動く。
"""
import json
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

CHANNEL_ID = "UCfALH0tKUgs-XsL-Xhwvj6A"
FEED_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "videos.json"
MAX_VIDEOS = 12

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "yt": "http://www.youtube.com/xml/schemas/2015",
}


def main() -> None:
    req = urllib.request.Request(FEED_URL, headers={"User-Agent": "wakapanda-site-updater"})
    with urllib.request.urlopen(req, timeout=30) as res:
        root = ET.fromstring(res.read())

    videos = []
    for entry in root.findall("atom:entry", NS):
        video_id = entry.findtext("yt:videoId", default="", namespaces=NS)
        title = entry.findtext("atom:title", default="", namespaces=NS)
        published = entry.findtext("atom:published", default="", namespaces=NS)
        if video_id and title:
            videos.append({"id": video_id, "title": title, "published": published[:10]})

    videos.sort(key=lambda v: v["published"], reverse=True)
    videos = videos[:MAX_VIDEOS]

    if not videos:
        # フィードが空・取得失敗のときは既存ファイルを守る(fail soft)
        raise SystemExit("フィードから動画を取得できなかったため、videos.json は更新しません")

    OUT_PATH.write_text(
        json.dumps(videos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"{len(videos)}本を書き出しました → {OUT_PATH}")


if __name__ == "__main__":
    main()
