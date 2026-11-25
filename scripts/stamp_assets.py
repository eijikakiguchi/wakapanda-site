#!/usr/bin/env python3
"""全ページの仕上げ: ①CSS・JS の読み込みに版番号(?v=xxxxxxxx)を付ける ②GA4のタグを入れる。

2026-11-25 ②追加: アクセス解析(GA4・測定ID G-XVNDLS1TKE)。build_*.py でページを作り直しても、
  ここで必ず </head> の前に入るので入れ忘れがない(入っているページには何もしない)。

2026-11-25 追加: GitHub Pages は CSS・JS をスマホに10分ほど覚えさせるので、
  push の直後は「ページは新しいのに見た目とプログラムは古い」状態になり、
  ロゴの右のアイコンが下に落ちる・オープニングが出ない、が起きた。
  中身が変わったときだけ番号が変わるので、毎回すぐ新しいものが読まれる。

build_*.py でページを作り直したあとに実行する(update_archive.py は最後に自動で実行)。
"""
import hashlib
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "_旧版", "data", "scripts", "img", "node_modules"}
REF = re.compile(r'((?:href|src)=")((?:\.\./)*(?:css|js)/[\w.-]+\.(?:css|js))(?:\?v=[0-9a-f]+)?(")')


GA_ID = "G-XVNDLS1TKE"
GA_TAG = (
    "<!-- Google アナリティクス(運営ポリシー参照) -->\n"
    f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>\n'
    "<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}"
    f"gtag('js',new Date());gtag('config','{GA_ID}');</script>\n"
)


def add_ga(text: str) -> str:
    if GA_ID in text or "</head>" not in text:
        return text
    return text.replace("</head>", GA_TAG + "</head>", 1)


def file_hash(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()[:8]


def main() -> None:
    changed = 0
    for html in BASE.rglob("*.html"):
        if any(part in SKIP_DIRS for part in html.relative_to(BASE).parts):
            continue
        text = html.read_text(encoding="utf-8")

        def repl(m):
            target = (html.parent / m.group(2)).resolve()
            if not target.exists():
                return m.group(0)
            return f"{m.group(1)}{m.group(2)}?v={file_hash(target)}{m.group(3)}"

        new = add_ga(REF.sub(repl, text))
        if new != text:
            html.write_text(new, encoding="utf-8")
            changed += 1
    print(f"仕上げ(版番号・GA4)で書きかえたページ: {changed}")


if __name__ == "__main__":
    main()
