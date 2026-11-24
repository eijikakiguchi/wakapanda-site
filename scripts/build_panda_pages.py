#!/usr/bin/env python3
"""
data/archive.json から個体別アルバムページ(panda/*.html)を生成する。

各ページ: プロフィール見出し + 先頭60本を静的HTMLで書き出し(JS無しでも読める)
         + 全件をJSONで埋め込み(js/panda.jsが「もっと見る」「並べ替え」に使う)
"""
import html
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from site_parts import site_header, site_footer, stamp

BASE = Path(__file__).parent.parent
ARCHIVE = BASE / "data" / "archive.json"
OUT_DIR = BASE / "panda"
STATIC_BATCH = 60

# プロフィール(誕生日が未検品のものは月日を出さない=事実は出典必須の掟)
PANDAS = [
    {
        "slug": "fuuhin", "name": "楓浜", "yomi": "ふうひん",
        "born": "2020年11月22日生まれ",
        "tag": "チャンネルの看板娘",
        "bio": "2020年、チャンネル開始の年に生まれた末っ子。飼育員さんが大好きで、"
               "「帰宅劇」と呼ばれる名場面をいくつも残した。1,967本のうち955本に登場する、"
               "このチャンネル最大のスター。",
    },
    {
        "slug": "saihin", "name": "彩浜", "yomi": "さいひん",
        "born": "2018年8月14日生まれ",
        "tag": "小さく生まれて、大きく育った",
        "bio": "遊びの天才。突風に飛ばされたり、コントのような場面を作ったり、"
               "見ている人を笑顔にする名場面が多い。",
    },
    {
        "slug": "yuihin", "name": "結浜", "yomi": "ゆいひん",
        "born": "2016年9月18日生まれ",
        "tag": "マイペースなお姉さん",
        "bio": "木の上でのんびりするのが得意。伝説のリアクション芸「パンダ落ちる」の主でもある。",
    },
    {
        "slug": "rauhin", "name": "良浜", "yomi": "らうひん",
        "born": "2000年9月6日生まれ",
        "tag": "浜家みんなのお母さん",
        "bio": "おおらかで優しい、一家の大黒柱。子どもたちとの再会シーンでは、"
               "見ている側まで胸が熱くなる。",
    },
    {
        "slug": "ouhin", "name": "桜浜", "yomi": "おうひん",
        "born": "2014年12月2日生まれ",
        "tag": "桃浜と双子の姉妹",
        "bio": "桃浜とふたり、双子として生まれた一頭。2023年2月に中国へ出発する前の"
               "白浜での日々を記録している。",
    },
    {
        "slug": "touhin", "name": "桃浜", "yomi": "とうひん",
        "born": "2014年12月2日生まれ",
        "tag": "桜浜と双子の姉妹",
        "bio": "桜浜とふたり、双子として生まれた一頭。2023年2月に中国へ出発する前の"
               "白浜での日々を記録している。",
    },
    {
        "slug": "eimei", "name": "永明", "yomi": "えいめい",
        "born": "1992年9月14日・北京動物園生まれ",
        "tag": "浜家のお父さん",
        "bio": "レジェンド枠。長く白浜で暮らし、浜家の歴史そのものを見てきた一頭。"
               "2023年2月に中国・成都へ渡り、2025年1月、32歳で静かに旅立ちました。",
    },
]

HEAD = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name}({yomi}) | 浜家の思い出、ぜんぶここに。</title>
<meta name="description" content="{name}({yomi})の動画を{count}本、撮影日順にまとめました。和歌ぱんだ・浜家の思い出アーカイブ。">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>&#128060;</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@500;700;900&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../css/style.css">
<script src="../js/phrase.js" defer></script>
<meta property="og:title" content="{name}({yomi}) | 浜家の思い出、ぜんぶここに。">
<meta property="og:description" content="{name}の動画を{count}本、撮影日順にまとめました。">
<meta property="og:type" content="website">
<meta property="og:url" content="https://wakapanda.com/panda/{slug}.html">
<meta property="og:image" content="https://wakapanda.com/img/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="https://wakapanda.com/panda/{slug}.html">
</head>
<body>

{site_header_html}

<main data-panda-page>

  <section class="panda-hero">
{face_html}
    <div class="panda-hero-body">
      <h1 class="panda-hero-name">{name}<span class="yomi">{yomi}</span></h1>
      <span class="panda-hero-tag">{tag}</span>
      <p class="panda-hero-bio">{bio}</p>
      <div class="panda-hero-stats">
        <span><strong>{count}本</strong>収録動画</span>
        <span><strong>{born}</strong></span>
      </div>
    </div>
  </section>

  <div class="panda-toolbar">
    <p class="toolbar-hint">古い日付から新しい日付へ、時系列で並んでいます。</p>
    <div class="sort-group" role="group" aria-label="並べ替え">
      <button type="button" class="sort-btn js-sort" data-order="time" aria-pressed="true">時系列</button>
      <button type="button" class="sort-btn js-sort" data-order="popular" aria-pressed="false">人気順</button>
    </div>
  </div>

  <section class="section section-flush-top">
    <div class="video-grid" id="video-grid" data-shown="{shown}">
{static_cards}
    </div>
    <p class="load-more">
      <button type="button" class="btn btn-ghost js-more"{more_hidden}>もっと見る</button>
    </p>
  </section>

  <script type="application/json">{json_data}</script>

</main>

{site_footer_html}

<script src="../js/panda.js"></script>
</body>
</html>
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
    # 2020-02-11より前に撮った動画は載せない(トップのモザイクと同じ扱い・2026-11-24えいじさん裁定)
    archive = [v for v in archive if not (v.get("shootDate") and v["shootDate"] < "2020-02-11")]
    OUT_DIR.mkdir(exist_ok=True)

    for p in PANDAS:
        videos = [v for v in archive if p["name"] in v["individuals"]]
        videos.sort(key=sort_key)

        static_slice = videos[:STATIC_BATCH]
        static_cards = "\n".join(card_html(v) for v in static_slice)
        more_hidden = "" if len(videos) > STATIC_BATCH else " hidden"

        html_out = HEAD.format(
            site_header_html=site_header("../", "個体別アルバム"), site_footer_html=site_footer("../"),
            name=p["name"], yomi=p["yomi"], slug=p["slug"],
            tag=p["tag"], bio=p["bio"], born=p["born"],
            count=len(videos), shown=len(static_slice),
            static_cards=static_cards, more_hidden=more_hidden,
            face_html=stamp("../", p["slug"], ""),
            json_data=json.dumps(videos, ensure_ascii=False),
        )
        out_path = OUT_DIR / f"{p['slug']}.html"
        out_path.write_text(html_out, encoding="utf-8")
        print(f"{p['name']}({p['slug']}): {len(videos)}本 -> {out_path.relative_to(BASE)}")


if __name__ == "__main__":
    main()
