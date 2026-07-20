(() => {
  document.body.classList.add("reveal-elements");

  const main =
    document.querySelector("main") ||
    document.querySelector("#wsite-content") ||
    document.querySelector(".main-wrap");

  if (main && !main.id) main.id = "main-content";

  if (main && !document.querySelector(".tiri-skip-link")) {
    const skip = document.createElement("a");
    skip.className = "tiri-skip-link";
    skip.href = `#${main.id}`;
    skip.textContent = "跳至主要內容";
    document.body.prepend(skip);
  }

  const englishLabels = new Set([
    "Home",
    "ABOUT TIRI",
    "ANNIVERSARY",
    "RECAP",
    "Course",
    "IRC©",
    "Award",
    "Membership",
    "IR Library",
    "Contact",
  ]);

  document.querySelectorAll(".desktop-nav > .wsite-menu-default > li, .mobile-nav > .wsite-menu-default > li").forEach((item) => {
    const label = item.querySelector(":scope > a > span")?.textContent.trim();
    if (englishLabels.has(label)) item.classList.add("tiri-language-duplicate");
  });

  const desktopNav = document.querySelector(".desktop-nav");
  if (desktopNav && !document.querySelector(".tiri-language-switch")) {
    const language = document.createElement("a");
    language.className = "tiri-language-switch";
    language.href = "en.html";
    language.textContent = "English";
    language.setAttribute("aria-label", "Switch to English");
    desktopNav.after(language);
  }

  document.querySelectorAll('a[target="_blank"]').forEach((link) => {
    const rel = new Set((link.getAttribute("rel") || "").split(/\s+/).filter(Boolean));
    rel.add("noopener");
    rel.add("noreferrer");
    link.setAttribute("rel", [...rel].join(" "));
  });

  document.querySelectorAll("img:not([loading])").forEach((image, index) => {
    if (index > 2) image.loading = "lazy";
    image.decoding = "async";
  });

  const openMenu = document.querySelector(".hamburger");
  const closeMenu = document.querySelector(".mobile-nav-toggle");
  const mobileNav = document.querySelector(".mobile-nav");

  const setMenu = (isOpen) => {
    document.body.classList.toggle("tiri-menu-open", isOpen);
    openMenu?.setAttribute("aria-expanded", String(isOpen));
    mobileNav?.setAttribute("aria-hidden", String(!isOpen));
  };

  if (openMenu && mobileNav) {
    openMenu.setAttribute("aria-controls", "mobile-navigation");
    openMenu.setAttribute("aria-expanded", "false");
    mobileNav.id = "mobile-navigation";
    mobileNav.setAttribute("aria-hidden", "true");
    openMenu.addEventListener("click", () => setMenu(true));
    closeMenu?.addEventListener("click", () => setMenu(false));
  }

  mobileNav?.querySelectorAll(".wsite-menu-item-wrap").forEach((item) => {
    const link = item.querySelector(":scope > a");
    const submenu = item.querySelector(":scope > .wsite-menu-wrap");
    if (!link || !submenu) return;
    link.setAttribute("aria-expanded", "false");
    link.addEventListener("click", (event) => {
      if (!submenu.classList.contains("tiri-submenu-open")) {
        event.preventDefault();
        submenu.classList.add("tiri-submenu-open");
        link.setAttribute("aria-expanded", "true");
      }
    });
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") setMenu(false);
  });
})();
