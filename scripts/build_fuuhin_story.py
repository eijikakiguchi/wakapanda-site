#!/usr/bin/env python3
"""
data/archive.json から「楓浜ものがたり」(fuuhin-monogatari.html)を生成する。

955本ぜんぶを並べるpanda/fuuhin.htmlとは別物。
誕生から現在まで、章立てのストーリーとしてハイライト動画で読ませるページ。
章の区切りと事実は wakapanda/ 配下の既存レポート・台帳で検品済みのものだけを使う
(2025年6月に浜家4頭が成都へ渡航、は再開プラン.md・楓浜テスト動画準備キット.mdで確認済み)。
"""
import html
import json
from pathlib import Path

BASE = Path(__file__).parent.parent
ARCHIVE = BASE / "data" / "archive.json"
OUT = BASE / "fuuhin-monogatari.html"

HIGHLIGHTS_PER_CHAPTER = 4

CHAPTERS = [
    {
        "title": "誕生・はじめまして",
        "period": "2020年11月〜2021年4月",
        "start": "2020-11-01", "end": "2021-04-30",
        "text": "2020年11月22日、良浜のもとに楓浜が生まれました。生まれてすぐの赤ちゃんパンダは"
                "しばらく非公開で育てられるため、映像として残っているのは生後100日を過ぎた"
                "2021年1月ごろから。よちよち歩きもままならない、いちばん小さいころの楓浜です。",
    },
    {
        "title": "赤ちゃん期",
        "period": "2021年5月〜9月",
        "start": "2021-05-01", "end": "2021-09-30",
        "text": "甘えん坊全開の時期。母・良浜にべったりで、ちょっとしたことで「かまって」と鳴く姿が"
                "たくさん撮れています。まだこの頃は、後の「帰宅劇」シリーズの兆しはありません。",
    },
    {
        "title": "やんちゃ期(飼育員さんとの黄金期)",
        "period": "2021年10月〜2022年12月",
        "start": "2021-10-01", "end": "2022-12-31",
        "text": "このチャンネル最大の当たり期間。大好きな飼育員さんを見つけると一直線に飛びかかる、"
                "呼ばれると渋々帰る——そんな「帰宅劇」「回収劇場」シリーズがここで生まれました。"
                "歴代1位(1,300万回)もこの時期の一本です。",
    },
    {
        "title": "白浜での日々",
        "period": "2023年〜2025年5月",
        "start": "2023-01-01", "end": "2025-05-24",
        "text": "大きくなってからも、飼育員さんへの愛情は変わらず。良浜ママとの再会シーンなど、"
                "落ち着いた大人の楓浜の日常が積み重なっていった時期です。",
    },
    {
        "title": "お別れ",
        "period": "2025年5月〜6月",
        "start": "2025-05-25", "end": "2025-06-30",
        "text": "中国への渡航が決まり、検疫期間に入る直前の「ラストデー」。"
                "白浜での日々に区切りがついた、特別な数週間です。"
                "そして2025年6月、楓浜は良浜・結浜・彩浜とともに中国・成都へ旅立ちました。"
                "白浜時代に撮りためた映像は、これからも少しずつ公開していきます。",
    },
]

# ハイライトから除外する動画(内容が章の趣旨と合わないもの)
EXCLUDE_IDS = {
    "ii99SR9oLA8",  # 歌つきの振り返り総集編。お別れの日々の実写記録ではない(2026-08-22えいじさん検品)
}

HEAD = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>楓浜ものがたり | 浜家の思い出、ぜんぶここに。</title>
<meta name="description" content="2020年11月22日生まれ、和歌ぱんだチャンネルの看板娘・楓浜の誕生から旅立ちまでを、章立てのハイライトで振り返るページです。">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>&#128060;</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@500;700;900&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/style.css">
<meta property="og:title" content="楓浜ものがたり | 浜家の思い出、ぜんぶここに。">
<meta property="og:description" content="誕生から旅立ちまで、楓浜の歩みを章立てで振り返ります。">
<meta property="og:type" content="website">
<meta property="og:url" content="https://wakapanda.com/fuuhin-monogatari.html">
</head>
<body>

<header class="site-header">
  <a class="brand" href="index.html">
    <span class="brand-ears" aria-hidden="true"><i></i><i></i></span>
    和歌ぱんだ
  </a>
  <nav class="site-nav" aria-label="ページ内メニュー">
    <a href="index.html#panda">個体別アルバム</a>
    <a href="index.html">トップへもどる</a>
  </nav>
</header>

<main>

  <section class="panda-hero">
{face_html}
    <div class="panda-hero-body">
      <h1 class="panda-hero-name">楓浜ものがたり</h1>
      <span class="panda-hero-tag">誕生から、旅立ちまで。</span>
      <p class="panda-hero-bio">
        2020年11月22日生まれ。和歌ぱんだチャンネル開始の年に生まれ、いちばん長く撮り続けられた楓浜だけの、
        全成長記録です。ほかの子たちの動画は<a href="panda/fuuhin.html">個体別アルバム</a>からどうぞ。
      </p>
    </div>
  </section>

{chapters}

</main>

<footer class="site-footer">
  <p class="footer-brand">和歌ぱんだ &#128060; wakapanda.com</p>
  <nav aria-label="フッターメニュー">
    <a href="about.html">このサイトについて</a>
    <a href="policy.html">運営ポリシー</a>
    <a href="https://www.youtube.com/channel/UCfALH0tKUgs-XsL-Xhwvj6A" target="_blank" rel="noopener">YouTube</a>
  </nav>
  <p class="footer-copy">&copy; 和歌ぱんだ &mdash; 掲載の映像・写真はすべて運営者が撮影したものです。</p>
</footer>

</body>
</html>
"""

CHAPTER_TMPL = """  <section class="section{alt}">
    <div class="section-head">
      <h2>{title}</h2>
      <p>{period}{count_note}</p>
    </div>
    <p class="chapter-text">{text}</p>
    <div class="video-grid">
{cards}
    </div>
    <p class="section-more">
      <a class="btn btn-ghost" href="panda/fuuhin.html">この時期をふくむ楓浜の全動画を見る</a>
    </p>
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


CSS_FACE = """    <div class="panda-face" aria-hidden="true">
      <i class="ear ear-l"></i><i class="ear ear-r"></i>
      <i class="eye eye-l"></i><i class="eye eye-r"></i>
      <i class="nose"></i>
    </div>"""


def face_html():
    # img/panda/fuuhin.png(jpg/webp)があればイラストを使う(build_panda_pages.pyと同じ約束)
    for ext in ("png", "jpg", "webp"):
        if (BASE / "img" / "panda" / f"fuuhin.{ext}").exists():
            return (f'    <img class="panda-illust" src="img/panda/fuuhin.{ext}" '
                    f'alt="楓浜のイラスト" width="120" height="120">')
    return CSS_FACE


def main():
    archive = json.loads(ARCHIVE.read_text(encoding="utf-8"))
    fu = [v for v in archive if "楓浜" in v["individuals"] and v["type"] == "通常"]
    for v in fu:
        v["_d"] = v["shootDate"] or v["publishDate"] or ""

    chapters_html = []
    for i, ch in enumerate(CHAPTERS):
        period_all = [v for v in fu if ch["start"] <= v["_d"] <= ch["end"]]
        # 3頭以上まとめてタグの動画(名前を並べただけの説明動画等)はハイライトから除外し、
        # 楓浜が主役級(タグ2頭以下)の動画だけを対象にする
        chunk = [v for v in period_all if len(v["individuals"]) <= 2 and v["id"] not in EXCLUDE_IDS]
        chunk.sort(key=lambda v: -v["views"])
        picks = chunk[:HIGHLIGHTS_PER_CHAPTER]
        cards = "\n".join(card_html(v) for v in picks)
        count_note = f"・この時期の動画 {len(period_all)}本のうちハイライト{len(picks)}本" if period_all else "・該当動画なし"
        chapters_html.append(CHAPTER_TMPL.format(
            alt=" section-fur" if i % 2 == 1 else "",
            title=ch["title"], period=ch["period"], count_note=count_note,
            text=ch["text"], cards=cards,
        ))
        print(f"{ch['title']}: {len(chunk)}本中{len(picks)}本を掲載")

    out_html = HEAD.format(chapters="\n".join(chapters_html), face_html=face_html())
    OUT.write_text(out_html, encoding="utf-8")
    print(f"出力: {OUT}")


if __name__ == "__main__":
    main()
