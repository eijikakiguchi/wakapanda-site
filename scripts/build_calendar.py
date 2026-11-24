#!/usr/bin/env python3
"""
data/archive.json から記念日カレンダー(kinenbi-calendar.html)を生成する。

「今日は◯年前のあの日」のための再訪装置。撮影日(なければ公開日)の月日で束ね、
1日1本(いちばん再生された動画)を代表として並べる。JSで「今日」をハイライトする。
"""
import html
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from site_parts import site_header, site_footer, stamp
from collections import defaultdict

BASE = Path(__file__).parent.parent
ARCHIVE = BASE / "data" / "archive.json"
LAST_DAY = "2025-06-28"  # 楓浜・良浜・結浜・彩浜が中国へ帰った日
OUT = BASE / "kinenbi-calendar.html"

MONTH_NAMES = [f"{m}月" for m in range(1, 13)]

HEAD = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>記念日カレンダー | 浜家の思い出、ぜんぶここに。</title>
<meta name="description" content="「今日は何年前のこの日」浜家の動画を、月日ごとに振り返るカレンダーです。撮影日つきで{days}日ぶん収録。">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>&#128060;</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@500;700;900&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/style.css">
<script src="js/phrase.js" defer></script>
<meta property="og:title" content="記念日カレンダー | 浜家の思い出、ぜんぶここに。">
<meta property="og:description" content="今日は何年前のこの日。浜家の動画を月日ごとに振り返ります。">
<meta property="og:type" content="website">
<meta property="og:url" content="https://wakapanda.com/kinenbi-calendar.html">
<meta property="og:image" content="https://wakapanda.com/img/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="https://wakapanda.com/kinenbi-calendar.html">
</head>
<body>

{site_header_html}

<main>
  <section class="hero hero-compact">
    <div class="hero-inner">
      <p class="hero-eyebrow">今日は何の日</p>
      <h1 class="hero-title">記念日<br><em>カレンダー</em></h1>
      <p class="hero-lead">
        「今日は何年前のこの日」。撮影日(なければ公開日)を頼りに、365日ぶん束ねました。
        {days}日ぶん、浜家のその日があります。
      </p>
    </div>
  </section>

  <p class="today-banner" id="today-banner" hidden>
    今日は <span id="today-label"></span> の日。<a href="#" id="today-link">その日の思い出を見る &darr;</a>
  </p>

  <nav class="month-nav" aria-label="月へジャンプ">
{month_pills}
  </nav>

  <div class="section">
{months}
  </div>
</main>

{site_footer_html}

<script>
(function () {{
  var now = new Date();
  var mm = String(now.getMonth() + 1).padStart(2, "0");
  var dd = String(now.getDate()).padStart(2, "0");
  var id = "d-" + mm + "-" + dd;
  var target = document.getElementById(id);
  if (!target) return;
  target.classList.add("is-today");
  var banner = document.getElementById("today-banner");
  var label = document.getElementById("today-label");
  var link = document.getElementById("today-link");
  label.textContent = mm + "月" + dd + "日";
  link.setAttribute("href", "#" + id);
  banner.hidden = false;
}})();
</script>
</body>
</html>
"""

MONTH_TMPL = """    <section class="calendar-month" id="m{month:02d}">
      <div class="section-head">
        <h2>{month}月</h2>
      </div>
      <div class="calendar-list">
{days}
      </div>
    </section>
"""


def format_views(n):
    if n >= 10000:
        return f"{round(n / 10000)}万回"
    return f"{n}回"


def day_html(mm, dd, videos):
    # 代表は「撮影日つき」を先に・その中で再生回数の多い順(2026-11-25 Fable検品)
    videos = sorted(videos, key=lambda v: (0 if v["shootDate"] else 1, -v["views"]))
    top = videos[0]
    date_str = top["shootDate"] or top["publishDate"]
    year = date_str[:4]
    title = html.escape(top["title"])
    others = f"ほか{len(videos) - 1}本" if len(videos) > 1 else ""
    return (
        f'        <a class="calendar-day" id="d-{mm}-{dd}" href="https://www.youtube.com/watch?v={top["id"]}" target="_blank" rel="noopener">'
        f'<span class="cal-date">{int(mm)}/{int(dd)}</span>'
        f'<img src="https://i.ytimg.com/vi/{top["id"]}/hqdefault.jpg" alt="" loading="lazy" width="112" height="63">'
        f'<span class="cal-body"><h3>{year}年 &mdash; {title}</h3>'
        f'<span class="cal-meta">{format_views(top["views"])}{("・" + others) if others else ""}</span></span>'
        f'</a>'
    )


def main():
    archive = json.loads(ARCHIVE.read_text(encoding="utf-8"))
    by_day = defaultdict(list)
    for v in archive:
        d = v["shootDate"] or v["publishDate"]
        if not d:
            continue
        # 撮影日がなく、帰国(2025-06-28)より後に公開した動画は「その日」が分からないので入れない
        if not v["shootDate"] and d > LAST_DAY:
            continue
        by_day[d[5:7] + "-" + d[8:10]].append(v)

    month_pills = "\n".join(
        f'    <a href="#m{m:02d}">{m}月</a>' for m in range(1, 13)
    )

    months_html = []
    for m in range(1, 13):
        days_in_month = sorted(
            (k for k in by_day if k[:2] == f"{m:02d}"), key=lambda k: k
        )
        if not days_in_month:
            continue
        day_rows = "\n".join(
            day_html(k[:2], k[3:5], by_day[k]) for k in days_in_month
        )
        months_html.append(MONTH_TMPL.format(month=m, days=day_rows))
        print(f"{m}月: {len(days_in_month)}日")

    out_html = HEAD.format(site_header_html=site_header("", "記念日カレンダー"), site_footer_html=site_footer(""), month_pills=month_pills, months="\n".join(months_html), days=len(by_day))
    OUT.write_text(out_html, encoding="utf-8")
    print(f"出力: {OUT} / 収録日数: {len(by_day)}")


if __name__ == "__main__":
    main()
