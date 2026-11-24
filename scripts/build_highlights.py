#!/usr/bin/env python3
"""
data/archive.json から名場面集(meiba-shu.html)を生成する。テーマ別の横糸の入口。
panda/*.html と同じ「先頭60本を静的HTML + 残りをJSON埋め込み」方式(js/panda.jsを共用)。
"""
import html
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from site_parts import site_header, site_footer, stamp

BASE = Path(__file__).parent.parent
ARCHIVE = BASE / "data" / "archive.json"
OUT = BASE / "meiba-shu.html"
STATIC_BATCH = 60

THEMES = [
    {
        "key": "kaiin", "title": "飼育員さんとの攻防",
        "lead": "呼ばれたら渋々帰る、見つけたら一直線に飛びつく。このチャンネルの黄金パターンです。",
        "match": lambda v: "飼育員" in v["title"],
    },
    {
        "key": "asobi", "title": "遊び・ハプニング",
        "lead": "転んだり、はまったり、驚いたり。見ているだけで笑顔になる名場面。",
        "match": lambda v: "遊び・ハプニング" in v["theme"],
    },
    {
        "key": "oyako", "title": "親子の時間",
        "lead": "良浜ママと子どもたち、きょうだい同士。浜家の絆が見える動画たち。",
        "match": lambda v: "親子" in v["theme"],
    },
    {
        "key": "iyashi", "title": "寝顔・癒し",
        "lead": "まったり、うとうと。見ているこちらまで力が抜ける、癒しの時間。",
        "match": lambda v: "寝顔・癒し" in v["theme"],
    },
]

HEAD = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>テーマ別に見る | 浜家の思い出、ぜんぶここに。</title>
<meta name="description" content="飼育員さんとの攻防、遊び・ハプニング、親子の時間、寝顔・癒し。浜家の動画をテーマ別にまとめました。">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>&#128060;</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@500;700;900&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/style.css">
<script src="js/phrase.js" defer></script>
<meta property="og:title" content="テーマ別に見る | 浜家の思い出、ぜんぶここに。">
<meta property="og:description" content="テーマ別に見る、浜家の名場面。">
<meta property="og:type" content="website">
<meta property="og:url" content="https://wakapanda.com/meiba-shu.html">
<meta property="og:image" content="https://wakapanda.com/img/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="https://wakapanda.com/meiba-shu.html">
</head>
<body>

{site_header_html}

<main>
  <section class="hero hero-compact">
    <div class="hero-inner">
      <p class="hero-eyebrow">テーマで振り返る</p>
      <h1 class="hero-title">テーマ別に見る</h1>
      <p class="hero-lead">個体をまたいで、テーマで浜家の動画を振り返るページです。</p>
    </div>
  </section>

{sections}
</main>

{site_footer_html}

<script src="js/panda.js"></script>
</body>
</html>
"""

SECTION_TMPL = """  <section class="section{alt}" data-panda-page id="{key}">
    <div class="section-head">
      <h2>{title}</h2>
      <p>{lead}収録{count}本。</p>
    </div>
    <div class="panda-toolbar">
      <p class="toolbar-hint">古い日付から新しい日付へ、時系列で並んでいます。</p>
      <div class="sort-group" role="group" aria-label="並べ替え">
        <button type="button" class="sort-btn js-sort" data-order="time" aria-pressed="true">時系列</button>
        <button type="button" class="sort-btn js-sort" data-order="popular" aria-pressed="false">人気順</button>
      </div>
    </div>
    <div class="video-grid" data-shown="{shown}">
{static_cards}
    </div>
    <p class="load-more">
      <button type="button" class="btn btn-ghost js-more"{more_hidden}>もっと見る</button>
    </p>
    <script type="application/json">{json_data}</script>
  </section>
"""


def format_views(n):
    if n >= 10000:
        return f"{round(n / 10000)}万回"
    return f"{n}回"


def format_duration(sec):
    m, s = divmod(int(sec or 0), 60)
    return f"{m}:{s:02d}"


def card_html(v):
    date_label = (v["shootDate"] or v["publishDate"] or "").replace("-", "/")
    title = html.escape(v["title"])
    dur = f' <span class="nowrap">({format_duration(v["durationSec"])})</span>' if v["durationSec"] else ""
    return (
        f'      <a class="video-card" href="https://www.youtube.com/watch?v={v["id"]}" target="_blank" rel="noopener">'
        f'<img src="https://i.ytimg.com/vi/{v["id"]}/hqdefault.jpg" alt="" loading="lazy" width="320" height="180">'
        f'<div class="video-body"><h3>{title}{dur}</h3>'
        f'<p class="video-meta"><span>{date_label}</span><span>{format_views(v["views"])}</span></p>'
        f'</div></a>'
    )


def sort_key(v):
    return (v["shootDate"] or v["publishDate"] or "", v["id"])


def main():
    archive = json.loads(ARCHIVE.read_text(encoding="utf-8"))
    sections = []
    for i, theme in enumerate(THEMES):
        videos = [v for v in archive if theme["match"](v)]
        videos.sort(key=sort_key)
        static_slice = videos[:STATIC_BATCH]
        static_cards = "\n".join(card_html(v) for v in static_slice)
        more_hidden = "" if len(videos) > STATIC_BATCH else " hidden"
        sections.append(SECTION_TMPL.format(
            alt=" section-fur" if i % 2 == 1 else "",
            key=theme["key"], title=theme["title"], lead=theme["lead"],
            count=len(videos), shown=len(static_slice),
            static_cards=static_cards, more_hidden=more_hidden,
            json_data=json.dumps(videos, ensure_ascii=False),
        ))
        print(f"{theme['title']}: {len(videos)}本")

    out_html = HEAD.format(site_header_html=site_header("", "テーマ別に見る"), site_footer_html=site_footer(""), sections="\n".join(sections))
    OUT.write_text(out_html, encoding="utf-8")
    print(f"出力: {OUT}")


if __name__ == "__main__":
    main()
