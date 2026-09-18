// 個体別アルバムページ — 「もっと見る」と並べ替え(JSがなくても最初の分は見える)
(function () {
  "use strict";

  function formatViews(n) {
    if (n >= 10000) return Math.round(n / 10000) + "万回";
    return n + "回";
  }

  function formatDuration(sec) {
    var m = Math.floor(sec / 60);
    var s = String(sec % 60).padStart(2, "0");
    return m + ":" + s;
  }

  function escapeHTML(s) {
    var d = document.createElement("div");
    d.textContent = s || "";
    return d.innerHTML;
  }

  function cardHTML(v) {
    var dateLabel = (v.shootDate || v.publishDate || "").replace(/-/g, "/");
    return (
      '<a class="video-card" href="https://www.youtube.com/watch?v=' + v.id + '" target="_blank" rel="noopener">' +
      '<img src="https://i.ytimg.com/vi/' + v.id + '/hqdefault.jpg" alt="" loading="lazy" width="320" height="180">' +
      '<div class="video-body">' +
      "<h3>" + escapeHTML(v.title) + (v.durationSec ? ' <span class="nowrap">(' + formatDuration(v.durationSec) + ")</span>" : "") + "</h3>" +
      '<p class="video-meta"><span>' + dateLabel + "</span><span>" + formatViews(v.views) + "</span></p>" +
      "</div></a>"
    );
  }

  function sortKeyTime(v) {
    return v.shootDate || v.publishDate || "";
  }

  document.querySelectorAll("[data-panda-page]").forEach(function (page) {
    var grid = page.querySelector(".video-grid");
    var dataEl = page.querySelector('script[type="application/json"]');
    if (!grid || !dataEl) return;

    var allVideos = JSON.parse(dataEl.textContent); // 撮影日(なければ公開日)の昇順で並んでいる
    var order = "time";
    var shown = parseInt(grid.getAttribute("data-shown") || "0", 10);
    var moreBtn = page.querySelector(".js-more");
    var sortBtns = page.querySelectorAll(".js-sort");
    var BATCH = 60;

    function sortedList() {
      var arr = allVideos.slice();
      if (order === "popular") {
        arr.sort(function (a, b) { return b.views - a.views; });
      } else {
        arr.sort(function (a, b) { return sortKeyTime(a).localeCompare(sortKeyTime(b)); });
      }
      return arr;
    }

    function renderMore() {
      var list = sortedList();
      var slice = list.slice(shown, shown + BATCH);
      slice.forEach(function (v) {
        grid.insertAdjacentHTML("beforeend", cardHTML(v));
      });
      shown += slice.length;
      if (moreBtn) moreBtn.hidden = shown >= list.length;
    }

    function resetAndRender() {
      grid.innerHTML = "";
      shown = 0;
      if (moreBtn) moreBtn.hidden = false;
      renderMore();
    }

    if (moreBtn) moreBtn.addEventListener("click", renderMore);

    sortBtns.forEach(function (btn) {
      btn.addEventListener("click", function () {
        if (btn.getAttribute("aria-pressed") === "true") return;
        order = btn.getAttribute("data-order");
        sortBtns.forEach(function (b) {
          b.setAttribute("aria-pressed", b === btn ? "true" : "false");
        });
        resetAndRender();
      });
    });
  });
})();
