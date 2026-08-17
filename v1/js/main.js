/* TIRI V1 — 微互動
   規格依 Files/15國IR網站設計規範與排版架構盤點.md（瑞士式互動節奏）
   - 入場：淡入 550ms（不做位移），同組卡片 stagger 70ms
   - 數字：首次進入 viewport 播放一次 count-up 900ms
   - 篩選：淡出→重排→淡入，總時長約 350ms
   - prefers-reduced-motion: reduce 時停用縮放與數字動畫 */

(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---- Header 捲動狀態 ----
     平順捲動時走 0.55s 漸變；跳躍捲動（錨點、拖捲軸、Cmd+↓）立即切換，
     否則 header 會有半透明的空窗期，下方內容與分隔線會透出來 */
  var header = document.getElementById("site-header");
  var lastY = window.scrollY;

  function onScroll() {
    var y = window.scrollY;
    if (Math.abs(y - lastY) > 260) {
      header.classList.add("no-anim");
      requestAnimationFrame(function () {
        requestAnimationFrame(function () { header.classList.remove("no-anim"); });
      });
    }
    lastY = y;
    header.classList.toggle("is-scrolled", y > 8);
    document.documentElement.classList.toggle("is-nav-filled", y > 8);
  }

  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("hashchange", onScroll);
  window.addEventListener("pageshow", onScroll);
  window.addEventListener("load", onScroll);
  onScroll();

  /* ---- Overlay scrollbar ----
     保留原生滾輪、鍵盤與捲動語意；滑塊可用滑鼠拖曳。
     觸控裝置與強制色彩模式繼續使用系統 scrollbar。 */
  var useOverlayScrollbar = window.matchMedia("(pointer: fine)").matches &&
    !window.matchMedia("(forced-colors: active)").matches;

  if (useOverlayScrollbar) {
    var scrollRail = document.createElement("div");
    var scrollThumb = document.createElement("div");
    var scrollFrame = 0;
    var scrollIdleTimer = 0;
    var dragPointer = null;
    var thumbHovered = false;
    var dragStartY = 0;
    var dragStartScroll = 0;
    var dragScale = 1;

    scrollRail.className = "site-scrollbar";
    scrollRail.setAttribute("aria-hidden", "true");
    scrollThumb.className = "site-scrollbar__thumb";
    scrollRail.appendChild(scrollThumb);
    document.body.appendChild(scrollRail);
    document.documentElement.classList.add("has-overlay-scrollbar");

    function getScrollHeight() {
      return Math.max(document.documentElement.scrollHeight, document.body.scrollHeight);
    }

    function updateOverlayScrollbar() {
      scrollFrame = 0;
      var viewportHeight = window.innerHeight;
      var trackHeight = scrollRail.clientHeight;
      var scrollHeight = getScrollHeight();
      var maxScroll = Math.max(0, scrollHeight - viewportHeight);

      if (maxScroll <= 1) {
        scrollRail.hidden = true;
        scrollRail.classList.remove("is-visible");
        window.clearTimeout(scrollIdleTimer);
        return;
      }

      var wasHidden = scrollRail.hidden;
      scrollRail.hidden = false;
      var thumbHeight = Math.min(trackHeight, Math.max(44, trackHeight * viewportHeight / scrollHeight));
      var thumbTravel = Math.max(0, trackHeight - thumbHeight);
      var scrollTop = Math.min(maxScroll, Math.max(0, window.scrollY));
      var thumbTop = maxScroll ? scrollTop / maxScroll * thumbTravel : 0;

      scrollThumb.style.height = thumbHeight + "px";
      scrollThumb.style.setProperty("--scroll-thumb-y", thumbTop + "px");
      if (wasHidden) showOverlayScrollbar();
    }

    function requestScrollbarUpdate() {
      if (!scrollFrame) scrollFrame = requestAnimationFrame(updateOverlayScrollbar);
    }

    function scheduleScrollbarFade() {
      window.clearTimeout(scrollIdleTimer);
      if (dragPointer !== null || thumbHovered) return;
      scrollIdleTimer = window.setTimeout(function () {
        scrollRail.classList.remove("is-visible");
      }, 2000);
    }

    function showOverlayScrollbar() {
      scrollRail.classList.add("is-visible");
      scheduleScrollbarFade();
    }

    function onOverlayScroll() {
      requestScrollbarUpdate();
      showOverlayScrollbar();
    }

    function holdScrollbarVisible() {
      thumbHovered = true;
      window.clearTimeout(scrollIdleTimer);
      scrollRail.classList.add("is-visible");
    }

    function releaseScrollbarHover() {
      thumbHovered = false;
      scheduleScrollbarFade();
    }

    scrollThumb.addEventListener("pointerdown", function (event) {
      if (event.button !== 0) return;
      event.preventDefault();
      window.clearTimeout(scrollIdleTimer);
      scrollRail.classList.add("is-visible");
      dragPointer = event.pointerId;
      dragStartY = event.clientY;
      dragStartScroll = window.scrollY;

      var maxScroll = Math.max(0, getScrollHeight() - window.innerHeight);
      var thumbTravel = Math.max(1, scrollRail.clientHeight - scrollThumb.getBoundingClientRect().height);
      dragScale = maxScroll / thumbTravel;

      scrollThumb.classList.add("is-dragging");
      scrollThumb.setPointerCapture(event.pointerId);
    });

    scrollThumb.addEventListener("pointermove", function (event) {
      if (event.pointerId !== dragPointer) return;
      window.scrollTo(0, dragStartScroll + (event.clientY - dragStartY) * dragScale);
    });

    function endScrollbarDrag(event) {
      if (event.pointerId !== dragPointer) return;
      dragPointer = null;
      scrollThumb.classList.remove("is-dragging");
      scheduleScrollbarFade();
    }

    scrollThumb.addEventListener("pointerup", endScrollbarDrag);
    scrollThumb.addEventListener("pointercancel", endScrollbarDrag);
    scrollThumb.addEventListener("pointerenter", holdScrollbarVisible);
    scrollThumb.addEventListener("pointerleave", releaseScrollbarHover);
    window.addEventListener("scroll", onOverlayScroll, { passive: true });
    window.addEventListener("resize", requestScrollbarUpdate);
    window.addEventListener("load", requestScrollbarUpdate);
    window.addEventListener("pageshow", requestScrollbarUpdate);

    if ("ResizeObserver" in window) {
      new ResizeObserver(requestScrollbarUpdate).observe(document.body);
    }

    updateOverlayScrollbar();
    showOverlayScrollbar();
  }

  /* ---- 滾輪慣性捲動 ----
     只接管滑鼠滾輪／觸控板的 wheel：把 delta 累積成目標值，
     每幀以指數衰減逼近（幀率無關），放開後仍會滑行一小段再停。
     觸控、鍵盤、拖捲軸、錨點、hash 都維持原生；一偵測到不是我們寫入的捲動
     就立即讓位（可中斷、不鎖輸入）。reduced-motion 直接停用。 */
  if (!reduceMotion && "requestAnimationFrame" in window) {
    var TAU = 0.14;            /* 逼近時間常數（秒），越小越跟手、越大越飄 */
    var STOP_EPS = 0.4;        /* 距目標小於此值即結束 */
    var inertiaTarget = 0;
    var inertiaCurrent = 0;
    var inertiaApplied = -1;   /* 上一幀實際寫入後讀回的 scrollY，用來偵測外部捲動 */
    var inertiaFrame = 0;
    var inertiaLastTs = 0;

    function maxScrollY() {
      return Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
    }

    function stopInertia() {
      if (inertiaFrame) cancelAnimationFrame(inertiaFrame);
      inertiaFrame = 0;
      inertiaApplied = -1;
      document.documentElement.classList.remove("is-wheel-scrolling");
    }

    function stepInertia(ts) {
      inertiaFrame = 0;
      /* 別人動了捲軸（拖原生捲軸、程式捲動、錨點）→ 讓位 */
      if (inertiaApplied >= 0 && Math.abs(window.scrollY - inertiaApplied) > 1.5) { stopInertia(); return; }

      var dt = inertiaLastTs ? Math.min(0.064, (ts - inertiaLastTs) / 1000) : 1 / 60;
      inertiaLastTs = ts;
      var max = maxScrollY();
      if (inertiaTarget > max) inertiaTarget = max;
      if (inertiaTarget < 0) inertiaTarget = 0;

      var diff = inertiaTarget - inertiaCurrent;
      if (Math.abs(diff) < STOP_EPS) {
        window.scrollTo(0, Math.round(inertiaTarget));
        inertiaCurrent = inertiaTarget;
        stopInertia();
        return;
      }
      inertiaCurrent += diff * (1 - Math.exp(-dt / TAU));
      /* 只寫整數像素：小數位移會讓瀏覽器（尤其 Safari）整頁重新點陣化，是主執行緒捲動最常見的掉幀源 */
      window.scrollTo(0, Math.round(inertiaCurrent));
      inertiaApplied = window.scrollY;
      inertiaFrame = requestAnimationFrame(stepInertia);
    }

    /* 事件路徑上有可捲動的容器（搜尋結果、下拉面板…）→ 交給原生。
       觸控板一秒可發上百個 wheel，getComputedStyle 走訪只在 target 改變或超過 250ms 才重做，
       其餘只讀 scrollTop 判斷該方向還能不能捲。 */
    var scrollableCache = { target: null, until: 0, containers: [], locked: false };

    function findScrollableContainers(node) {
      var found = [];
      while (node && node !== document.body && node !== document.documentElement && node.nodeType === 1) {
        var oy = getComputedStyle(node).overflowY;
        if ((oy === "auto" || oy === "scroll" || oy === "overlay") && node.scrollHeight > node.clientHeight + 1) found.push(node);
        node = node.parentNode;
      }
      return found;
    }

    function refreshScrollableCache(target, now) {
      scrollableCache.target = target;
      scrollableCache.until = now + 250;
      scrollableCache.containers = findScrollableContainers(target);
      var h = getComputedStyle(document.documentElement).overflowY;
      var b = getComputedStyle(document.body).overflowY;
      scrollableCache.locked = h === "hidden" || b === "hidden" || h === "clip" || b === "clip";
    }

    function containerCanScroll(deltaY) {
      var list = scrollableCache.containers;
      for (var i = 0; i < list.length; i++) {
        var node = list[i];
        if (deltaY < 0 ? node.scrollTop > 0 : node.scrollTop + node.clientHeight < node.scrollHeight - 1) return true;
      }
      return false;
    }

    function onInertiaWheel(event) {
      if (event.defaultPrevented || event.ctrlKey || event.metaKey) return;      /* 縮放手勢放行 */
      if (Math.abs(event.deltaX) > Math.abs(event.deltaY)) return;                /* 橫向留給原生 */
      var now = event.timeStamp || performance.now();
      if (event.target !== scrollableCache.target || now > scrollableCache.until) refreshScrollableCache(event.target, now);
      if (scrollableCache.locked) return;
      if (containerCanScroll(event.deltaY)) { stopInertia(); return; }

      var dy = event.deltaY;
      if (event.deltaMode === 1) dy *= 40;                       /* lines → px */
      else if (event.deltaMode === 2) dy *= window.innerHeight;  /* pages → px */
      if (!dy) return;

      var max = maxScrollY();
      var y = window.scrollY;
      /* 已在邊界且還往外推：不攔，維持原生（不做假的 rubber-band） */
      if ((dy < 0 && y <= 0) || (dy > 0 && y >= max - 0.5)) { stopInertia(); return; }

      event.preventDefault();
      if (!inertiaFrame) {                 /* 從「現在畫面上的值」起步，不會跳 */
        inertiaCurrent = y;
        inertiaTarget = y;
        inertiaLastTs = 0;
        document.documentElement.classList.add("is-wheel-scrolling");
      }
      inertiaTarget = Math.min(max, Math.max(0, inertiaTarget + dy));
      if (!inertiaFrame) inertiaFrame = requestAnimationFrame(stepInertia);
    }

    window.addEventListener("wheel", onInertiaWheel, { passive: false });
    /* 其他輸入一介入就交還控制權 */
    window.addEventListener("keydown", stopInertia, true);
    window.addEventListener("pointerdown", stopInertia, true);
    window.addEventListener("click", stopInertia, true);
    window.addEventListener("hashchange", stopInertia);
    window.addEventListener("touchstart", stopInertia, { passive: true, capture: true });
  }

  /* 語言下拉、滿寬面板、搜尋都掛在 header 上，同時開會疊在一起——
     透過這兩個掛勾互收（實作在各自的區塊內指定） */
  var closeLangMenu = function () {};
  var closeMegaPanels = function () {};

  /* ---- 滿寬下拉：展開時 header 轉實色 ----
     沉浸式（photo 頁）頂部本來是透明的，面板卻是紙白，兩塊貼在一起會斷掉；
     加 is-menuopen 讓沉浸式規則讓位，同時收掉 header 底線 */
  var mainNav = document.querySelector(".main-nav");

  if (mainNav) {
    // 展開動畫（320ms）跑完才進 settled：之後換選單直接換內容，不重播手風琴
    var settleTimer = null;
    var closeTimer = null;

    var setMenuOpen = function (open) {
      clearTimeout(settleTimer);
      clearTimeout(closeTimer);
      if (open) {
        header.classList.add("is-menuopen");
        settleTimer = setTimeout(function () {
          header.classList.add("is-menusettled");
        }, 340);
      } else {
        // settled 先拿掉讓面板開始摺疊，但 is-menuopen 要留到摺完（320ms）——
        // 否則 header 會比面板早一步變透明，photo 頁上會看到閃一下
        header.classList.remove("is-menusettled");
        closeTimer = setTimeout(function () {
          header.classList.remove("is-menuopen");
        }, 120);
      }
    };

    // 判定範圍是整個 header：滑到 CTA、社群 icon、搜尋時面板要繼續開著，
    // 只有滑鼠離開整個 header 才收
    var menuItems = mainNav.querySelectorAll("li:has(> .menu-panel)");

    // 面板內最後 hover 的子項：滑到 header 其他區域時底線要留著，狀態不能斷
    var clearLastHover = function (scope) {
      (scope || mainNav).querySelectorAll(".mega-item.is-last-hover")
        .forEach(function (el) { el.classList.remove("is-last-hover"); });
    };

    // 換選單時各面板高度不同，底緣直接跳很生硬；
    // 把高度差也補成手風琴（內容瞬間換掉，只有紙的下緣在動）
    var HEIGHT_MS = 220;
    var heightTimer = null;
    var lessMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

    var resetPanelHeights = function () {
      menuItems.forEach(function (item) {
        var panel = item.querySelector(".menu-panel");
        panel.style.transition = "";
        panel.style.height = "";
      });
    };

    var tweenHeight = function (fromPanel, toPanel) {
      var fromH = fromPanel.getBoundingClientRect().height;
      clearTimeout(heightTimer);
      resetPanelHeights();
      var toH = toPanel.getBoundingClientRect().height;
      if (Math.round(fromH) === Math.round(toH)) return;

      toPanel.style.transition = "none";
      toPanel.style.height = fromH + "px";
      void toPanel.offsetHeight;                     // 強制 reflow，起點才會生效
      toPanel.style.transition = "height " + HEIGHT_MS + "ms var(--ease)";
      toPanel.style.height = toH + "px";
      heightTimer = setTimeout(resetPanelHeights, HEIGHT_MS + 20);
    };

    var setActive = function (li) {
      // 面板已經開著、且是換到另一個選單時才補高度差
      var prev = mainNav.querySelector("li.is-menu-active > .menu-panel");
      var next = li ? li.querySelector(".menu-panel") : null;
      var settled = header.classList.contains("is-menusettled");

      menuItems.forEach(function (item) {
        item.classList.toggle("is-menu-active", item === li);
      });
      clearLastHover();   // 換選單或關閉都要重置
      setMenuOpen(Boolean(li));
      if (li) closeLangMenu();

      if (settled && prev && next && prev !== next && !lessMotion.matches) {
        tweenHeight(prev, next);
      } else if (!next) {
        clearTimeout(heightTimer);
        resetPanelHeights();
      }
    };

    // Hover intent：面板還沒開時要停留一下才展開。
    // 沒有這道門檻的話，滑鼠只是要去按搜尋、路徑上掃過選單就會把面板叫出來，
    // 又因為「在 header 內就維持開啟」而賴著不走。
    // 已經開著時換選單則不延遲——切換要跟手。
    var OPEN_DELAY = 120;
    var openTimer = null;

    menuItems.forEach(function (li) {
      li.addEventListener("mouseenter", function () {
        clearTimeout(openTimer);
        if (header.classList.contains("is-menuopen")) {
          setActive(li);
        } else {
          openTimer = setTimeout(function () { setActive(li); }, OPEN_DELAY);
        }
      });
      li.addEventListener("mouseleave", function () { clearTimeout(openTimer); });
      li.querySelectorAll(".mega-item").forEach(function (item) {
        item.addEventListener("mouseenter", function () {
          clearLastHover(li);
          item.classList.add("is-last-hover");
        });
      });
    });
    header.addEventListener("mouseleave", function () {
      clearTimeout(openTimer);
      setActive(null);
    });

    closeMegaPanels = function () { setActive(null); };

    // 鍵盤：焦點離開整個 header 才收（面板由 :focus-within 顯示）
    header.addEventListener("focusin", function (e) {
      if (mainNav.contains(e.target)) {
        var li = e.target.closest("li:has(> .menu-panel)");
        if (li) setActive(li);
      }
    });
    header.addEventListener("focusout", function (e) {
      if (!header.contains(e.relatedTarget)) setActive(null);
    });
  }

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

  /* ---- 搜尋下滑面板（Swiss 式，320ms 手風琴） ---- */
  var searchDrop = document.getElementById("search-panel");
  var searchToggle = document.querySelector(".search-toggle");

  function setSearch(open) {
    if (!searchDrop) return;
    if (open) closeLangMenu();
    searchDrop.classList.toggle("is-open", open);
    if (searchToggle) searchToggle.setAttribute("aria-expanded", String(open));
    document.body.style.overflow = open ? "hidden" : "";
    if (open) {
      var input = searchDrop.querySelector("input[type='search']");
      if (input) setTimeout(function () { input.focus(); }, 600);
    }
  }
  if (searchDrop && searchToggle) {
    searchToggle.addEventListener("click", function () {
      setSearch(!searchDrop.classList.contains("is-open"));
    });
    searchDrop.addEventListener("click", function (event) {
      if (event.target.closest("[data-search-close]")) setSearch(false);
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && searchDrop.classList.contains("is-open")) {
        setSearch(false);
        searchToggle.focus();
      }
    });
  }

  /* ---- 站內搜尋（2026-08-17）----
     前端索引：../search-index.json 由 _archive/scripts/v1build/build_search_index.py 掃 html/ 產出，
     首次打開面板才載入。中文用子字串比對（多詞 AND），結果依八區分組、即時顯示在輸入框下方；
     不跳頁、不另開結果頁。 */
  (function initSiteSearch() {
    var cfg = window.TIRI_SEARCH;
    var results = document.getElementById("search-results");
    var input = document.getElementById("site-search-input");
    if (!cfg || !results || !input || !searchDrop) return;
    var inner = results.querySelector(".search-results-inner");
    var form = input.closest("form");
    var t = cfg.strings;
    var index = null, loading = null;
    var currentHits = [], activeIndex = -1, debounce = 0;
    var SNIPPET = 72;

    function esc(str) {
      return String(str).replace(/[&<>"]/g, function (c) {
        return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
      });
    }
    function fmt(str, map) {
      return str.replace(/\{(\w+)\}/g, function (_, k) { return esc(map[k]); });
    }

    function loadIndex() {
      if (index) return Promise.resolve(index);
      if (loading) return loading;
      loading = fetch("../search-index.json").then(function (r) { return r.json(); }).then(function (data) {
        index = data.filter(function (e) { return e.l === cfg.lang; }).map(function (e) {
          e.tl = e.t.toLowerCase();
          e.bl = e.b.toLowerCase();
          return e;
        });
        return index;
      });
      return loading;
    }
    /* 面板一打開就預抓索引，打字時已就緒 */
    searchToggle.addEventListener("click", function () { loadIndex(); });

    function terms(q) {
      return q.trim().toLowerCase().split(/\s+/).filter(Boolean);
    }
    function search(q) {
      var ts = terms(q);
      if (!ts.length || !index) return [];
      var hits = [];
      index.forEach(function (e) {
        var score = 0, ok = true;
        for (var i = 0; i < ts.length; i++) {
          var inTitle = e.tl.indexOf(ts[i]) > -1;
          var bodyPos = e.bl.indexOf(ts[i]);
          if (!inTitle && bodyPos < 0) { ok = false; break; }
          /* 拉丁詞落在單字邊界才算完整命中（"IR" 命中 "IR Update" 給滿分，命中 "TIRI" 只給一半） */
          if (inTitle) score += (/^[a-z0-9]+$/.test(ts[i]) && !new RegExp("(^|[^a-z0-9])" + ts[i]).test(e.tl)) ? 18 : 40;
          if (bodyPos > -1) score += Math.min(6, e.bl.split(ts[i]).length - 1) * 2 + (bodyPos < 200 ? 4 : 0);
        }
        if (ok) hits.push({ e: e, score: score });
      });
      hits.sort(function (a, b) { return b.score - a.score; });
      return hits;
    }

    /* 命中字反白：對已 escape 的純文字做，避免把標記本身當成內容 */
    function highlight(text, ts) {
      var out = "", lower = text.toLowerCase(), i = 0;
      while (i < text.length) {
        var best = -1, bestLen = 0;
        for (var k = 0; k < ts.length; k++) {
          if (lower.substr(i, ts[k].length) === ts[k] && ts[k].length > bestLen) { best = k; bestLen = ts[k].length; }
        }
        if (best > -1) { out += "<mark>" + esc(text.substr(i, bestLen)) + "</mark>"; i += bestLen; }
        else { out += esc(text[i]); i++; }
      }
      return out;
    }
    function snippet(e, ts) {
      var pos = -1;
      for (var k = 0; k < ts.length; k++) {
        var p = e.bl.indexOf(ts[k]);
        if (p > -1 && (pos < 0 || p < pos)) pos = p;
      }
      var start = pos < 0 ? 0 : Math.max(0, pos - Math.floor(SNIPPET / 3));
      var text = e.b.substr(start, SNIPPET * 2);
      if (start > 0) text = "…" + text;
      if (start + SNIPPET * 2 < e.b.length) text += "…";
      return highlight(text, ts);
    }

    function render(q) {
      var ts = terms(q);
      activeIndex = -1;
      if (!ts.length) {
        currentHits = [];
        inner.innerHTML = '<div class="search-hot"><span class="search-overline">' + esc(t.searchHot) + '</span>' +
          t.searchHotTerms.map(function (w) { return '<button type="button" class="search-chip" data-term="' + esc(w) + '">' + esc(w) + '</button>'; }).join("") + '</div>';
        settle();
        return;
      }
      if (!index) {
        inner.innerHTML = '<p class="search-note">' + esc(t.searchLoading) + '</p>';
        settle();
        return;
      }
      currentHits = search(q);
      if (!currentHits.length) {
        inner.innerHTML = '<p class="search-note">' + fmt(t.searchEmpty, { q: q.trim() }) + '</p>';
        settle();
        return;
      }
      /* 全部列出，依八區分組；組的先後＝該組最佳命中的分數（最相關的區塊排最前），同分照導覽順序 */
      var groups = {}, best = {};
      currentHits.forEach(function (h) {
        (groups[h.e.s] = groups[h.e.s] || []).push(h.e);
        best[h.e.s] = Math.max(best[h.e.s] || 0, h.score);
      });
      var order = Object.keys(groups).sort(function (a, b) {
        return (best[b] - best[a]) || (cfg.sections.indexOf(a) - cfg.sections.indexOf(b));
      });
      var n = 0, html = "";
      order.forEach(function (s) {
        html += '<section class="search-group"><span class="search-overline">' + esc(s) + '</span><ul>';
        groups[s].forEach(function (e) {
          html += '<li><a class="search-hit" href="' + esc(e.u) + '" data-i="' + (n++) + '"><span class="t">' + highlight(e.t, ts) + '</span><span class="d">' + snippet(e, ts) + '</span></a></li>';
        });
        html += '</ul></section>';
      });
      html += '<div class="search-foot"><span>' + fmt(t.searchCount, { n: currentHits.length }) + '</span></div>';
      inner.innerHTML = html;
      settle();
    }

    /* 高度補間：結果數變化時面板底緣不能一幀瞬跳（同 mega panel 作法） */
    function settle() {
      var maxH = Math.max(200, window.innerHeight - results.getBoundingClientRect().top - 48);
      var target = Math.min(inner.scrollHeight, maxH);
      results.style.height = target + "px";
      results.classList.toggle("is-scroll", inner.scrollHeight > maxH);
      results.scrollTop = 0;
    }

    function setActive(i) {
      var links = inner.querySelectorAll(".search-hit");
      if (!links.length) return;
      activeIndex = (i + links.length) % links.length;
      links.forEach(function (a, k) { a.classList.toggle("is-active", k === activeIndex); });
      var el = links[activeIndex];
      var top = el.offsetTop, bottom = top + el.offsetHeight;
      if (top < results.scrollTop) results.scrollTop = top;
      else if (bottom > results.scrollTop + results.clientHeight) results.scrollTop = bottom - results.clientHeight;
    }

    input.addEventListener("input", function () {
      window.clearTimeout(debounce);
      debounce = window.setTimeout(function () {
        loadIndex().then(function () { render(input.value); });
        render(input.value);
      }, 120);
    });
    input.addEventListener("keydown", function (event) {
      if (event.key === "ArrowDown") { event.preventDefault(); setActive(activeIndex + 1); }
      else if (event.key === "ArrowUp") { event.preventDefault(); setActive(activeIndex - 1); }
    });
    /* 進入結果頁：先把面板收起（0.6s 上滑，主要位移在前 0.4s），再交給站內轉場——
       支援 View Transitions 的瀏覽器由 @view-transition 交叉淡入；不支援的走 is-leaving 淡出備援。
       輸入內容在面板收完後清掉，回上一頁（bfcache）再開時是乾淨狀態。 */
    var navigating = false;
    function goTo(href) {
      if (navigating || !href) return;
      navigating = true;
      setSearch(false);
      var useVT = typeof document.startViewTransition === "function" && window.CSS && CSS.supports("view-transition-name: none");
      var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      var wait = reduce ? 0 : 400;
      window.setTimeout(function () {
        if (!useVT && !reduce) {
          document.documentElement.classList.add("is-leaving");
          window.setTimeout(function () { window.location.href = href; }, 340);
        } else {
          window.location.href = href;
        }
      }, wait);
      window.setTimeout(function () {
        input.value = "";
        render("");
        navigating = false;
        document.documentElement.classList.remove("is-leaving");
      }, 2500);   /* 防呆：導航沒發生也要復原 */
    }
    if (form) {
      form.addEventListener("submit", function () {
        var links = inner.querySelectorAll(".search-hit");
        var target = links[activeIndex > -1 ? activeIndex : 0];
        if (target) goTo(target.getAttribute("href"));
      });
    }
    /* 叉叉：有輸入內容＝先清除（回到熱門捷徑、焦點留在輸入框）；已是空的才關閉面板 */
    var closeBtn = searchDrop.querySelector(".search-close");
    if (closeBtn) {
      closeBtn.addEventListener("click", function () {
        if (input.value) {
          input.value = "";
          render("");
          input.focus();
        } else {
          setSearch(false);
          searchToggle.focus();
        }
      });
    }

    inner.addEventListener("click", function (event) {
      var chip = event.target.closest(".search-chip");
      if (chip) {
        input.value = chip.getAttribute("data-term");
        input.focus();
        loadIndex().then(function () { render(input.value); });
        return;
      }
      var hit = event.target.closest(".search-hit");
      if (hit && event.button === 0 && !(event.metaKey || event.ctrlKey || event.shiftKey || event.altKey)) {
        event.preventDefault();
        goTo(hit.getAttribute("href"));
      }
    });
    inner.addEventListener("mousemove", function (event) {
      var hit = event.target.closest(".search-hit");
      if (hit) {
        var i = Number(hit.getAttribute("data-i"));
        if (i !== activeIndex) setActive(i);
      }
    });
    window.addEventListener("resize", function () { if (searchDrop.classList.contains("is-open")) settle(); });

    /* 開面板：顯示熱門捷徑並鎖定高度；關面板：清空 */
    var observer = new MutationObserver(function () {
      if (searchDrop.classList.contains("is-open")) {
        results.style.transition = "none";
        render(input.value);
        void results.offsetHeight;
        results.style.transition = "";
      }
    });
    observer.observe(searchDrop, { attributes: true, attributeFilter: ["class"] });
    render("");

    /* ?q=關鍵字 直接開面板帶入查詢（可分享的搜尋連結） */
    var preset = new URLSearchParams(window.location.search).get("q");
    if (preset) {
      input.value = preset;
      setSearch(true);
      loadIndex().then(function () { render(preset); });
    }
  })();

  /* ---- 跨頁轉場備援 ----
     支援 View Transitions 的瀏覽器由 CSS 的 @view-transition 接手（交叉淡入淡出、
     不會經過白畫面），JS 完全不攔截導航。只有不支援的瀏覽器才走下面的淡出流程。 */
  var motionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  var supportsViewTransitions =
    typeof document.startViewTransition === "function" &&
    window.CSS && CSS.supports("view-transition-name: none");

  window.addEventListener("pageshow", function () {
    document.documentElement.classList.remove("is-leaving");
  });

  document.addEventListener("click", function (event) {
    if (supportsViewTransitions) return;
    if (motionQuery.matches) return;
    if (event.defaultPrevented || event.button !== 0) return;
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;

    var link = event.target.closest("a[href]");
    if (!link || link.target === "_blank" || link.hasAttribute("download")) return;

    var href = link.getAttribute("href");
    if (!href || href.charAt(0) === "#" || /^(https?:)?\/\//.test(href) || /^(mailto|tel):/.test(href)) return;

    // 同頁錨點（如 about.html#team）不攔截：只換 hash 不會重載，淡出後會停在全白
    if (link.href.split("#")[0] === location.href.split("#")[0]) return;

    event.preventDefault();
    document.documentElement.classList.add("is-leaving");
    setTimeout(function () { location.href = link.href; }, 340);
    // 防呆：導航若未發生（被擋下等），別讓頁面卡在全白
    setTimeout(function () { document.documentElement.classList.remove("is-leaving"); }, 2500);
  });

  /* ---- 語言切換下拉（header-top 工具列，navbar.js 注入，向下展開） ---- */
  var langToggle = document.querySelector(".lang-toggle");
  var langMenu = document.getElementById("lang-menu");

  if (langToggle && langMenu) {
    var setLang = function (open) {
      langMenu.classList.toggle("is-open", open);
      langToggle.setAttribute("aria-expanded", String(open));
    };
    closeLangMenu = function () { setLang(false); };
    langToggle.addEventListener("click", function (event) {
      event.stopPropagation();
      var willOpen = !langMenu.classList.contains("is-open");
      if (willOpen) closeMegaPanels();   // 語言下拉開啟時收掉滿寬面板，兩者不同時開
      setLang(willOpen);
    });
    document.addEventListener("click", function (event) {
      if (!event.target.closest(".lang-switch")) setLang(false);
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && langMenu.classList.contains("is-open")) {
        setLang(false);
        langToggle.focus();
      }
    });
  }

  /* ---- 入場動畫的啟動時機 ----
     跨頁 View Transition 期間，新頁已經 render 了、只是被舊頁快照蓋著，
     IntersectionObserver 會在那時就觸發，等交叉淡入結束時入場動畫早已播完，
     使用者只看到靜止畫面。所以要等 viewTransition.finished 之後才開始觀察。 */
  var entranceCallbacks = [];
  var entranceStarted = false;

  function startEntrance() {
    if (entranceStarted) return;
    entranceStarted = true;
    entranceCallbacks.forEach(function (fn) { fn(); });
    entranceCallbacks.length = 0;
  }

  function onPageRevealed(fn) {
    if (entranceStarted) fn();
    else entranceCallbacks.push(fn);
  }

  if ("onpagereveal" in window) {
    window.addEventListener("pagereveal", function (event) {
      if (event.viewTransition) event.viewTransition.finished.then(startEntrance, startEntrance);
      else startEntrance();
    });
    // 防呆：pagereveal 或 finished 沒如期發生時，別讓內容永遠停在隱藏狀態
    setTimeout(startEntrance, 1500);
  } else {
    startEntrance();
  }

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

    onPageRevealed(function () {
      revealTargets.forEach(function (el) { revealObserver.observe(el); });
    });
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
    onPageRevealed(function () {
      counters.forEach(function (el) { countObserver.observe(el); });
    });
  }

  /* ---- 洞察分類篩選（淡出→切換→淡入，約 350ms） ---- */
  var filterButtons = document.querySelectorAll(".filter-btn");
  var insightCards = document.querySelectorAll(".insight-card[data-category], .event-item[data-category]");
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
