// 和歌ぱんだ — data/ のJSONを読み込んで一覧を描画する
(function () {
  "use strict";

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === "text") node.textContent = attrs[k];
      else node.setAttribute(k, attrs[k]);
    });
    (children || []).forEach(function (c) { node.appendChild(c); });
    return node;
  }

  // ---- 最新動画 ----
  var videoGrid = document.getElementById("video-grid");
  if (videoGrid) {
    fetch("data/videos.json")
      .then(function (res) { return res.json(); })
      .then(function (videos) {
        videos.slice(0, 8).forEach(function (v) {
          var card = el("a", {
            class: "video-card",
            href: "https://www.youtube.com/watch?v=" + encodeURIComponent(v.id),
            target: "_blank",
            rel: "noopener"
          }, [
            el("img", {
              src: "https://i.ytimg.com/vi/" + encodeURIComponent(v.id) + "/hqdefault.jpg",
              alt: "",
              loading: "lazy"
            }),
            el("div", { class: "video-body" }, [
              el("h3", { text: v.title }),
              el("time", { datetime: v.published, text: v.published.replace(/-/g, "/") })
            ])
          ]);
          videoGrid.appendChild(card);
        });
      })
      .catch(function () {
        videoGrid.appendChild(el("p", {
          class: "video-empty",
          text: "動画リストをうまく読み込めませんでした。YouTubeチャンネルから直接ご覧ください。"
        }));
      });
  }

  // ---- パンダNOW ----
  var newsList = document.getElementById("news-list");
  if (newsList) {
    fetch("data/news.json")
      .then(function (res) { return res.json(); })
      .then(function (items) {
        items.forEach(function (n) {
          var item = el("article", { class: "news-item" }, [
            el("time", { text: n.date.replace(/-/g, "年") + "月" }),
            el("h3", { text: n.title }),
            el("p", { text: n.body }),
            el("span", { class: "news-source", text: "出典: " + n.source })
          ]);
          newsList.appendChild(item);
        });
      })
      .catch(function () { /* ニュースが読めなくても他のコーナーはそのまま動かす */ });
  }
})();
