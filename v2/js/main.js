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

  /* ---- 懸浮島視覺殼＋搜尋層搬家（執行期做，134 頁 HTML 不動） ----
     殼必須注入 body、不能放在 header 裡：.site-header 有 view-transition-name，
     會被隔離成獨立繪製群組，群組內的 backdrop-filter 取樣不到頁面內容，
     毛玻璃會變純半透明（偽元素另踩 Safari WebKit bug）。
     搜尋現在改為 header 內的 absolute dropdown，與島體共用展開高度，
     不再使用會被 transform 影響的 fixed 全螢幕面板。 */
  var islandShell = document.querySelector(".island-shell");
  if (!islandShell) {
    islandShell = document.createElement("span");
    islandShell.className = "island-shell";
    islandShell.setAttribute("aria-hidden", "true");
    document.body.prepend(islandShell);
  }
  var searchPanelEl = document.getElementById("search-panel");

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
  var searchDrop = searchPanelEl;
  var searchToggle = document.querySelector(".search-toggle");
  /* 入口保留 header actions 原本的純 icon；只改變點擊後的展開方式。 */
  var searchToggles = document.querySelectorAll(".search-toggle");

  if (mainNav) {
    // 展開動畫（320ms）跑完才進 settled：之後換選單直接換內容，不重播手風琴
    var settleTimer = null;
    var closeTimer = null;

    var setMenuOpen = function (open) {
      clearTimeout(settleTimer);
      clearTimeout(closeTimer);
      if (open) {
        header.classList.add("is-menuopen");
        islandShell.classList.add("is-menuopen");
        settleTimer = setTimeout(function () {
          header.classList.add("is-menusettled");
        }, 340);
      } else {
        // is-menuopen 讓殼在頂部（未滾動）也保持浮現，要等面板收合（200ms）
        // 完才拿掉——太早拿掉，殼會在面板還在收的時候先開始淡出
        header.classList.remove("is-menusettled");
        closeTimer = setTimeout(function () {
          header.classList.remove("is-menuopen");
          islandShell.classList.remove("is-menuopen");
        }, 210);
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

    // 島式下拉：面板高度全程由 JS 驅動（inline height＋transition）。
    // 首開＝spring 過衝彈跳（島長高再彈回）；換選單＝從目前高度補間 220ms；
    // 關閉＝0.2s 俐落收合。clip-path 手風琴已退場（超出範圍會被夾住，彈不出來）。
    var HEIGHT_MS = 220;
    var lessMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

    // 視覺殼＝header::before 一整塊圓角矩形：高度（--panel-h）與圓角（--shell-r）
    // 要跟面板高度同一組 transition 同步動，殼與內容才不會脫開
    var setShell = function (h, dur, easing) {
      islandShell.style.setProperty("--panel-h", h + "px");
      islandShell.style.setProperty("--panel-t", dur);
      islandShell.style.setProperty("--panel-e", easing);
    };

    var openPanel = function (panel, fromH) {
      var target = panel.scrollHeight;
      if (lessMotion.matches) {
        panel.style.transition = "none";
        panel.style.height = target + "px";
        setShell(target, "0s", "linear");
        return;
      }
      panel.style.transition = "none";
      panel.style.height = (fromH == null ? 0 : fromH) + "px";
      setShell(fromH == null ? 0 : fromH, "0s", "linear");
      void panel.offsetHeight;                     // 強制 reflow，起點才會生效
      var dur = fromH == null ? "0.6s" : HEIGHT_MS + "ms";
      var easing = fromH == null ? "var(--spring)" : "var(--ease)";
      panel.style.transition = "height " + dur + " " + easing;
      panel.style.height = target + "px";
      setShell(target, dur, easing);
    };

    var closePanel = function (panel, instant) {
      if (instant || lessMotion.matches) {
        panel.style.transition = "none";
        panel.style.height = "0px";
        setShell(0, "0s", "linear");
        return;
      }
      // visibility 要等收合結束才隱藏：inline transition 會整組蓋掉樣式表的，
      // 所以延遲要跟高度一起寫在這裡
      panel.style.transition = "height 0.2s var(--ease), visibility 0s linear 0.2s";
      panel.style.height = "0px";
      setShell(0, "0.2s", "var(--ease)");
    };

    var setActive = function (li, externalFromH) {
      var prevLi = mainNav.querySelector("li.is-menu-active");
      var prev = prevLi ? prevLi.querySelector(".menu-panel") : null;
      var next = li ? li.querySelector(".menu-panel") : null;

      menuItems.forEach(function (item) {
        item.classList.toggle("is-menu-active", item === li);
      });
      clearLastHover();   // 換選單或關閉都要重置
      setMenuOpen(Boolean(li));

      if (next && !prev) {
        openPanel(next, externalFromH);                    // 首開：彈跳；搜尋切入：接手現有高度
      } else if (next && prev && prev !== next) {
        var fromH = prev.getBoundingClientRect().height;   // 換選單：接手目前高度
        closePanel(prev, true);
        openPanel(next, fromH);
      } else if (!next && prev) {
        closePanel(prev);
      }
    };

    // 開著時改視窗大小：內容重排後高度會變，重新量一次（殼要跟著）
    window.addEventListener("resize", function () {
      var open = mainNav.querySelector("li.is-menu-active > .menu-panel");
      if (!open && searchDrop && searchDrop.classList.contains("is-open")) open = searchDrop;
      if (open) {
        open.style.transition = "none";
        open.style.height = open.scrollHeight + "px";
        setShell(open.scrollHeight, "0s", "linear");
      }
    });

    // Hover intent：面板還沒開時要停留一下才展開。
    // 沒有這道門檻的話，滑鼠只是要去按搜尋、路徑上掃過選單就會把面板叫出來，
    // 又因為「在 header 內就維持開啟」而賴著不走。
    // 已經開著時換選單則不延遲——切換要跟手。
    var OPEN_DELAY = 120;
    var openTimer = null;

    menuItems.forEach(function (li) {
      var menuTrigger = li.querySelector(":scope > a");
      if (menuTrigger) {
        menuTrigger.addEventListener("click", function (event) {
          if (!searchDrop || !searchDrop.classList.contains("is-open")) return;

          /* 搜尋開著時，hover 仍不作用；但點擊是明確意圖：
             第一次點擊不導頁，原位把搜尋面板換成對應 mega menu。 */
          event.preventDefault();
          clearTimeout(openTimer);
          var searchHeight = searchDrop.getBoundingClientRect().height;
          searchDrop.classList.remove("is-open");
          searchToggles.forEach(function (button) {
            button.setAttribute("aria-expanded", "false");
          });
          closePanel(searchDrop, true);
          setActive(li, searchHeight);
        });
      }

      li.addEventListener("mouseenter", function () {
        clearTimeout(openTimer);
        if (searchDrop && searchDrop.classList.contains("is-open")) return;
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
      if (searchDrop && searchDrop.classList.contains("is-open")) return;
      setActive(null);
    });

    // 鍵盤：焦點離開整個 header 才收（面板由 :focus-within 顯示）
    header.addEventListener("focusin", function (e) {
      if (searchDrop && searchDrop.classList.contains("is-open")) return;
      if (mainNav.contains(e.target)) {
        var li = e.target.closest("li:has(> .menu-panel)");
        if (li) setActive(li);
      }
    });
    header.addEventListener("focusout", function (e) {
      if (!header.contains(e.relatedTarget) &&
          !(searchDrop && searchDrop.classList.contains("is-open"))) setActive(null);
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

  /* ---- 搜尋：與 mega dropdown 共用毛玻璃島體與高度動畫 ---- */

  function setSearch(open) {
    if (!searchDrop) return;
    if (open && typeof setActive === "function") setActive(null);
    searchDrop.classList.toggle("is-open", open);
    searchToggles.forEach(function (button) {
      button.setAttribute("aria-expanded", String(open));
    });
    if (typeof setMenuOpen === "function") setMenuOpen(open);
    if (open && typeof openPanel === "function") openPanel(searchDrop);
    if (!open && typeof closePanel === "function") closePanel(searchDrop);
    if (open) {
      var input = searchDrop.querySelector("input[type='search']");
      if (input) setTimeout(function () { input.focus(); }, 360);
    }
  }
  if (searchDrop && searchToggles.length) {
    searchToggles.forEach(function (button) {
      button.addEventListener("click", function () {
        setSearch(!searchDrop.classList.contains("is-open"));
      });
    });
    searchDrop.addEventListener("click", function (event) {
      if (event.target.closest("[data-search-close]")) setSearch(false);
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && searchDrop.classList.contains("is-open")) {
        setSearch(false);
        var visibleToggle = Array.from(searchToggles).find(function (button) {
          return button.offsetParent !== null;
        });
        if (visibleToggle) visibleToggle.focus();
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

  /* ---- Segment 膠囊切換（共用元件）----
     用法：<div class="segment"><button class="segment-btn" data-value="…"
     aria-pressed="true|false">…</button>…</div>
     指示膠囊由此注入並滑動到選中項；切換時對 .segment 發
     CustomEvent "segment:change"（detail.value＝選中的 data-value）。 */
  document.querySelectorAll(".segment").forEach(function (segment) {
    var buttons = Array.prototype.slice.call(segment.querySelectorAll(".segment-btn"));
    if (!buttons.length) return;

    var thumb = document.createElement("span");
    thumb.className = "segment-thumb";
    thumb.setAttribute("aria-hidden", "true");
    segment.insertBefore(thumb, segment.firstChild);

    function activeButton() {
      return segment.querySelector('.segment-btn[aria-pressed="true"]') || buttons[0];
    }

    function moveThumb(button) {
      thumb.style.width = button.offsetWidth + "px";
      thumb.style.height = button.offsetHeight + "px";
      thumb.style.transform =
        "translate(" + button.offsetLeft + "px, " + button.offsetTop + "px)";
      segment.classList.toggle(
        "is-thumb-solid",
        button.getAttribute("data-thumb") === "solid"
      );
    }

    /* 先定位再開啟 transition（.is-ready），初始定位才不會播滑動動畫 */
    moveThumb(activeButton());
    window.requestAnimationFrame(function () {
      segment.classList.add("is-ready");
    });
    window.addEventListener("resize", function () {
      moveThumb(activeButton());
    });

    segment.addEventListener("click", function (event) {
      var button = event.target.closest(".segment-btn");
      if (!button || button.getAttribute("aria-pressed") === "true") return;
      buttons.forEach(function (other) {
        other.setAttribute("aria-pressed", String(other === button));
      });
      moveThumb(button);
      if (button.scrollIntoView) {
        button.scrollIntoView({
          behavior: reduceMotion ? "auto" : "smooth",
          block: "nearest",
          inline: "nearest",
        });
      }
      segment.dispatchEvent(
        new CustomEvent("segment:change", {
          detail: { value: button.getAttribute("data-value") },
        })
      );
    });
  });

  /* ---- 洞察分類篩選（淡出→切換→淡入，約 350ms）：訂閱 filter-bar 的 segment ---- */
  var insightCards = document.querySelectorAll(".insight-card");
  var insightGrid = document.querySelector(".insights-grid");
  var filterTimer = null;
  var gridResizeTimer = null;

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
    filterTimer = window.setTimeout(function () {
      /* 卡片數改變會讓格線高度瞬跳、下方內容抖動→鎖高補間 0.28s */
      var startHeight = insightGrid ? insightGrid.offsetHeight : 0;
      swap();
      if (!insightGrid) return;
      window.clearTimeout(gridResizeTimer);
      insightGrid.style.height = "";
      var endHeight = insightGrid.offsetHeight;
      if (endHeight === startHeight) return;
      insightGrid.classList.add("is-resizing");
      insightGrid.style.height = startHeight + "px";
      void insightGrid.offsetHeight; /* 強制 reflow，讓起點高度生效 */
      insightGrid.style.height = endHeight + "px";
      gridResizeTimer = window.setTimeout(function () {
        insightGrid.classList.remove("is-resizing");
        insightGrid.style.height = "";
      }, 320);
    }, 200);
  }

  /* ---- 示意表單：阻止送出跳頁 ---- */
  document.querySelectorAll("form").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
    });
  });

  document.querySelectorAll(".filter-bar .segment").forEach(function (segment) {
    segment.addEventListener("segment:change", function (event) {
      applyFilter(event.detail.value);
    });
  });
})();
