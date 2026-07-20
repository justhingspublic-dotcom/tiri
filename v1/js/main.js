/* TIRI V1 — 微互動
   規格依 Files/15國IR網站設計規範與排版架構盤點.md（瑞士式互動節奏）
   - 入場：淡入＋上移 16px／550ms，同組卡片 stagger 70ms
   - 數字：首次進入 viewport 播放一次 count-up 900ms
   - 篩選：淡出→重排→淡入，總時長約 350ms
   - prefers-reduced-motion: reduce 時停用位移、縮放與數字動畫 */

(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---- Header 捲動狀態 ---- */
  var header = document.getElementById("site-header");
  function onScroll() {
    header.classList.toggle("is-scrolled", window.scrollY > 8);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---- 行動抽屜（320ms，含背景遮罩） ---- */
  var drawer = document.getElementById("drawer");
  var toggle = document.querySelector(".nav-toggle");

  function setDrawer(open) {
    drawer.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "關閉選單" : "開啟選單");
    document.body.style.overflow = open ? "hidden" : "";
  }
  toggle.addEventListener("click", function () {
    setDrawer(!drawer.classList.contains("is-open"));
  });
  drawer.addEventListener("click", function (event) {
    if (event.target.closest("[data-drawer-close]")) setDrawer(false);
  });
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && drawer.classList.contains("is-open")) {
      setDrawer(false);
      toggle.focus();
    }
  });

  /* ---- 入場動畫（IntersectionObserver＋群組 stagger） ---- */
  var revealTargets = document.querySelectorAll(".reveal");

  if (reduceMotion || !("IntersectionObserver" in window)) {
    revealTargets.forEach(function (el) { el.classList.add("is-visible"); });
  } else {
    document.querySelectorAll("[data-reveal-group]").forEach(function (group) {
      var children = group.querySelectorAll(".reveal");
      children.forEach(function (el, index) {
        el.style.setProperty("--reveal-delay", (index * 70) + "ms");
      });
    });

    var revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });

    revealTargets.forEach(function (el) { revealObserver.observe(el); });
  }

  /* ---- 數字 count-up（一次性，900ms） ---- */
  var counters = document.querySelectorAll("[data-count]");

  function formatCount(value, plain) {
    return plain ? String(value) : value.toLocaleString("en-US");
  }

  function runCounter(el) {
    var target = parseInt(el.getAttribute("data-count"), 10);
    var plain = el.hasAttribute("data-count-plain");
    var duration = 900;
    var start = null;

    function step(timestamp) {
      if (start === null) start = timestamp;
      var progress = Math.min((timestamp - start) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 4); /* ease-out-quart */
      el.textContent = formatCount(Math.round(target * eased), plain);
      if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  if (!reduceMotion && "IntersectionObserver" in window) {
    var countObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          runCounter(entry.target);
          countObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.6 });
    counters.forEach(function (el) { countObserver.observe(el); });
  }

  /* ---- 洞察分類篩選（淡出→切換→淡入，約 350ms） ---- */
  var filterButtons = document.querySelectorAll(".filter-btn");
  var insightCards = document.querySelectorAll(".insight-card");
  var filterTimer = null;

  function applyFilter(category) {
    function swap() {
      insightCards.forEach(function (card) {
        var match = category === "all" || card.getAttribute("data-category") === category;
        card.classList.toggle("is-hidden", !match);
      });
      insightCards.forEach(function (card) {
        card.classList.remove("is-hiding");
      });
    }

    if (reduceMotion) {
      swap();
      return;
    }
    insightCards.forEach(function (card) { card.classList.add("is-hiding"); });
    window.clearTimeout(filterTimer);
    filterTimer = window.setTimeout(swap, 200);
  }

  /* ---- 示意表單：阻止送出跳頁 ---- */
  document.querySelectorAll("form").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
    });
  });

  filterButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      if (button.getAttribute("aria-pressed") === "true") return;
      filterButtons.forEach(function (other) {
        other.setAttribute("aria-pressed", String(other === button));
      });
      applyFilter(button.getAttribute("data-filter"));
    });
  });
})();
