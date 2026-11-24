"""全ページ共通のヘッダー・フッター(2026-11-24 紙の雰囲気にそろえる)。

トップ(index.html)と同じメニューを、下層ページでも同じ形で出す。
使い方: from site_parts import site_header, site_footer
    up = "" (ルート直下のページ) / "../" (panda/・bamen/・tokushu/ の中)
    current = いま開いているページのメニュー名(aria-current を付ける。無ければ "")
"""

YOUTUBE = "https://www.youtube.com/channel/UCfALH0tKUgs-XsL-Xhwvj6A"

# (表示名, ルートからのパス)
MENU = [
    ("名場面", "bamen/"),
    ("年表", "index.html#nenpyo"),
    ("個体別アルバム", "index.html#album"),
    ("テーマ別に見る", "meiba-shu.html"),
    ("楓浜ものがたり", "fuuhin-monogatari.html"),
    ("記念日カレンダー", "kinenbi-calendar.html"),
    ("このサイトについて", "about.html"),
]


def site_header(up: str = "", current: str = "") -> str:
    links = []
    for name, path in MENU:
        cur = ' aria-current="page"' if name == current else ""
        links.append(f'    <a href="{up}{path}"{cur}>{name}</a>')
    nav = "\n".join(links)
    return f"""<noscript><style>.site-nav{{display:flex !important;position:static !important;box-shadow:none !important;flex-wrap:wrap}}.menu-btn{{display:none !important}}.site-header{{flex-wrap:wrap}}</style></noscript>
<header class="site-header">
  <div class="brand-wrap"><a class="brand" href="{up}index.html">和歌ぱんだ</a><a class="yt-link" href="{YOUTUBE}" target="_blank" rel="noopener" aria-label="YouTubeチャンネル(新しいタブで開きます)"><svg viewBox="0 0 28 20" width="30" height="21" aria-hidden="true"><rect width="28" height="20" rx="5" fill="#FF0000"/><path d="M11.2 5.6v8.8l7.6-4.4z" fill="#fff"/></svg></a></div>
  <button class="menu-btn" id="menu-btn" type="button" aria-expanded="false" aria-controls="site-nav">メニュー</button>
  <nav class="site-nav" id="site-nav" aria-label="サイトのメニュー">
{nav}
  </nav>
</header>"""


def site_footer(up: str = "") -> str:
    return f"""<footer class="site-footer">
  <p class="footer-brand">和歌ぱんだ wakapanda.com</p>
  <nav aria-label="フッターメニュー">
    <a href="{up}about.html">このサイトについて</a>
    <a href="{up}policy.html">運営ポリシー</a>
    <a href="{YOUTUBE}" target="_blank" rel="noopener">YouTube</a>
  </nav>
  <p class="footer-copy">© 和歌ぱんだ — 掲載の映像・写真はすべて運営者が撮影したものです。</p>
</footer>
<script src="{up}js/site.js" defer></script>"""


def stamp(up: str, slug: str, name: str = "") -> str:
    """個体の丸写真を切手にした飾り(トップの手紙と同じ部品)。"""
    cap = f'<span class="stamp-name">{name}</span>' if name else ""
    return (f'<div class="hero-stamp" aria-hidden="true"><span class="stamp">'
            f'<img src="{up}img/top/peek/{slug}.jpg" alt="" width="360" height="360"></span>{cap}</div>')
