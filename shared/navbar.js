(function () {
  "use strict";

  var navigation = [
    {
      href: "about.html",
      label: "關於 TIRI",
      columns: [
        {
          label: "協會",
          links: [
            ["about.html", "協會使命", "創會緣起、願景與協會定位"],
            ["team2026.html", "第三屆理監事成員", "現任理監事名單"],
            ["board.html", "歷屆理監事", "第一屆至第三屆名冊"],
            ["about.html#committee", "功能委員會", "各功能委員會的組成"]
          ]
        },
        {
          label: "服務與認證",
          links: [
            ["services.html", "功能與服務", "培訓、證照、評鑑、研究調查等 12 項服務"],
            ["certificate.html", "鄧白氏企業認證™", "D-U-N-S® 環球編碼 65-851-5060"]
          ]
        }
      ],
      figure: ["about.html", "../images/hero-annual-forum.jpg", "專為上市櫃、興櫃、公開發行與創櫃公司經理人而設的專業協會，致力推進台灣投資人關係的實踐。", "認識協會"]
    },
    {
      href: "events.html",
      label: "活動課程",
      columns: [
        {
          label: "活動與獎項",
          links: [
            ["events.html", "焦點與近期課程", "年度大會、專業課程與國際證照總覽"],
            ["news-971146.html", "精彩回顧", "歷屆年度大會與活動紀錄"],
            ["mission-206783.html", "TIRI Awards", "第五屆投票啟動，邀請投資圈與媒體參與"],
            ["mission-206783-766399.html", "TIRI 潛力進展獎", "表揚中小型企業的 IR 進步標竿"]
          ]
        },
        {
          label: "專業課程與證照",
          links: [
            ["tiric.html", "TIRIC IR 專業實戰班", "採 NIRI 授權教材繁體中文版"],
            ["trainbod.html", "董監事進修課程", "可折抵董監事與公司治理主管進修時數"],
            ["certification.html", "IRC 國際證照", "NIRI 專業證照，會員報名省 200 美元"],
            ["scholarshipirc.html", "IRC 贊助獎學金", "填寫申請表取得贊助資格"]
          ]
        }
      ],
      figure: ["news-971146.html", "../images/event-2025-conference.jpg", "2025 年度大會以「智慧驅動未來，IR 共創新時代」為題，呼應數位轉型與 AI 對資本市場的影響。", "查看年度大會"]
    },
    {
      href: "knowledge.html",
      label: "知識資源",
      columns: [
        {
          label: "刊物與專欄",
          links: [
            ["knowledge.html", "知識總覽", "專欄、精選文章與專訪的完整入口"],
            ["news-387131-325944.html", "證券雙月刊專欄", "證交所「證券服務雙月刊」歷期專欄"],
            ["5th_report-516844.html", "TIRI 年刊", "創始於 2024 年，每年出刊一次"]
          ]
        },
        {
          label: "文章與專訪",
          links: [
            ["news-387131-325944-831518.html", "專文分享", "會員與講者的主題分享文章"],
            ["irupdatestc.html", "NIRI IR Update 精選", "2019–2020 與 NIRI 合作中文化的精選文章"],
            ["2356035370-277843933339333297022010738263.html", "專訪 沈馥馥理事長", "專訪中華電信代理發言人沈馥馥協理"]
          ]
        }
      ],
      figure: ["knowledge.html", "../images/hero-talk.jpg", "證交所「證券服務雙月刊」專欄、NIRI IR Update 精選、專文與專訪──台灣 IR 的知識庫。", "前往知識資源"]
    },
    {
      href: "membership.html",
      label: "會員服務",
      columns: [
        {
          label: "會員",
          links: [
            ["membership.html", "會員類別與會費", "個人與團體會員的類別與費用"],
            ["benefit.html", "會員專屬優惠", "課程、證照與治理服務的專屬折扣"],
            ["join.html", "加入會員", "申請流程、入會表單與匯款資訊"]
          ]
        },
        {
          label: "治理服務",
          links: [
            ["bodperform.html", "董事會績效評估", "團體會員享 85 折優惠"],
            ["corpperform.html", "提升公司治理服務", "團體會員享 8 折優惠"]
          ]
        }
      ],
      figure: ["join.html", "../images/hero-handshake.jpg", "個人首次入會 NT$8,000（入會費 2,000＋常年會費 6,000），隔年起每年 NT$6,000。", "加入會員"]
    },
    {
      href: "news.html",
      label: "最新消息",
      columns: [
        {
          label: "消息",
          links: [
            ["news.html", "協會消息", "協會公告、課程講座與產業參與紀錄"],
            ["news-971146.html", "精彩回顧", "歷屆年度大會與活動現場紀錄"]
          ]
        },
        { label: "", links: [] }
      ],
      figure: ["news-971146.html", "../images/hero-recap.jpg", "2025/10/23　2025 年度大會暨引領 IR 智慧新時代", "看活動回顧"]
    },
    {
      href: "partners.html",
      label: "合作夥伴",
      columns: [
        {
          label: "夥伴與贊助",
          links: [
            ["partners.html", "合作夥伴總覽", "年度大會贊助單位與會員優惠夥伴"],
            ["partners.html#sponsor", "贊助方案", "企業贊助方案說明"],
            ["contact.html", "聯絡我們", "(02) 2381-9248・台北市中正區重慶南路一段 57 號"]
          ]
        },
        { label: "", links: [] }
      ],
      figure: ["partners.html#sponsor", "../images/hero-networking.jpg", "年度大會贊助單位、會員專屬優惠合作夥伴，以及企業贊助方案。", "成為合作夥伴"]
    }
  ];

  var drawerLinks = [
    ["關於 TIRI", "about.html", [["about.html", "協會使命"], ["team2026.html", "第三屆理監事成員"], ["board.html", "歷屆理監事"], ["about.html#committee", "功能委員會"], ["services.html", "功能與服務"], ["certificate.html", "鄧白氏企業認證™"]]],
    ["活動課程", "events.html", [["events.html", "焦點與近期課程"], ["news-971146.html", "精彩回顧"], ["tiric.html", "TIRIC IR 專業實戰班"], ["trainbod.html", "董監事進修課程"], ["certification.html", "IRC 國際證照"], ["scholarshipirc.html", "IRC 贊助獎學金"], ["mission-206783.html", "TIRI Awards"], ["mission-206783-766399.html", "TIRI 潛力進展獎"]]],
    ["知識資源", "knowledge.html", [["knowledge.html", "知識總覽"], ["news-387131-325944-831518.html", "專文分享"], ["news-387131-325944.html", "證券雙月刊專欄"], ["irupdatestc.html", "NIRI IR Update 精選"], ["2356035370-277843933339333297022010738263.html", "專訪 沈馥馥理事長"], ["5th_report-516844.html", "TIRI 年刊"]]],
    ["會員服務", "membership.html", [["membership.html", "會員類別與會費"], ["benefit.html", "會員專屬優惠"], ["bodperform.html", "董事會績效評估"], ["corpperform.html", "提升公司治理服務"], ["join.html", "加入會員"]]],
    ["最新消息", "news.html", [["news.html", "協會消息"], ["news-971146.html", "精彩回顧"]]],
    ["合作夥伴", "partners.html", [["partners.html", "合作夥伴總覽"], ["partners.html#sponsor", "贊助方案"], ["contact.html", "聯絡我們"]]]
  ];

  function icon(id, size) {
    return '<svg class="icon" width="' + size + '" height="' + size + '" viewBox="0 0 24 24" aria-hidden="true"><use href="#' + id + '"></use></svg>';
  }

  function renderColumns(columns) {
    return columns.map(function (column) {
      var heading = column.label ? '<span class="mega-overline">' + column.label + '</span>' : "";
      var links = column.links.map(function (link) {
        return '<a class="mega-item" href="' + link[0] + '"><span class="t">' + link[1] + '</span><span class="d">' + link[2] + '</span></a>';
      }).join("");
      return '<div class="mega-col">' + heading + links + '</div>';
    }).join("");
  }

  function renderDesktopNav() {
    return navigation.map(function (item) {
      var figure = item.figure;
      return '<li><a href="' + item.href + '">' + item.label + '</a>' +
        '<div class="menu-panel"><div class="mega-inner">' + renderColumns(item.columns) +
        '<a class="mega-figure" href="' + figure[0] + '">' +
        '<img src="' + figure[1] + '" alt="" loading="lazy" width="380" height="176">' +
        '<span class="cap">' + figure[2] + '</span><span class="cta">' + figure[3] + ' <span aria-hidden="true">→</span></span>' +
        '</a></div></div></li>';
    }).join("");
  }

  function renderDrawer() {
    return drawerLinks.map(function (item) {
      var subs = item[2].map(function (link) {
        return '<a href="' + link[0] + '">' + link[1] + '</a>';
      }).join("");
      return '<li><a class="d-main" href="' + item[1] + '">' + item[0] + ' <span class="arrow" aria-hidden="true">→</span></a><div class="subs">' + subs + '</div></li>';
    }).join("");
  }

  function renderSocialIcons() {
    var links = [
      ["https://www.facebook.com/tiri2018/", "Facebook", "i-facebook"],
      ["https://www.linkedin.com/company/taiwan-investor-relations-institute-tiri-%E5%8F%B0%E7%81%A3%E6%8A%95%E8%B3%87%E4%BA%BA%E9%97%9C%E4%BF%82%E5%8D%94%E6%9C%83/", "LinkedIn", "i-linkedin"],
      ["https://lin.ee/AcTa5dh", "LINE", "i-line"],
      ["https://www.youtube.com/@officetiri6311", "YouTube", "i-youtube"],
      ["mailto:office@tiri.tw", "Email", "i-mail"]
    ];
    return links.map(function (link) {
      var external = link[0].indexOf("http") === 0 ? ' target="_blank" rel="noopener"' : "";
      return '<a href="' + link[0] + '"' + external + ' aria-label="' + link[1] + '"><span class="roll">' + icon(link[2], 16) + icon(link[2], 16) + '</span></a>';
    }).join("");
  }

  function renderHeaderTop() {
    return '<nav class="header-top" aria-label="工具列">' +
      '<button class="search-toggle" type="button" aria-expanded="false" aria-controls="search-panel">' + icon("i-search", 15) + '搜尋</button>' +
      '<span class="divider" aria-hidden="true"></span><a href="login.html">會員登入</a>' +
      '<span class="divider" aria-hidden="true"></span><span class="social-icons">' + renderSocialIcons() + '</span></nav>';
  }

  function renderActions(variant) {
    var tools = variant === "v2"
      ? '<button class="search-toggle" type="button" aria-expanded="false" aria-controls="search-panel" aria-label="搜尋">' + icon("i-search", 17) + '</button><a class="login-link" href="login.html">登入</a>'
      : "";
    return '<div class="header-actions">' + tools +
      '<a class="btn btn-primary btn-cta-desktop" href="join.html"><span class="roll"><span>加入會員</span><span aria-hidden="true">加入會員</span></span></a>' +
      '<button class="nav-toggle" type="button" aria-expanded="false" aria-controls="drawer" aria-label="開啟選單"><span class="bar" aria-hidden="true"></span><span class="bar" aria-hidden="true"></span><span class="bar" aria-hidden="true"></span></button></div>';
  }

  function renderComponent(variant) {
    return '<header class="site-header" id="site-header"><div class="container">' +
      '<a class="wordmark" href="index.html" aria-label="TIRI 台灣投資人關係協會 首頁"><span class="mark" aria-hidden="true">TI<span>RI</span></span><span class="name">台灣投資人關係協會</span></a>' +
      '<div class="header-right">' + (variant === "v1" ? renderHeaderTop() : "") +
      '<div class="header-main"><nav class="main-nav" aria-label="主導覽"><ul>' + renderDesktopNav() + '</ul></nav>' + renderActions(variant) + '</div></div></div>' +
      '<div class="search-drop" id="search-panel"><div class="search-backdrop" data-search-close></div><div class="search-sheet"><div class="container">' +
      '<form data-demo-form role="search" aria-label="站內搜尋"><label class="sr-only" for="site-search-input">關鍵字</label><input id="site-search-input" type="search" name="q" placeholder="搜尋課程、活動、文章…"><button class="search-close" type="button" data-search-close aria-label="關閉搜尋">' + icon("i-x", 14) + '</button><button class="btn btn-primary" type="submit">搜尋</button></form>' +
      '</div></div></div></header>' +
      '<div class="drawer" id="drawer"><div class="drawer-backdrop" data-drawer-close></div><div class="drawer-panel" role="dialog" aria-modal="true" aria-label="行動選單"><nav aria-label="行動導覽"><ul>' + renderDrawer() + '</ul></nav>' +
      '<div class="drawer-cta"><a class="btn btn-primary" href="join.html">加入會員</a><a class="btn btn-outline" href="login.html">會員登入</a></div></div></div>';
  }

  function markCurrentPage(root) {
    var current = window.location.pathname.split("/").pop() || "index.html";
    root.querySelectorAll('a[href]').forEach(function (link) {
      var target = link.getAttribute("href").split("#")[0];
      if (target === current) link.setAttribute("aria-current", "page");
    });
  }

  class TiriNavbar extends HTMLElement {
    connectedCallback() {
      if (this.dataset.ready === "true") return;
      var variant = this.getAttribute("variant") === "v1" ? "v1" : "v2";
      this.style.display = "contents";
      this.innerHTML = renderComponent(variant);
      this.dataset.ready = "true";
      markCurrentPage(this);
    }
  }

  if (!customElements.get("tiri-navbar")) {
    customElements.define("tiri-navbar", TiriNavbar);
  }
})();
