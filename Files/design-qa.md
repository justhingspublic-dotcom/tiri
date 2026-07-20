# Design QA

## Reference

- Source URL: <https://www.tiri.tw/>
- Reference screenshots:
  - `original/images/qa-source-desktop.png`（1440 × 1000）
  - `original/images/qa-source-mobile.png`（390 × 844）

## Static implementation

- Entry page: `original/html/index.html`
- Shared styles: `original/css/site.css`
- Shared interactions: `original/js/site.js`
- Implementation screenshots:
  - `original/images/qa-static-desktop.png`（1440 × 1000）
  - `original/images/qa-static-mobile.png`（390 × 844）
- Side-by-side comparisons:
  - `original/images/qa-comparison-desktop.png`
  - `original/images/qa-comparison-mobile.png`

## Checks performed

- Desktop navigation no longer overlaps the logo.
- Sticky navigation is offset below the offline notice.
- Desktop hero height and crop match the source layout.
- Mobile logo, hamburger navigation, hero crop, content width, and section rhythm were checked.
- All 126 HTML pages share the same CSS and JavaScript files.
- No inline `<style>`, inline `style` attribute, or inline JavaScript remains.
- Local-reference check reports zero missing files.

## Accepted differences

- A short offline notice is intentionally added above the header.
- Backend-only features, form submission, search, maps, video embeds, member login, and third-party widgets may still require network access.
- Font rendering can vary slightly by operating system and locally available fonts.
