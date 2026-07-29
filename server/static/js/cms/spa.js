// TIRI 收件後台 SPA 殼層（改寫自 JustGolf kit spa.js）：攔截 /admin 頁面連結 → fetch 整頁
// → 抽換 #main-content，側邊欄/header 永不重建，URL 用 history.pushState 同步。
// route 不改（伺服器仍回整頁），換頁淡入用既有 .is-spa-entered（b_admin.css）。
//
// 與 kit 版差異：
//   1. 本後台頁面 JS 全在 {% block extra_js %} 內聯（IIFE＋var，重跑安全），沒有 pageInit 註冊表
//      → 抽換後直接重新執行新頁 extra_js 區的 <script>（base.html 以註解標記包住該區塊）。
//   2. document 層級監聽器由 window.PageSignal（AbortController）管理：
//      換頁前 abort 舊頁、執行新頁 script 前換新 signal，頁面腳本自行帶 { signal } 註冊。
//   3. 側欄 active／收件數：讀取新頁 #nav-data JSON 更新 Vue 殼層（window.__aApp）。
(function () {
  var MAIN = '#main-content';
  var PREFIX = '/admin';
  var CSS_START = 'b-spa-extra-css-start';
  var CSS_END = 'b-spa-extra-css-end';
  var JS_START = 'b-spa-extra-js-start';
  var JS_END = 'b-spa-extra-js-end';
  var MANAGED_ATTR = 'data-spa-managed';

  // spa.js 自己追蹤「目前 DOM 載入的 path」，popstate 用來判斷是否真的換了頁（僅 query 變不算）
  var lastPath = location.pathname;

  function normPath(p) {
    return String(p || '').split('?')[0].split('#')[0].replace(/\/+$/, '');
  }
  function samePath(a, b) { return normPath(a) === normPath(b); }

  // ---- 標記區塊掃描：回傳 head/body 中夾在 <!-- start -->…<!-- end --> 間的元素 ----
  function nodesBetweenMarkers(root, startMark, endMark) {
    var nodes = [];
    var inBlock = false;
    Array.prototype.forEach.call((root && root.childNodes) || [], function (node) {
      if (node.nodeType === 8) {
        var marker = (node.nodeValue || '').trim();
        if (marker === startMark) { inBlock = true; return; }
        if (marker === endMark) { inBlock = false; return; }
      }
      if (inBlock && node.nodeType === 1) nodes.push(node);
    });
    return nodes;
  }

  // ---- 頁專屬 CSS（extra_css）：初載標記，換頁時整批移除再從新頁複製 ----
  function markInitialExtraCss() {
    nodesBetweenMarkers(document.head, CSS_START, CSS_END).forEach(function (node) {
      node.setAttribute(MANAGED_ATTR, 'css');
    });
  }
  function syncExtraCss(doc) {
    document.head.querySelectorAll('[' + MANAGED_ATTR + '="css"]').forEach(function (n) { n.remove(); });
    nodesBetweenMarkers(doc.head, CSS_START, CSS_END).forEach(function (node) {
      var clone = node.cloneNode(true);
      clone.setAttribute(MANAGED_ATTR, 'css');
      document.head.appendChild(clone);
    });
  }

  // ---- 頁專屬 JS（extra_js）：移除上一頁注入的，逐一以新 <script> 重建執行 ----
  function runExtraJs(doc) {
    document.body.querySelectorAll('[' + MANAGED_ATTR + '="js"]').forEach(function (n) { n.remove(); });
    nodesBetweenMarkers(doc.body, JS_START, JS_END).forEach(function (node) {
      if (node.tagName !== 'SCRIPT') return;
      var s = document.createElement('script');
      if (node.src) s.src = node.src;
      s.textContent = node.textContent;
      s.setAttribute(MANAGED_ATTR, 'js');
      document.body.appendChild(s);   // 內聯 script 附加即同步執行
    });
  }

  // ---- 頁生命週期：document 層級監聽器全帶 window.PageSignal 註冊，換頁前一刀 abort ----
  function resetPageSignal() {
    if (window.__pageCtl) { try { window.__pageCtl.abort(); } catch (e) {} }
    window.__pageCtl = new AbortController();
    window.PageSignal = window.__pageCtl.signal;
  }

  // ---- 殼層增強（新內容進 DOM 後）：icon 重繪＋kit 下拉重掛 ----
  function reEnhance(main) {
    if (window.renderLucideIcons) window.renderLucideIcons();
    if (window.BDropdown) window.BDropdown.init(main || document);
  }

  // ---- 側欄同步：讀新頁 #nav-data（nav 連同收件數、active key）更新 Vue 殼層 ----
  function syncNav(doc) {
    var app = window.__aApp;
    var dataEl = doc.getElementById('nav-data');
    if (!app || !dataEl) return;
    var data;
    try { data = JSON.parse(dataEl.textContent); } catch (e) { return; }
    app.navMenu = data.nav || [];
    app.activeKey = data.active || '';
    // 比照整頁載入的 created()：只展開含當前頁的群組（手風琴 single-open）
    var open = {};
    app.navMenu.forEach(function (m, i) {
      if (m.sub && m.sub.some(function (s) { return s.key === app.activeKey; })) open[i] = true;
    });
    app.openMenus = open;
    app.flyout.open = false;
  }

  // ---- 核心：抽換 #main-content ----
  function applyMain(html, url) {
    var doc = new DOMParser().parseFromString(html, 'text/html');
    var fresh = doc.querySelector(MAIN);
    var current = document.querySelector(MAIN);
    if (!fresh || !current || !doc.getElementById('nav-data')) return false;   // 非後台頁（如被導去登入）→ 降級

    // 離開舊頁：解除 document 層級監聽、清掉可能殘留的 modal 鎖捲動
    resetPageSignal();
    document.body.classList.remove('b-modal-lock');

    syncExtraCss(doc);
    current.className = fresh.className;
    current.innerHTML = fresh.innerHTML;

    // 換好淡入（克制過場）：加動畫 class，結束後移除以免影響後續
    current.classList.add('is-spa-entered');
    current.addEventListener('animationend', function onEnd() {
      current.classList.remove('is-spa-entered');
      current.removeEventListener('animationend', onEnd);
    });

    var freshTitle = doc.querySelector('title');
    if (freshTitle) document.title = freshTitle.textContent;

    // 側欄 active／收件數 → 新頁 extra_js 執行（會讀 location.search，pushState 已先行）→ 殼層增強
    syncNav(doc);
    runExtraJs(doc);
    reEnhance(current);

    // 捲回頂端（換頁語意）＋焦點移到主內容（無障礙；main 已 tabindex=-1）
    current.scrollTop = 0;
    try { window.scrollTo(0, 0); } catch (e) {}
    try { current.focus({ preventScroll: true }); } catch (e) {}
    try { lastPath = new URL(url || location.pathname, window.location.origin).pathname; }
    catch (e) { lastPath = location.pathname; }
    return true;
  }

  var navSeq = 0;   // 導航序號：慢的舊回應不得覆蓋使用者後來選的頁（點兩下/Back 競態）

  function navigate(url, push) {
    var seq = ++navSeq;
    // 延遲顯示載入態（變灰）：fetch 多半很快，180ms 內回來就完全不變灰 → 俐落無停頓感
    var loadingTimer = setTimeout(function () {
      var m = document.querySelector(MAIN);
      if (m) m.classList.add('is-spa-loading');
    }, 180);
    function clearLoading() {
      clearTimeout(loadingTimer);
      var m = document.querySelector(MAIN);
      if (m) m.classList.remove('is-spa-loading');
    }
    fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' }, credentials: 'same-origin' })
      .then(function (r) {
        // 被重導（如 session 過期導去登入頁）→ 整頁導航讓瀏覽器處理
        var target = new URL(url, window.location.origin);
        if (r.redirected && !samePath(new URL(r.url).pathname, target.pathname)) { window.location.href = url; return null; }
        return r.text();
      })
      .then(function (html) {
        if (html == null) return;
        if (seq !== navSeq) return;   // 已有更新的導航 → 丟棄舊回應
        // pushState 先於 applyMain：新頁 extra_js 會讀 location.search（如收件匣 ?form=）初始化
        if (push) history.pushState({ spa: true }, '', url);
        if (!applyMain(html, url)) { window.location.reload(); return; }  // 抽換失敗 → 降級整頁（URL 已更新）
      })
      .catch(function () { if (seq === navSeq) window.location.href = url; })  // 網路錯 → 降級
      .finally(clearLoading);
  }

  // ---- 判斷一個連結是否該由 SPA 接管 ----
  function shouldHandle(a, ev) {
    if (!a) return false;
    if (ev.defaultPrevented) return false;
    if (ev.button !== 0 || ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey) return false;
    if (a.target && a.target !== '' && a.target !== '_self') return false;       // _blank 等
    if (a.hasAttribute('download')) return false;
    if (a.dataset.noSpa !== undefined) return false;                              // 明確退出 SPA
    var href = a.getAttribute('href') || '';
    if (!href || href.charAt(0) === '#' || href.indexOf('javascript:') === 0) return false;
    var url;
    try { url = new URL(a.href, window.location.origin); } catch (e) { return false; }
    if (url.origin !== window.location.origin) return false;
    // 同源 + 後台頁面路徑（/admin…）才接管
    if (url.pathname !== PREFIX && url.pathname.indexOf(PREFIX + '/') !== 0) return false;
    // 非頁面路徑不接管：登入/登出、CSV 下載等帶副檔名的資源
    var tail = normPath(url.pathname).split('/').pop().toLowerCase();
    if (tail === 'login' || tail === 'logout' || tail.indexOf('.') !== -1) return false;
    // 同 path 僅 query 不同（頁內篩選）→ 不接管（頁面腳本自己處理）
    if (samePath(url.pathname, window.location.pathname) && url.search) return false;
    return true;
  }

  document.addEventListener('click', function (ev) {
    var a = ev.target.closest && ev.target.closest('a[href]');
    if (!shouldHandle(a, ev)) return;
    ev.preventDefault();
    var url = new URL(a.href, window.location.origin);
    // 點到目前頁本身（雙方都無 query）→ 略過；當前帶篩選 query 時點同頁 = 清除篩選，要真的導航
    if (samePath(url.pathname, location.pathname) && !url.search && !location.search) return;
    navigate(a.href, true);
  });

  // ---- 上一頁/下一頁：path 改變 → SPA 換頁；path 不變（僅 query，如篩選 pushState）→ 不處理 ----
  window.addEventListener('popstate', function () {
    if (!document.querySelector(MAIN)) return;
    if (samePath(location.pathname, lastPath)) return;
    navigate(location.pathname + location.search, false);
  });

  markInitialExtraCss();
  window.ASpa = { navigate: navigate };
})();
