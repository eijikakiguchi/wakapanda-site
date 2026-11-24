/* 和歌ぱんだ トップ(見本)
   1) 読み込み中のパンダ → 2) サムネ1,936枚が舞って楓浜の顔のモザイクに → 3) 手紙の7頭がのぞく → 4) 年表の年えらび */
(function () {
  "use strict";

  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const hero = document.querySelector(".hero");
  const canvas = document.getElementById("mosaic");
  const ctx = canvas.getContext("2d");
  const loader = document.getElementById("loader");
  const copy = document.querySelector(".hero-copy");

  const loadImg = (src) => new Promise((ok, ng) => {
    const im = new Image();
    im.onload = () => ok(im);
    im.onerror = ng;
    im.src = src;
  });

  let data, mosaic, face;
  let tiles = [];
  let layout = null;
  let t0 = 0, done = false, skipAt = null;
  const FACE_ALPHA = 0.45;

  function measure() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = hero.clientWidth, h = hero.clientHeight;
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const top = 70;
    const copyH = copy.offsetHeight + 124;  // 文字の高さ+下の余白(「下へ」の分)
    const S = Math.max(180, Math.min(w - 32, h - top - copyH, 640));
    const x0 = (w - S) / 2;
    const y0 = top + Math.max(0, (h - top - copyH - S) / 2);
    layout = { w, h, S, x0, y0, cell: S / data.cols };
  }

  function makeTiles() {
    const n = data.cols * data.rows;
    tiles = new Array(n);
    for (let i = 0; i < n; i++) {
      const c = i % data.cols, r = (i / data.cols) | 0;
      // 外側から中心へ、少しずつ集まる(中心からの距離で順番に少しばらつき)
      const dx = c / data.cols - 0.5, dy = r / data.rows - 0.5;
      const dist = Math.sqrt(dx * dx + dy * dy);
      tiles[i] = {
        c, r,
        sx: Math.random() * 1.3 - 0.15,     // はじめの位置(画面の割合)
        sy: Math.random() * 1.3 - 0.15,
        sc: 1.8 + Math.random() * 2.6,      // はじめの大きさ(マスの何倍)
        rot: (Math.random() - 0.5) * 0.9,
        ph: Math.random() * Math.PI * 2,
        delay: 0.5 + dist * 1.9 + Math.random() * 0.9,
        dur: 1.1 + Math.random() * 0.5,
      };
    }
  }

  const easeOut = (p) => 1 - Math.pow(1 - p, 3);
  const lastLand = () => tiles.reduce((m, t) => Math.max(m, t.delay + t.dur), 0);

  function drawFinal(alpha) {
    const { S, x0, y0 } = layout;
    ctx.drawImage(mosaic, x0, y0, S, S);
    if (alpha > 0) {
      ctx.globalAlpha = alpha;
      ctx.drawImage(face, x0, y0, S, S);
      ctx.globalAlpha = 1;
    }
  }

  function frame(now) {
    if (done) return;
    let t = (now - t0) / 1000;
    const end = lastLand();
    if (skipAt !== null) t = end + 1.2;
    const { w, h, x0, y0, cell } = layout;
    ctx.clearRect(0, 0, w, h);
    const src = data.tile;

    if (t < end) {
      // 着地したマス → 飛んでいるマスの順で描く
      const flying = [];
      for (const k of tiles) {
        const p = (t - k.delay) / k.dur;
        if (p >= 1) {
          ctx.drawImage(mosaic, k.c * src, k.r * src, src, src, x0 + k.c * cell, y0 + k.r * cell, cell + 0.5, cell + 0.5);
        } else {
          flying.push([k, Math.max(0, p)]);
        }
      }
      for (const [k, p0] of flying) {
        const p = easeOut(p0);
        const drift = (1 - p0) * 10;
        const sxp = k.sx * w + Math.sin(t * 0.9 + k.ph) * drift;
        const syp = k.sy * h + Math.cos(t * 0.7 + k.ph) * drift;
        const tx = x0 + k.c * cell, ty = y0 + k.r * cell;
        const size = cell * (k.sc + (1 - k.sc) * p);
        const x = sxp + (tx - sxp) * p, y = syp + (ty - syp) * p;
        const rot = k.rot * (1 - p);
        ctx.save();
        ctx.translate(x + size / 2, y + size / 2);
        if (rot) ctx.rotate(rot);
        if (p < 0.9) {
          const b = Math.max(1, size * 0.06);
          ctx.fillStyle = "#FAF6EE";
          ctx.fillRect(-size / 2 - b, -size / 2 - b, size + b * 2, size + b * 2);
        }
        ctx.drawImage(mosaic, k.c * src, k.r * src, src, src, -size / 2, -size / 2, size, size);
        ctx.restore();
      }
      requestAnimationFrame(frame);
      return;
    }

    // ぜんぶ並んだら、楓浜の顔をうっすら重ねる
    const a = Math.min(1, (t - end) / 1.0) * FACE_ALPHA;
    drawFinal(a);
    if (a >= FACE_ALPHA) {
      finish();
    } else {
      requestAnimationFrame(frame);
    }
  }

  function finish() {
    done = true;
    hero.classList.add("is-done");
    canvas.classList.add("is-clickable");
    render();
  }

  function render() {
    measure();
    ctx.clearRect(0, 0, layout.w, layout.h);
    drawFinal(FACE_ALPHA);
  }

  // マスを押すと、そのサムネイルの吹き出し → そこからYouTubeへ
  const pop = document.createElement("div");
  pop.className = "tile-pop";
  pop.hidden = true;
  pop.innerHTML = '<button type="button" aria-label="とじる">×</button><img alt="" width="320" height="180"><a target="_blank" rel="noopener">YouTubeでこの動画を見る</a>';
  hero.appendChild(pop);
  pop.querySelector("button").addEventListener("click", () => { pop.hidden = true; });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") pop.hidden = true; });

  function cellAt(ev) {
    if (!done) return -1;
    const rect = canvas.getBoundingClientRect();
    const x = ev.clientX - rect.left - layout.x0, y = ev.clientY - rect.top - layout.y0;
    if (x < 0 || y < 0 || x >= layout.S || y >= layout.S) return -1;
    return ((y / layout.cell) | 0) * data.cols + ((x / layout.cell) | 0);
  }
  canvas.addEventListener("click", (ev) => {
    const i = cellAt(ev);
    if (i < 0 || !data.ids[i]) { pop.hidden = true; return; }
    const id = data.ids[i];
    const c = i % data.cols, r = (i / data.cols) | 0;
    pop.querySelector("img").src = "https://i.ytimg.com/vi/" + id + "/mqdefault.jpg";
    pop.querySelector("a").href = "https://www.youtube.com/watch?v=" + id;
    const half = 120;
    const x = Math.min(Math.max(layout.x0 + (c + 0.5) * layout.cell, half), layout.w - half);
    const y = layout.y0 + r * layout.cell;
    pop.style.left = x + "px";
    pop.style.top = (y < 240 ? y + layout.cell + 190 : y) + "px";
    pop.hidden = false;
    pop.querySelector("a").focus({ preventScroll: true });
  });
  canvas.addEventListener("mousemove", (ev) => {
    canvas.style.cursor = cellAt(ev) >= 0 ? "pointer" : "default";
  });

  document.getElementById("skip").addEventListener("click", () => { skipAt = performance.now(); });

  let resizeTimer;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => { if (!data) return; pop.hidden = true; if (done) render(); else measure(); }, 120);
  });

  const minWait = new Promise((ok) => setTimeout(ok, 900));
  Promise.all([
    fetch("data/mosaic.json").then((r) => r.json()),
    loadImg("img/top/mosaic.webp"),
    loadImg("img/top/face.webp"),
    minWait,
  ]).then(([d, m, f]) => {
    data = d; mosaic = m; face = f;
    measure();
    makeTiles();
    loader.classList.add("is-done");
    // 文字(Webフォント)が入ったら、大きさを測り直す
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => { if (done) render(); else measure(); });
    // オープニングは「視差効果を減らす」の人にも同じものを出す(2026-11-25 えいじさん裁定・SKIPで飛ばせる)
    t0 = performance.now();
    requestAnimationFrame(frame);
  }).catch(() => {
    // 読み込めなくても文字は見えるように
    loader.classList.add("is-done");
    hero.classList.add("is-done");
  });

  // ヘッダー: 少し下がったら紙の帯をつける
  const header = document.querySelector(".site-header");
  const onScroll = () => header.classList.toggle("is-scrolled", window.scrollY > 40);
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // スマホのメニュー
  const menuBtn = document.getElementById("menu-btn");
  const nav = document.getElementById("site-nav");
  menuBtn.addEventListener("click", () => {
    const open = nav.classList.toggle("is-open");
    menuBtn.setAttribute("aria-expanded", String(open));
  });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && nav.classList.contains("is-open")) { nav.classList.remove("is-open"); menuBtn.setAttribute("aria-expanded", "false"); menuBtn.focus(); } });
  nav.addEventListener("click", (e) => { if (e.target.closest("a")) { nav.classList.remove("is-open"); menuBtn.setAttribute("aria-expanded", "false"); } });

  // 手紙: 7頭の切手が順番に貼られる
  const peek = document.querySelector(".stamps");
  if ("IntersectionObserver" in window && !reduce) {
    new IntersectionObserver((es, ob) => {
      es.forEach((e) => { if (e.isIntersecting) { peek.classList.add("is-in"); ob.disconnect(); } });
    }, { threshold: 0.35 }).observe(peek);
  } else {
    peek.classList.add("is-in");
  }

  // 年表: いま見ている年に印
  const links = [...document.querySelectorAll(".year-nav a")];
  const years = [...document.querySelectorAll(".year")];
  if ("IntersectionObserver" in window) {
    const ob = new IntersectionObserver((es) => {
      es.forEach((e) => {
        if (e.isIntersecting) {
          links.forEach((a) => a.classList.toggle("is-current", a.dataset.year === e.target.dataset.year));
        }
      });
    }, { rootMargin: "-40% 0px -55% 0px" });
    years.forEach((y) => ob.observe(y));
  }
  // 新しい動画: 横の動画を新しい順に6本(足りなければショートで埋める)
  const shinsaku = document.getElementById("shinsaku-list");
  if (shinsaku) {
    fetch("data/videos.json").then((r) => r.json()).then((list) => {
      const longs = list.filter((v) => !v.short);
      const picks = longs.concat(list.filter((v) => v.short)).slice(0, 6);
      if (picks.length === 0) throw new Error("empty");
      picks.forEach((v) => {
        const li = document.createElement("li");
        const a = document.createElement("a");
        a.className = "shinsaku-card";
        a.href = (v.short ? "https://www.youtube.com/shorts/" : "https://www.youtube.com/watch?v=") + encodeURIComponent(v.id);
        a.target = "_blank"; a.rel = "noopener";
        const img = document.createElement("img");
        img.src = "https://i.ytimg.com/vi/" + encodeURIComponent(v.id) + "/hqdefault.jpg";
        img.alt = ""; img.loading = "lazy"; img.width = 480; img.height = 360;
        const h = document.createElement("h3"); h.textContent = v.title;
        const time = document.createElement("time"); time.dateTime = v.published; time.textContent = v.published.replace(/-/g, "/");
        a.append(img, h, time); li.append(a); shinsaku.append(li);
      });
    }).catch(() => {
      shinsaku.insertAdjacentHTML("afterend", '<p class="shinsaku-lead">動画の一覧を読み込めませんでした。YouTubeチャンネルから直接ご覧ください。</p>');
    });
  }
})();
