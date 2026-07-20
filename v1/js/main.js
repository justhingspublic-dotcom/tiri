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

  /* ---- 語言切換下拉（footer，向上展開） ---- */
  var langToggle = document.querySelector(".lang-toggle");
  var langMenu = document.getElementById("lang-menu");

  if (langToggle && langMenu) {
    var setLang = function (open) {
      langMenu.classList.toggle("is-open", open);
      langToggle.setAttribute("aria-expanded", String(open));
    };
    langToggle.addEventListener("click", function (event) {
      event.stopPropagation();
      setLang(!langMenu.classList.contains("is-open"));
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
