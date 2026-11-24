#!/usr/bin/env python3
"""トップの「楓浜の顔のモザイク」を作る。

公開済み動画のサムネ(i.ytimg.com の mqdefault)を正方形に切って小さくし、
楓浜の顔の写真の明るさ・色に合わせて並べ替えた1枚の画像(並べ終わりの姿)を作る。
ページ側(js/top.js)はこの画像を1マスずつ切り出して飛ばし、最後に顔の写真を薄く重ねる。

使い方:
  python3 scripts/build_top_mosaic.py <サムネのフォルダ> <顔の元画像>
出力:
  img/top/mosaic.webp … 並べ終わりのモザイク(COLS x ROWS マス)
  img/top/face.webp   … 重ねる顔の写真(半分の大きさ・ページで引きのばす)
  data/mosaic.json   … マスの数と、各マスの動画ID(クリックでその動画へ)
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance
from scipy.optimize import linear_sum_assignment

ROOT = Path(__file__).resolve().parent.parent
COLS = ROWS = 44          # 1,936マス(公開動画1,967本からいちばん合う1,936本)
TILE = 28                 # 1マスの画素
FACE_BOX = (740, 90, 1080, 430)  # 顔の元画像(1280x720)から切る範囲


def tile_of(path):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    s = min(w, h)
    # 上下の黒帯や文字を避けて、真ん中の正方形
    im = im.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2))
    return im.resize((TILE, TILE), Image.LANCZOS)


def main():
    thumbs_dir = Path(sys.argv[1])
    face_src = Path(sys.argv[2])
    # 2020-02-11より前は家族の記録なので使わない(撮影日なしの動画はそのまま使う)
    ids = [v["id"] for v in json.load(open(ROOT / "data/archive.json", encoding="utf-8"))
           if not (v.get("shootDate") and v["shootDate"] < "2020-02-11")]

    tiles, means, used_ids = [], [], []
    for vid in ids:
        p = thumbs_dir / f"{vid}.jpg"
        if not p.exists():
            continue
        t = tile_of(p)
        tiles.append(t)
        means.append(np.asarray(t, dtype=np.float32).reshape(-1, 3).mean(0))
        used_ids.append(vid)
    means = np.array(means)

    face = Image.open(face_src).convert("RGB").crop(FACE_BOX)
    face = ImageEnhance.Contrast(face).enhance(1.25)
    target = np.asarray(face.resize((COLS, ROWS), Image.LANCZOS), dtype=np.float32).reshape(-1, 3)

    # 明るさを重めに見た色の差(顔は白黒なので明るさが大事)
    def lum(a):
        return a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)

    # サムネ全体の明るさの幅を、顔の明るさの幅に合わせてから比べる
    tl, ml = lum(target), lum(means)
    ml_n = (ml - ml.mean()) / (ml.std() + 1e-6) * tl.std() + tl.mean()
    cost = 3.0 * (tl[:, None] - ml_n[None, :]) ** 2
    cost += 0.15 * ((target[:, None, :] - means[None, :, :]) ** 2).sum(-1)
    rows, cols = linear_sum_assignment(cost)

    mosaic = Image.new("RGB", (COLS * TILE, ROWS * TILE))
    order = [None] * (COLS * ROWS)
    for cell, k in zip(rows, cols):
        x, y = cell % COLS, cell // COLS
        mosaic.paste(tiles[k], (x * TILE, y * TILE))
        order[cell] = used_ids[k]

    out = ROOT / "img/top"
    out.mkdir(parents=True, exist_ok=True)
    mosaic.save(out / "mosaic.webp", quality=58, method=6)
    # 顔は薄く重ねるだけなので半分の大きさで十分
    face.resize((COLS * TILE // 2, ROWS * TILE // 2), Image.LANCZOS).save(out / "face.webp", quality=72, method=6)
    json.dump({"cols": COLS, "rows": ROWS, "tile": TILE, "ids": order},
              open(ROOT / "data/mosaic.json", "w", encoding="utf-8"), separators=(",", ":"))
    print("マス", COLS * ROWS, "/ サムネ", len(used_ids))


if __name__ == "__main__":
    main()
