#!/usr/bin/env python3
"""
data/bamen.json と data/tokushu.json から、名場面ページ(bamen/<id>.html)・名場面の一覧(bamen/index.html)・
特集ページ(tokushu/<key>.html)・sitemap.xml を作る。(2026-11-24 名場面サイト・軍配の方針書どおり)

掟:
- 載せるのは YouTube で公開済みの場面だけ。映像は YouTube の埋め込み(クリックして再生)で見せる
- 広告・アフィリエイトは載せない
- 埋め込みには end を付けない(場面のあとも続けて見てもらう)
- 場面IDは「撮影日-ひとこと」で一度決めたら変えない(動画を上げ直しても URL が残るように)
- 1場面1ページ。同じ場面が入っている動画が複数あれば videos に並べる(先頭が埋め込みに使う動画)
- 個体が確定していない場面は載せない(data 側で pandas に確定名だけ入れる)
- 歌の動画(MV)は場面ページにしない。元の場面の songs に {id,title,start,publish} を入れ、公開日時を過ぎたものだけ
  「この場面が出てくる歌」として出す(予約中のMVは公開日に作り直すと出る)
- 年齢・撮影日の表記・場面の長さ・関連場面・特集の期間はここで計算する(手で二重に持たない)
"""
import datetime as dt
import html
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from site_parts import site_header, site_footer, stamp

BASE = Path(__file__).parent.parent
BAMEN = BASE / "data" / "bamen.json"
TOKUSHU = BASE / "data" / "tokushu.json"
SITE = "https://wakapanda.com"
CHANNEL = "https://www.youtube.com/channel/UCfALH0tKUgs-XsL-Xhwvj6A"

# 個体: 読み・誕生日・個体ページ
PANDAS = {
    "良浜": ("らうひん", "2000-09-06", "rauhin"),
    "永明": ("えいめい", "1992-09-14", "eimei"),
    "結浜": ("ゆいひん", "2016-09-18", "yuihin"),
    "彩浜": ("さいひん", "2018-08-14", "saihin"),
    "桜浜": ("おうひん", "2014-12-02", "ouhin"),
    "桃浜": ("とうひん", "2014-12-02", "touhin"),
    "楓浜": ("ふうひん", "2020-11-22", "fuuhin"),
}

e = html.escape


# ---------- 計算 ----------
def d(s):
    return dt.date.fromisoformat(s)


def date_label(s):
    x = d(s)
    return f"{x.year}年{x.month}月{x.day}日"


def month_label(s):
    x = d(s)
    return f"{x.year}年{x.month}月"


def months_old(name, shot):
    b, x = d(PANDAS[name][1]), d(shot)
    m = (x.year - b.year) * 12 + (x.month - b.month) - (1 if x.day < b.day else 0)
    return m


def age_label(name, shot):
    m = months_old(name, shot)
    if m < 12:
        return f"生後{m}か月"
    y, r = divmod(m, 12)
    return f"{y}歳" if r == 0 else f"{y}歳{r}か月"


def length_label(sec):
    sec = int(round(sec))
    if sec < 60:
        return f"約{max(10, round(sec / 10) * 10)}秒"
    m, s = divmod(sec, 60)
    return f"約{m}分" if s < 15 else (f"約{m}分30秒" if s < 45 else f"約{m + 1}分")


def mmss(sec):
    m, s = divmod(int(sec), 60)
    return f"{m}:{s:02d}"


def main_video(s):
    return s["videos"][0]


def is_public(g):
    """歌(MV)の公開日時を過ぎているか。予約中のMVへのリンクは出さない"""
    return dt.datetime.fromisoformat(g["publish"]) <= dt.datetime.now(dt.timezone.utc)


def has_photo(s):
    return (BASE / "img" / "bamen" / f"{s['id']}.jpg").exists()


def thumb(s, up):
    if has_photo(s):
        return f"{up}img/bamen/{s['id']}.jpg"
    return f"https://i.ytimg.com/vi/{main_video(s)['id']}/hqdefault.jpg"


def thumb_abs(s):
    if has_photo(s):
        return f"{SITE}/img/bamen/{s['id']}.jpg"
    return f"https://i.ytimg.com/vi/{main_video(s)['id']}/hqdefault.jpg"


def related_of(s, scenes, tokushu_of):
    """同じ特集 → 同じ個体 → 撮影日が近い順に3つ"""
    tk = tokushu_of.get(s["id"])
    same_tk = set(tk["scenes"]) if tk else set()

    def score(o):
        return (
            0 if o["id"] in same_tk else 1,
            0 if set(o["pandas"]) & set(s["pandas"]) else 1,
            abs((d(o["date"]) - d(s["date"])).days),
        )

    return sorted((o for o in scenes if o["id"] != s["id"]), key=score)[:3]


def jsonld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>\n"


def breadcrumb(items):
    return jsonld({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": f"{SITE}/{u}"} for i, (n, u) in enumerate(items)
        ],
    })


# ---------- 共通の枠 ----------
def head(title, desc, url, depth, extra=""):
    up = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE}/{url}">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>&#128060;</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@500;700;900&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{up}css/style.css">
<script src="{up}js/phrase.js" defer></script>
<link rel="stylesheet" href="{up}css/bamen.css">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE}/{url}">
{extra}</head>
<body>

{site_header(up, "名場面")}

<main>
"""


def foot(depth):
    up = "../" * depth
    return f"""</main>

{site_footer(up)}
</body>
</html>
"""


def scene_card(s, depth):
    up = "../" * depth
    # 親子の場面は楓浜を先に(表記と月齢をそろえる・2026-11-25)
    ps = sorted(s["pandas"], key=lambda p: p != "楓浜")
    name = "・".join(ps)
    return (
        f'      <a class="video-card bamen-card" href="{up}bamen/{s["id"]}.html">'
        f'<img src="{thumb(s, up)}" alt="" loading="lazy" width="320" height="180">'
        f'<div class="video-body"><h3>{e(s["title"])}</h3>'
        f'<p class="video-meta"><span>{e(date_label(s["date"]))}</span><span>{e(name)} {e(age_label(ps[0], s["date"]))}</span></p>'
        f"</div></a>"
    )


# ---------- ページ ----------
def scene_page(s, scenes, tokushu_of):
    v = main_video(s)
    url = f"bamen/{s['id']}.html"
    first = s["pandas"][0]
    yomi, _, slug = PANDAS[first]
    watch = f"https://www.youtube.com/watch?v={v['id']}&t={int(v['start'])}s"
    embed = f"https://www.youtube.com/embed/{v['id']}?start={int(v['start'])}&rel=0"
    page_title = f"{s['title']}|{month_label(s['date'])} 白浜のパンダ | 和歌ぱんだ"
    tk = tokushu_of.get(s["id"])

    ld = jsonld({
        "@context": "https://schema.org",
        "@type": "VideoObject",
        "name": s["title"],
        "description": s["lead"],
        "thumbnailUrl": thumb_abs(s),
        "uploadDate": v["uploadDate"],
        "embedUrl": embed,
    })
    crumbs = [("トップ", "index.html"), ("名場面", "bamen/")]
    if tk:
        crumbs.append((tk["short"], f"tokushu/{tk['key']}.html"))
    crumbs.append((s["title"], url))
    ld += breadcrumb(crumbs)
    og = f'<meta property="og:image" content="{thumb_abs(s)}">\n'

    crumb_html = '<a href="../bamen/">名場面</a>'
    if tk:
        crumb_html += f' &rsaquo; <a href="../tokushu/{tk["key"]}.html">{e(tk["short"])}</a>'

    panda_links = "・".join(f'<a href="../panda/{PANDAS[p][2]}.html">{e(p)}</a>' for p in s["pandas"])
    facts = [
        ("撮影日", e(date_label(s["date"]))),
        ("個体", panda_links),
        ("年齢", e("・".join(f"{p} {age_label(p, s['date'])}" for p in s["pandas"]) if len(s["pandas"]) > 1 else age_label(first, s["date"]))),
    ]
    if s.get("shiikuin"):
        facts.append(("飼育員さん", "登場します"))
    facts.append(("場面の長さ", e(length_label(v["end"] - v["start"]))))
    facts_html = "".join(f"<li><span>{k}</span>{val}</li>" for k, val in facts)

    others = s["videos"][1:]
    others_html = ""
    if others:
        others_html = "    <p class=\"bamen-source\">この場面は、ほかの動画にも入っています: " + "、".join(
            f'<a href="https://www.youtube.com/watch?v={o["id"]}&t={int(o["start"])}s" target="_blank" rel="noopener">{e(o["title"])}</a>'
            for o in others) + "</p>\n"

    # この場面が出てくる歌(MVは場面ページにしない・公開日を過ぎた歌だけ出す・2026-11-26)
    songs = [g for g in s.get("songs", []) if is_public(g)]
    songs_html = ""
    if songs:
        songs_html = "    <p class=\"bamen-source bamen-song\">&#9835; この場面が出てくる歌: " + "、".join(
            f'<a href="https://www.youtube.com/watch?v={g["id"]}&t={int(g["start"])}s" target="_blank" rel="noopener">{e(g["title"])}</a>'
            for g in songs) + "</p>\n"
    others_html += songs_html

    rel = related_of(s, scenes, tokushu_of)
    rel_html = ""
    if rel:
        rel_html = (
            '  <section class="section section-fur">\n    <div class="section-head"><h2>あわせて見たい場面</h2></div>\n'
            '    <div class="video-grid">\n' + "\n".join(scene_card(r, 1) for r in rel) + "\n    </div>\n  </section>\n"
        )
    photo_html = ""
    if has_photo(s):
        photo_html = (f'    <figure class="bamen-photo"><img src="../img/bamen/{s["id"]}.jpg" alt="{e(s["photoAlt"])}" width="640" height="360" loading="lazy">'
                      f'<figcaption>この場面のひとコマ</figcaption></figure>\n')

    body = f"""  <article class="section bamen">
    <p class="bamen-crumb">{crumb_html}</p>
    <h1 class="bamen-title">{e(s["title"])}</h1>
    <p class="bamen-lead">{e(s["lead"])}</p>
    <div class="bamen-player">
      <iframe src="{embed}" title="{e(v["title"])}" loading="lazy"
        allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
    </div>
    <p class="bamen-start">&#9654; 再生すると、動画の {mmss(v["start"])} からこの場面が始まります。</p>
    <ul class="bamen-facts">{facts_html}</ul>
    <div class="bamen-desc">
{chr(10).join("      <p>" + e(p) + "</p>" for p in s["desc"].split(chr(10)))}
    </div>
{photo_html}    <p class="bamen-actions">
      <a class="btn btn-primary" href="{watch}" target="_blank" rel="noopener">YouTubeでこの場面から見る</a>
      <a class="btn btn-ghost" href="../panda/{slug}.html">{e(first)}({e(yomi)})の動画をもっと見る</a>
    </p>
    <p class="bamen-source">この場面が入っている動画: <a href="https://www.youtube.com/watch?v={v["id"]}" target="_blank" rel="noopener">{e(v["title"])}</a></p>
{others_html}  </article>
{rel_html}"""
    return head(page_title, s["lead"], url, 1, og + ld) + body + foot(1)


def period_text(scenes):
    """特集の場面の撮影期間と年齢の幅(先頭の個体で計算)"""
    ds = sorted(s["date"] for s in scenes)
    p = scenes[0]["pandas"][0]
    a, b = ds[0], ds[-1]
    return f"{month_label(a)}〜{month_label(b)}({age_label(p, a)}〜{age_label(p, b)})"


def tokushu_page(t, by_id):
    url = f"tokushu/{t['key']}.html"
    scenes = [by_id[i] for i in t["scenes"] if i in by_id]
    period = period_text(scenes)
    qa = [{"q": q["q"], "a": q["a"].replace("{期間}", period)} for q in t.get("qa", [])]
    ld = jsonld({
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": t["h1"],
        "itemListElement": [
            {"@type": "ListItem", "position": n + 1, "url": f"{SITE}/bamen/{s['id']}.html", "name": s["title"]}
            for n, s in enumerate(scenes)
        ],
    })
    if qa:
        ld += jsonld({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": q["a"].replace("\n", "")}}
                for q in qa
            ],
        })
    ld += breadcrumb([("トップ", "index.html"), ("名場面", "bamen/"), (t["short"], url)])
    og = f'<meta property="og:image" content="{thumb_abs(scenes[0])}">\n'
    qa_html = "".join(
        f'    <section class="tokushu-qa">\n      <h2>{e(q["q"])}</h2>\n'
        + "".join(f"      <p>{e(p)}</p>\n" for p in q["a"].split("\n"))
        + "    </section>\n"
        for q in qa
    )
    body = f"""  <section class="hero hero-compact">
    <div class="hero-inner">
      <p class="hero-eyebrow">特集・{e(t["eyebrow"])}</p>
      <h1 class="hero-title">{e(t["h1"])}</h1>
      <p class="hero-lead">{e(t["lead"])}</p>
    </div>
  </section>
  <section class="section">
    <div class="section-head"><h2>{e(t["listHeading"])}</h2><p>{len(scenes)}場面・{e(period)}。カードを押すと、その場面から再生できるページが開きます。</p></div>
    <div class="video-grid">
{chr(10).join(scene_card(s, 1) for s in scenes)}
    </div>
  </section>
  <article class="section section-fur tokushu-body">
{qa_html}  </article>
"""
    return head(f"{t['h1']} | 和歌ぱんだ", t["metaDesc"], url, 1, og + ld) + body + foot(1)


def index_page(scenes, tokushu, by_id):
    tk_links = "".join(
        f'      <a class="hamake-card" href="../tokushu/{t["key"]}.html"><span class="hamake-year">特集</span><h3>{e(t["short"])}</h3><p>{e(t["cardText"])}</p></a>\n'
        for t in tokushu
    )
    # 欄の分け方(2026-11-25 えいじさん裁定): 楓浜→良浜ママと楓浜(親子)→ほかの子は生まれた順。場面の多い楓浜を先頭に
    groups = [("fuuhin", "楓浜(ふうひん)の名場面", "楓浜", ["fuuhin"], [x for x in scenes if x["pandas"] == ["楓浜"]])]
    groups.append(("oyako", "良浜(らうひん)ママと楓浜(ふうひん)", "良浜ママと楓浜", ["rauhin", "fuuhin"],
                   [x for x in scenes if set(x["pandas"]) == {"良浜", "楓浜"}]))
    for name in PANDAS:
        if name == "楓浜":
            continue
        g = [x for x in scenes if x["pandas"] == [name]]
        groups.append((PANDAS[name][2], f"{name}({PANDAS[name][0]})の名場面", name, [PANDAS[name][2]], g))
    placed = sum(len(g[4]) for g in groups)
    assert placed == len(scenes), f"欄に入らない場面がある: {placed}/{len(scenes)}"
    groups = [g for g in groups if g[4]]
    jump = "".join(
        f'      <a class="bamen-jump-btn" href="#{key}"><span class="bamen-jump-faces">'
        + "".join(f'<img src="../img/top/peek/{f}.jpg" alt="" width="44" height="44">' for f in faces)
        + f'</span><span class="bamen-jump-name">{e(label)}</span><span class="bamen-jump-count">{len(g)}場面</span></a>\n'
        for key, _, label, faces, g in groups
    )
    sections = ""
    for key, title, _, _, g in groups:
        g = sorted(g, key=lambda x: (x["date"], x["id"]))
        years = sorted({x["date"][:4] for x in g})
        inner = ""
        for y in years:
            gy = [x for x in g if x["date"][:4] == y]
            if len(years) > 1:
                inner += f'    <h3 class="bamen-year">{y}年<small>{len(gy)}場面</small></h3>\n'
            inner += '    <div class="video-grid">\n' + "\n".join(scene_card(x, 1) for x in gy) + "\n    </div>\n"
        sections += (
            f'  <section class="section section-fur bamen-group" id="{key}">\n    <div class="section-head"><h2>{e(title)}</h2><p>{len(g)}場面・撮影日の古い順。</p></div>\n'
            + inner + "  </section>\n"
        )
    og = f'<meta property="og:image" content="{thumb_abs(scenes[0])}">\n'
    ld = breadcrumb([("トップ", "index.html"), ("名場面", "bamen/")])
    body = f"""  <section class="hero hero-compact">
    <div class="hero-inner">
      <p class="hero-eyebrow">名場面</p>
      <h1 class="hero-title">白浜のパンダ 浜家の名場面</h1>
      <p class="hero-lead">YouTubeで公開した動画から、1場面ずつ取り出しました。押すと、その場面の秒から再生できます。</p>
    </div>
  </section>
  <nav class="section bamen-jump" aria-label="パンダで選ぶ">
    <p class="bamen-jump-title">パンダで選ぶ</p>
    <div class="bamen-jump-list">
{jump}    </div>
  </nav>
  <section class="section">
    <div class="section-head"><h2>特集</h2></div>
    <div class="hamake-grid">
{tk_links}    </div>
  </section>
{sections}"""
    return head("白浜のパンダ 浜家の名場面 | 和歌ぱんだ", "和歌山・白浜で撮った浜家のパンダの名場面を、1場面ずつその秒から見られるページです。", "bamen/", 1, og + ld) + body + foot(1)


def sitemap():
    pages = sorted(p.relative_to(BASE).as_posix() for p in BASE.rglob("*.html")
                   if not any(part.startswith((".", "_")) for part in p.relative_to(BASE).parts))
    today = dt.date.today().isoformat()
    urls = []
    for p in pages:
        loc = f"{SITE}/" if p == "index.html" else f"{SITE}/{p[:-len('index.html')]}" if p.endswith("/index.html") else f"{SITE}/{p}"
        urls.append(f"  <url><loc>{loc}</loc><lastmod>{today}</lastmod></url>")
    (BASE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls) + "\n</urlset>\n", encoding="utf-8")
    return len(urls)


def main():
    scenes = json.loads(BAMEN.read_text(encoding="utf-8"))
    tokushu = json.loads(TOKUSHU.read_text(encoding="utf-8"))
    for s in scenes:  # 確定していない個体名は載せない
        for p in s["pandas"]:
            assert p in PANDAS, f"{s['id']}: 個体名が確定していない → {p}"
    ids = [s["id"] for s in scenes]
    assert len(ids) == len(set(ids)), "場面IDが重複している"
    by_id = {s["id"]: s for s in scenes}
    tokushu_of = {}
    for t in tokushu:
        for i in t["scenes"]:
            tokushu_of.setdefault(i, t)
    (BASE / "bamen").mkdir(exist_ok=True)
    (BASE / "tokushu").mkdir(exist_ok=True)
    for s in scenes:
        (BASE / "bamen" / f"{s['id']}.html").write_text(scene_page(s, scenes, tokushu_of), encoding="utf-8")
    for t in tokushu:
        (BASE / "tokushu" / f"{t['key']}.html").write_text(tokushu_page(t, by_id), encoding="utf-8")
    (BASE / "bamen" / "index.html").write_text(index_page(scenes, tokushu, by_id), encoding="utf-8")
    n = sitemap()
    print(f"場面ページ {len(scenes)}枚・特集 {len(tokushu)}本・一覧1枚・sitemap {n}件を出力")


if __name__ == "__main__":
    main()
