(function () {
  "use strict";

  /* 第一層 1~8 對應共用資料夾「1首頁～8年刊下載」，分組沿用原站架構 */
  var navigation = [
    {
      href: "index.html",
      label: "首頁"
    },
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
          label: "服務與聯繫",
          links: [
            ["services.html", "功能與服務", "培訓、證照、評鑑、研究調查等 12 項服務"],
            ["certificate.html", "鄧白氏企業認證™", "D-U-N-S® 環球編碼 65-851-5060"],
            ["partners.html", "合作夥伴", "年度大會贊助單位與會員優惠夥伴"],
            ["contact.html", "聯絡我們", "(02) 2381-9248・台北市中正區重慶南路一段 57 號"]
          ]
        }
      ],
      figure: ["about.html", "../images/hero-annual-forum.jpg", "專為上市櫃、興櫃、公開發行與創櫃公司經理人而設的專業協會，致力推進台灣投資人關係的實踐。", "認識協會"]
    },
    {
      href: "news.html",
      label: "活動訊息",
      columns: [
        {
          label: "消息與活動",
          links: [
            ["news.html", "協會消息", "協會公告、課程講座與產業參與紀錄"],
            ["events.html", "近期活動", "即將登場的大會、課程與講座"]
          ]
        },
        {
          label: "回顧",
          links: [
            ["news-971146.html", "精彩回顧", "歷屆年度大會與活動現場紀錄"]
          ]
        }
      ],
      figure: ["news-971146.html", "../images/hero-recap.jpg", "2025/10/23　2025 年度大會暨引領 IR 智慧新時代", "看活動回顧"]
    },
    {
      href: "trainbod.html",
      label: "課程與服務",
      columns: [
        {
          label: "進修課程",
          links: [
            ["trainbod.html", "董監事進修課程", "可折抵董監事與公司治理主管進修時數"],
            ["trainbod-384680.html", "會計主管進修班", "會計主管繼續進修課程分享"]
          ]
        },
        {
          label: "治理服務",
          links: [
            ["bodperform.html", "董事會績效評估", "外部評估服務，團體會員享 85 折"],
            ["corpperform.html", "提升公司治理服務", "團體會員享 8 折優惠"]
          ]
        }
      ],
      figure: ["trainbod.html", "../images/seminar-room.jpg", "董監事進修、董事會績效評估與提升公司治理──協會的核心課程與治理服務。", "查看課程"]
    },
    {
      href: "certification.html",
      label: "證照獎項",
      columns: [
        {
          label: "專業證照",
          links: [
            ["certification.html", "IRC 國際證照", "NIRI 專業證照，會員報名省 200 美元"],
            ["scholarshipirc.html", "IRC 贊助獎學金", "填寫申請表取得贊助資格"],
            ["tiric.html", "TIRIC IR 專業實戰班", "採 NIRI 授權教材繁體中文版"]
          ]
        },
        {
          label: "獎項",
          links: [
            ["mission-206783.html", "TIRI Awards", "第五屆投票啟動，邀請投資圈與媒體參與"],
            ["mission-206783-766399.html", "TIRI 潛力進展獎", "表揚中小型企業的 IR 進步標竿"]
          ]
        }
      ],
      figure: ["certification.html", "../images/event-awards.jpg", "IRC 國際證照與 TIRI Awards──IR 專業能力與企業成就的雙重肯定。", "了解 IRC 證照"]
    },
    {
      href: "knowledge.html",
      label: "專業分享",
      columns: [
        {
          label: "刊物與專欄",
          links: [
            ["knowledge.html", "知識總覽", "專欄、精選文章與專訪的完整入口"],
            ["news-387131-325944.html", "證券雙月刊專欄", "證交所「證券服務雙月刊」歷期專欄"]
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
      figure: ["knowledge.html", "../images/hero-talk.jpg", "證交所「證券服務雙月刊」專欄、NIRI IR Update 精選、專文與專訪──台灣 IR 的知識庫。", "前往專業分享"]
    },
    {
      href: "membership.html",
      label: "會員中心",
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
          label: "贊助機制",
          links: [
            ["partners.html#sponsor", "贊助方案", "企業贊助方案說明"]
          ]
        }
      ],
      figure: ["join.html", "../images/hero-handshake.jpg", "個人首次入會 NT$8,000（入會費 2,000＋常年會費 6,000），隔年起每年 NT$6,000。", "加入會員"]
    },
    {
      href: "5th_report-516844.html",
      label: "年刊下載",
      columns: [
        {
          label: "歷年年刊",
          links: [
            ["5th_report-516844.html", "年刊簡介", "創始於 2024 年，每年出刊一次"],
            ["5th_report.html", "5 周年年刊", "協會成立五周年年刊"],
            ["5th_report-848158.html", "6 周年年刊", "協會成立六周年年刊"],
            ["7th_report-848158-214091.html", "7 周年年刊", "協會成立七周年年刊"]
          ]
        },
        { label: "", links: [] }
      ],
      figure: ["5th_report-516844.html", "../images/hero-chart.jpg", "TIRI 年刊收錄年度活動成果與 IR 觀點，線上閱覽與下載。", "下載年刊"]
    }
  ];

  var drawerLinks = [
    ["首頁", "index.html", []],
    ["關於 TIRI", "about.html", [["about.html", "協會使命"], ["team2026.html", "第三屆理監事成員"], ["board.html", "歷屆理監事"], ["about.html#committee", "功能委員會"], ["services.html", "功能與服務"], ["certificate.html", "鄧白氏企業認證™"], ["partners.html", "合作夥伴"], ["contact.html", "聯絡我們"]]],
    ["活動訊息", "news.html", [["news.html", "協會消息"], ["events.html", "近期活動"], ["news-971146.html", "精彩回顧"]]],
    ["課程與服務", "trainbod.html", [["trainbod.html", "董監事進修課程"], ["trainbod-384680.html", "會計主管進修班"], ["bodperform.html", "董事會績效評估"], ["corpperform.html", "提升公司治理服務"]]],
    ["證照獎項", "certification.html", [["certification.html", "IRC 國際證照"], ["scholarshipirc.html", "IRC 贊助獎學金"], ["tiric.html", "TIRIC IR 專業實戰班"], ["mission-206783.html", "TIRI Awards"], ["mission-206783-766399.html", "TIRI 潛力進展獎"]]],
    ["專業分享", "knowledge.html", [["knowledge.html", "知識總覽"], ["news-387131-325944.html", "證券雙月刊專欄"], ["news-387131-325944-831518.html", "專文分享"], ["irupdatestc.html", "NIRI IR Update 精選"], ["2356035370-277843933339333297022010738263.html", "專訪 沈馥馥理事長"]]],
    ["會員中心", "membership.html", [["membership.html", "會員類別與會費"], ["benefit.html", "會員專屬優惠"], ["join.html", "加入會員"], ["partners.html#sponsor", "贊助方案"]]],
    ["年刊下載", "5th_report-516844.html", [["5th_report-516844.html", "年刊簡介"], ["5th_report.html", "5 周年年刊"], ["5th_report-848158.html", "6 周年年刊"], ["7th_report-848158-214091.html", "7 周年年刊"]]]
  ];

  /* 英文版導覽：頁面沿用 Weebly 原站英文選單的 40 頁（檔名多為數字尾碼，非 _en），
     分組照原站英文選單層級，重排成與中文版一致的 mega-menu 結構 */
  var navigationEn = [
    {
      href: "en.html",
      label: "Home"
    },
    {
      href: "mission_en.html",
      label: "About TIRI",
      columns: [
        {
          label: "Institute",
          links: [
            ["mission_en.html", "About TIRI", "Mission, vision and objectives"],
            ["team_en-2026.html", "Third Board of Directors", "Current board members"],
            ["team_en-2018.html", "First Board of Directors", "Founding board members"],
            ["team_en-2022.html", "Second Board of Directors", "Second-term board members"],
            ["committee-817915.html", "Functional Committee", "Committee organization"]
          ]
        },
        {
          label: "Services & Contact",
          links: [
            ["services_en.html", "Functions and Services", "Training, certification, evaluation and research"],
            ["contact-197913.html", "Contact", "(02) 2381-9248・office@tiri.tw"]
          ]
        }
      ],
      figure: ["mission_en.html", "../images/hero-annual-forum.jpg", "A professional institute dedicated to advancing investor relations practice in Taiwan.", "About TIRI"]
    },
    {
      href: "news-971146-722067.html",
      label: "Recap",
      columns: [
        {
          label: "Recap",
          links: [
            ["news-971146-722067.html", "Event Recap", "Highlights from past annual conferences"],
            ["seminar181023-720761-875714-576604-415060-555931-912810-913907-187124.html", "2025 Annual Conference", "Leading a Smart New Era of IR"],
            ["seminar181023-720761-875714-576604-415060-555931-882088-817291.html", "2024 Annual Conference", "Global Vision: Co-Creating a New Era for IR"],
            ["seminar181023-720761-875714-576604-415060-555931-882088.html", "2023 Annual Conference", "Annual Conference and International Forum"]
          ]
        },
        {
          label: "Earlier Conferences",
          links: [
            ["seminar181023-720761-875714-576604-415060.html", "2022 Annual Conference", "Annual Conference and International Forum"],
            ["seminar181023-720761-875714-576604.html", "2021 Annual Conference", "The Future of ESG is NOW"],
            ["seminar181023-720761-875714.html", "2020 Annual Conference", "Launch Ceremony of TIRI IR Awards"],
            ["seminar181023-720761.html", "2019 Annual Conference", "Asia Investor Relations Connection"],
            ["seminar181023.html", "2018 Inaugural Conference", "Inaugural Conference and Master Forum"]
          ]
        }
      ],
      figure: ["news-971146-722067.html", "../images/hero-recap.jpg", "2025/10/23　2025 Annual Conference: Leading a Smart New Era of IR", "View Recap"]
    },
    {
      href: "trainbod-329824.html",
      label: "Courses & Services",
      columns: [
        {
          label: "Continuing Education",
          links: [
            ["trainbod-329824.html", "Board Member & CG Officer Education", "Continuing education for board members and corporate governance officers"],
            ["trainbod-384680-716109.html", "Accounting Executives Course", "Course sharing: continuing education for accounting executives"]
          ]
        },
        {
          label: "Governance Services",
          links: [
            ["bodperform-583064.html", "Board Performance Evaluation", "External board performance evaluation service"],
            ["corpperform-750901.html", "Corporate Governance Service", "Service for enhancing corporate governance"]
          ]
        }
      ],
      figure: ["trainbod-329824.html", "../images/seminar-room.jpg", "Continuing education, board evaluation and corporate governance services.", "View Courses"]
    },
    {
      href: "certification-388672.html",
      label: "Certification & Awards",
      columns: [
        {
          label: "Certification",
          links: [
            ["certification-388672.html", "IRC©", "NIRI's international investor relations certification"],
            ["scholarshipirc-952540.html", "Sponsor for IRC©", "Sponsorship for IRC© candidates"],
            ["tiric-677070.html", "TIRI Elite Program", "Executive-level IR practical elite program"]
          ]
        },
        {
          label: "Awards",
          links: [
            ["mission-206783-396345-512343.html", "Awards Overview", "About the TIRI award programs"],
            ["mission-206783-803349.html", "TIRI Awards", "Annual investor relations awards"],
            ["mission-206783-766399-942925.html", "TIRI Progress Achievement Award", "Recognizing IR progress of small and mid-cap companies"]
          ]
        }
      ],
      figure: ["certification-388672.html", "../images/event-awards.jpg", "IRC© certification and TIRI Awards — recognition for IR professionals and companies.", "About IRC©"]
    },
    {
      href: "news-387131-325944-831518-306343.html",
      label: "IR Library",
      columns: [
        {
          label: "Publications",
          links: [
            ["news-387131-325944-897961.html", "TWSE BIMONTHLY", "Columns from the TWSE Securities Service bimonthly"],
            ["irupdatestc-146678.html", "NIRI Selected", "Selected articles from NIRI IR Update"]
          ]
        },
        {
          label: "Articles & Interviews",
          links: [
            ["news-387131-325944-831518-306343.html", "Article Sharing", "Articles from members and speakers"],
            ["exclusive-interview-ndash-founding-chairman-fu-fu-shen.html", "Exclusive Interview", "Founding Chairman Fu-Fu Shen"]
          ]
        }
      ],
      figure: ["news-387131-325944-831518-306343.html", "../images/hero-talk.jpg", "Columns, selected articles and interviews — Taiwan's IR knowledge base.", "Visit IR Library"]
    },
    {
      href: "membership-567311.html",
      label: "Membership",
      columns: [
        {
          label: "Membership",
          links: [
            ["membership-567311.html", "Membership", "Membership categories and fees"],
            ["membership-249817-957999.html", "Membership Service", "Services for TIRI members"],
            ["benefit-499886.html", "Membership Benefits", "Discounts on courses, certification and services"],
            ["join-342161.html", "Join TIRI", "Application process and membership form"]
          ]
        },
        { label: "", links: [] }
      ],
      figure: ["join-342161.html", "../images/hero-handshake.jpg", "Join TIRI and enjoy member benefits across courses, certification and services.", "Join TIRI"]
    },
    {
      href: "5th_report-665763.html",
      label: "Anniversary",
      columns: [
        {
          label: "Anniversary Reports",
          links: [
            ["5th_report-665763.html", "Anniversary", "TIRI anniversary annual reports"],
            ["5th_report-665763-570037-605322.html", "5th Anniversary", "5th anniversary annual report"],
            ["6th_report-665763-570037.html", "6th Anniversary", "6th anniversary annual report"],
            ["7th_report-665763-570037-304514.html", "7th Anniversary", "7th anniversary annual report"]
          ]
        },
        { label: "", links: [] }
      ],
      figure: ["5th_report-665763.html", "../images/hero-chart.jpg", "TIRI anniversary reports — annual activities and IR insights, read online or download.", "View Reports"]
    }
  ];

  var drawerLinksEn = [
    ["Home", "en.html", []],
    ["About TIRI", "mission_en.html", [["mission_en.html", "About TIRI"], ["team_en-2026.html", "Third Board of Directors"], ["team_en-2018.html", "First Board of Directors"], ["team_en-2022.html", "Second Board of Directors"], ["committee-817915.html", "Functional Committee"], ["services_en.html", "Functions and Services"], ["contact-197913.html", "Contact"]]],
    ["Recap", "news-971146-722067.html", [["news-971146-722067.html", "Event Recap"], ["seminar181023-720761-875714-576604-415060-555931-912810-913907-187124.html", "2025 Annual Conference"], ["seminar181023-720761-875714-576604-415060-555931-882088-817291.html", "2024 Annual Conference"], ["seminar181023-720761-875714-576604-415060-555931-882088.html", "2023 Annual Conference"], ["seminar181023-720761-875714-576604-415060.html", "2022 Annual Conference"], ["seminar181023-720761-875714-576604.html", "2021 Annual Conference"], ["seminar181023-720761-875714.html", "2020 Annual Conference"], ["seminar181023-720761.html", "2019 Annual Conference"], ["seminar181023.html", "2018 Inaugural Conference"]]],
    ["Courses & Services", "trainbod-329824.html", [["trainbod-329824.html", "Board Member & CG Officer Education"], ["trainbod-384680-716109.html", "Accounting Executives Course"], ["bodperform-583064.html", "Board Performance Evaluation"], ["corpperform-750901.html", "Corporate Governance Service"]]],
    ["Certification & Awards", "certification-388672.html", [["certification-388672.html", "IRC©"], ["scholarshipirc-952540.html", "Sponsor for IRC©"], ["tiric-677070.html", "TIRI Elite Program"], ["mission-206783-396345-512343.html", "Awards Overview"], ["mission-206783-803349.html", "TIRI Awards"], ["mission-206783-766399-942925.html", "TIRI Progress Achievement Award"]]],
    ["IR Library", "news-387131-325944-831518-306343.html", [["news-387131-325944-897961.html", "TWSE BIMONTHLY"], ["irupdatestc-146678.html", "NIRI Selected"], ["news-387131-325944-831518-306343.html", "Article Sharing"], ["exclusive-interview-ndash-founding-chairman-fu-fu-shen.html", "Exclusive Interview"]]],
    ["Membership", "membership-567311.html", [["membership-567311.html", "Membership"], ["membership-249817-957999.html", "Membership Service"], ["benefit-499886.html", "Membership Benefits"], ["join-342161.html", "Join TIRI"]]],
    ["Anniversary", "5th_report-665763.html", [["5th_report-665763.html", "Anniversary"], ["5th_report-665763-570037-605322.html", "5th Anniversary"], ["6th_report-665763-570037.html", "6th Anniversary"], ["7th_report-665763-570037-304514.html", "7th Anniversary"]]]
  ];

  /* 介面文字（依頁面語言切換；連結資料另見 navigation / navigationEn） */
  var uiStrings = {
    zh: {
      homeHref: "index.html",
      wordmarkLabel: "TIRI 台灣投資人關係協會 首頁",
      toolbarLabel: "工具列",
      mainNavLabel: "主導覽",
      searchLabel: "搜尋",
      searchFormLabel: "站內搜尋",
      searchKeyword: "關鍵字",
      searchPlaceholder: "搜尋課程、活動、文章…",
      searchClose: "關閉搜尋",
      searchSubmit: "搜尋",
      joinLabel: "加入會員",
      joinHref: "join.html",
      navToggleLabel: "開啟選單",
      drawerLabel: "行動選單",
      drawerNavLabel: "行動導覽",
      langCurrent: "中文"
    },
    en: {
      homeHref: "en.html",
      wordmarkLabel: "Taiwan Investor Relations Institute (TIRI) Home",
      toolbarLabel: "Toolbar",
      mainNavLabel: "Main navigation",
      searchLabel: "Search",
      searchFormLabel: "Site search",
      searchKeyword: "Keyword",
      searchPlaceholder: "Search courses, events, articles…",
      searchClose: "Close search",
      searchSubmit: "Search",
      joinLabel: "Join TIRI",
      joinHref: "join-342161.html",
      navToggleLabel: "Open menu",
      drawerLabel: "Mobile menu",
      drawerNavLabel: "Mobile navigation",
      langCurrent: "English"
    }
  };

  /* 英文頁清單由英文導覽資料推導：檔名落在清單內就渲染英文版 navbar */
  var englishPages = (function () {
    var set = {};
    function add(href) {
      var file = href.split("#")[0];
      if (file) set[file] = true;
    }
    navigationEn.forEach(function (item) {
      add(item.href);
      if (item.figure) add(item.figure[0]);
      (item.columns || []).forEach(function (column) {
        column.links.forEach(function (link) { add(link[0]); });
      });
    });
    return set;
  })();

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

  function renderDesktopNav(items) {
    return items.map(function (item) {
      if (!item.columns) {
        return '<li><a href="' + item.href + '">' + item.label + '</a></li>';
      }
      var figure = item.figure;
      return '<li><a href="' + item.href + '">' + item.label + '</a>' +
        '<div class="menu-panel"><div class="mega-inner">' + renderColumns(item.columns) +
        '<a class="mega-figure" href="' + figure[0] + '">' +
        '<img src="' + figure[1] + '" alt="" loading="lazy" width="380" height="176">' +
        '<span class="cap">' + figure[2] + '</span><span class="cta">' + figure[3] + ' <span aria-hidden="true">→</span></span>' +
        '</a></div></div></li>';
    }).join("");
  }

  function renderDrawer(items) {
    return items.map(function (item) {
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

  function renderLangSwitch(lang) {
    var zhCurrent = lang === "zh" ? ' aria-current="true"' : "";
    var enCurrent = lang === "en" ? ' aria-current="true"' : "";
    return '<div class="lang-switch">' +
      '<button class="lang-toggle" type="button" aria-expanded="false" aria-controls="lang-menu">' +
      icon("i-globe", 14) + '<span class="lang-current">' + uiStrings[lang].langCurrent + '</span>' +
      '<svg class="icon chev" width="10" height="10" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-chevron-down"></use></svg>' +
      '</button>' +
      '<div class="lang-menu" id="lang-menu">' +
      '<a href="index.html"' + zhCurrent + '>中文</a>' +
      '<a href="en.html"' + enCurrent + '>English</a>' +
      '</div></div>';
  }

  function renderHeaderTop(t, lang) {
    /* 會員登入先隱藏（暫時用不到）；要還原時在搜尋後補回：
       '<span class="divider" aria-hidden="true"></span><a href="login.html">會員登入</a>' */
    return '<nav class="header-top" aria-label="' + t.toolbarLabel + '">' +
      '<button class="search-toggle" type="button" aria-expanded="false" aria-controls="search-panel">' + icon("i-search", 15) + t.searchLabel + '</button>' +
      '<span class="divider" aria-hidden="true"></span><span class="social-icons">' + renderSocialIcons() + '</span>' +
      '<span class="divider" aria-hidden="true"></span>' + renderLangSwitch(lang) + '</nav>';
  }

  function renderActions(variant, t) {
    /* 登入先隱藏（暫時用不到）；要還原時在搜尋鈕後補回：
       '<a class="login-link" href="login.html">登入</a>' */
    var tools = variant === "v2"
      ? '<button class="search-toggle" type="button" aria-expanded="false" aria-controls="search-panel" aria-label="' + t.searchLabel + '">' + icon("i-search", 17) + '</button>'
      : "";
    return '<div class="header-actions">' + tools +
      '<a class="btn btn-primary btn-cta-desktop" href="' + t.joinHref + '"><span class="roll"><span>' + t.joinLabel + '</span><span aria-hidden="true">' + t.joinLabel + '</span></span></a>' +
      '<button class="nav-toggle" type="button" aria-expanded="false" aria-controls="drawer" aria-label="' + t.navToggleLabel + '"><span class="bar" aria-hidden="true"></span><span class="bar" aria-hidden="true"></span><span class="bar" aria-hidden="true"></span></button></div>';
  }

  function renderComponent(variant, lang) {
    var t = uiStrings[lang];
    var navItems = lang === "en" ? navigationEn : navigation;
    var drawerItems = lang === "en" ? drawerLinksEn : drawerLinks;
    return '<header class="site-header" id="site-header"><div class="container">' +
      '<a class="wordmark" href="' + t.homeHref + '" aria-label="' + t.wordmarkLabel + '"><img src="../images/tiri-logo.png" alt="" width="1100" height="649"></a>' +
      '<div class="header-right">' + (variant === "v1" ? renderHeaderTop(t, lang) : "") +
      '<div class="header-main"><nav class="main-nav" aria-label="' + t.mainNavLabel + '"><ul>' + renderDesktopNav(navItems) + '</ul></nav>' + renderActions(variant, t) + '</div></div></div>' +
      '<div class="search-drop" id="search-panel"><div class="search-backdrop" data-search-close></div><div class="search-sheet"><div class="container">' +
      '<form data-demo-form role="search" aria-label="' + t.searchFormLabel + '"><label class="sr-only" for="site-search-input">' + t.searchKeyword + '</label><input id="site-search-input" type="search" name="q" placeholder="' + t.searchPlaceholder + '"><button class="search-close" type="button" data-search-close aria-label="' + t.searchClose + '">' + icon("i-x", 14) + '</button><button class="btn btn-primary" type="submit">' + t.searchSubmit + '</button></form>' +
      '</div></div></div></header>' +
      '<div class="drawer" id="drawer"><div class="drawer-backdrop" data-drawer-close></div><div class="drawer-panel" role="dialog" aria-modal="true" aria-label="' + t.drawerLabel + '"><nav aria-label="' + t.drawerNavLabel + '"><ul>' + renderDrawer(drawerItems) + '</ul></nav>' +
      /* 抽屜的「會員登入」outline 鈕先隱藏（暫時用不到）；要還原時在加入會員後補回：
         '<a class="btn btn-outline" href="login.html">會員登入</a>' */
      '<div class="drawer-cta"><a class="btn btn-primary" href="' + t.joinHref + '">' + t.joinLabel + '</a></div></div></div>';
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
      var current = window.location.pathname.split("/").pop() || "index.html";
      var lang = englishPages[current] ? "en" : "zh";
      this.style.display = "contents";
      this.innerHTML = renderComponent(variant, lang);
      this.dataset.ready = "true";
      markCurrentPage(this);
    }
  }

  if (!customElements.get("tiri-navbar")) {
    customElements.define("tiri-navbar", TiriNavbar);
  }
})();
