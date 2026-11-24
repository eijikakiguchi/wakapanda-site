#!/usr/bin/env python3
"""全ページの CSS・JS の読み込みに、中身から作った版番号(?v=xxxxxxxx)を付ける。

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

        new = REF.sub(repl, text)
        if new != text:
            html.write_text(new, encoding="utf-8")
            changed += 1
    print(f"版番号を付けたページ: {changed}")


if __name__ == "__main__":
    main()
