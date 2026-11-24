/* 日本語を「文節」の切れ目でだけ改行させる(「名場/面」のような泣き別れを防ぐ)
   ブラウザの単語分け(Intl.Segmenter・Safari/Chromeとも対応)で言葉に分け、
   助詞・送りがな・句読点は前の言葉にくっつけて、ひとまとまりごとに折り返し禁止の印をつける。
   見出し・短い文・ボタンなどだけに使う(長い本文はふつうの折り返しのまま)。 */
(function () {
  "use strict";
  if (!window.Intl || !Intl.Segmenter) return;

  var seg = new Intl.Segmenter("ja", { granularity: "word" });
  var SELECTOR = "h1,h2,h3,h4,h5,p,li,dt,dd,figcaption,th,td,button,a,small,time,label";
  var MAX_TEXT = 120;   // これより長い本文はそのまま
  var MAX_CHUNK = 14;   // これより長いまとまりは折り返し禁止にしない(はみ出し防止)

  // 文字の種類(正規表現は \u 表記で書く)
  var HIRA = "\\u3041-\\u3096";
  var KATA = "\\u30a1-\\u30fa\\u30fc";
  var KANJI = "\\u3400-\\u9fff\\u3005";
  var PUNCT = "\\u3001\\u3002\\uff0c\\uff0e,.\\u30fb\\uff01\\uff1f!?\\u300d\\u300f\\uff09)\\]\\u3011\\u3009\\u300b\\u2026\\u2025\\u301c\\uff5e";
  var ATTACH = new RegExp("^[" + HIRA + "\\u30fc" + PUNCT + "]+$");     // 助詞・送りがな・句読点・閉じかっこ
  var OPEN = new RegExp("[\\u300c\\u300e\\uff08(\\[\\u3010\\u3008\\u300a]$"); // 開きかっこ(次の言葉にくっつける)
  var JA = new RegExp("[" + HIRA + KATA + KANJI + "]");
  var KANJI_END = new RegExp("[" + KANJI + "]$"), KANJI_START = new RegExp("^[" + KANJI + "]");
  var KATA_END = new RegExp("[" + KATA + "]$"), KATA_START = new RegExp("^[" + KATA + "]");
  var DIGIT_END = /[0-9０-９,]$/, NUM_OR_KANJI_START = new RegExp("^[0-9" + KANJI + "]");
  var PAREN_START = /^[（(]/;

  // 前のまとまりにつなげるか
  function joins(cur, p) {
    if (ATTACH.test(p)) return true;                                // 助詞・送りがな・句読点
    if (PAREN_START.test(p)) return true;                           // 楓浜(ふうひん) の読みがな
    if (KANJI_END.test(cur) && KANJI_START.test(p)) return true;    // 漢字どうし(名前・熟語)
    if (KATA_END.test(cur) && KATA_START.test(p)) return true;      // カタカナどうし
    if (DIGIT_END.test(cur) && NUM_OR_KANJI_START.test(p)) return true; // 2020年・1,936本
    return false;
  }

  function chunks(text) {
    var out = [], cur = "", prevOpen = false;
    var parts = Array.from(seg.segment(text), function (s) { return s.segment; });
    for (var i = 0; i < parts.length; i++) {
      var p = parts[i];
      if (/^\s+$/.test(p)) { if (cur) out.push(cur); out.push(p); cur = ""; prevOpen = false; continue; }
      // 「お池」「ご案内」の お・ご は次の言葉の頭につける
      var honor = (p === "\u304a" || p === "\u3054") && i + 1 < parts.length && KANJI_START.test(parts[i + 1]);
      if (cur && (honor || (!prevOpen && !joins(cur, p)))) { out.push(cur); cur = ""; }
      if (honor) { cur = p; prevOpen = true; continue; }
      cur += p;
      prevOpen = OPEN.test(p) || PAREN_START.test(p) && p.length === 1;
    }
    if (cur) out.push(cur);
    return out;
  }

  function wrapNode(node) {
    var text = node.nodeValue;
    if (!JA.test(text) || text.trim().length < 2) return;
    // 横並び(flex/grid)の箱の中では、分けた言葉が1つずつ離れて並んでしまうので触らない
    var disp = getComputedStyle(node.parentElement).display;
    if (/flex|grid/.test(disp)) return;
    var list = chunks(text);
    if (list.length < 2) return;
    var frag = document.createDocumentFragment();
    list.forEach(function (c, i) {
      if (/^\s+$/.test(c) || c.length > MAX_CHUNK) {
        frag.appendChild(document.createTextNode(c));
      } else {
        // 専用の名前(w-ph)にして、ほかのCSS(「li span」など)が当たらないようにする
        var sp = document.createElement("w-ph");
        sp.textContent = c;
        frag.appendChild(sp);
      }
      if (i < list.length - 1) frag.appendChild(document.createElement("wbr"));
    });
    node.parentNode.replaceChild(frag, node);
  }

  function run(root) {
    var els = (root || document).querySelectorAll(SELECTOR);
    for (var i = 0; i < els.length; i++) {
      var el = els[i];
      if (el.dataset.ph || el.closest("script,style,noscript,textarea,.no-ph")) continue;
      if ((el.textContent || "").length > MAX_TEXT) continue;
      el.dataset.ph = "1";
      var walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null);
      var nodes = [], n;
      // 内側にさらに対象の要素があるときは、その中の文字はそちらに任せる
      while ((n = walker.nextNode())) if (n.parentElement.closest(SELECTOR) === el) nodes.push(n);
      nodes.forEach(wrapNode);
    }
  }

  window.wakapandaPhrase = run;   // あとから差し込む部分(最新動画など)にも使える
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", function () { run(); });
  else run();
})();
