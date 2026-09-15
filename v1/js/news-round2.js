/* The source records stay intact; only the date-based presentation changes. */
(() => {
  'use strict';
  const source = document.getElementById('news-events');
  if (!source) return;
  const events = JSON.parse(source.textContent);
  const today = new Intl.DateTimeFormat('sv-SE', {timeZone:'Asia/Taipei',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
  const escape = value => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  function card(event, recent) {
    const tag = event.href ? 'a' : 'article';
    const external = /^https?:/.test(event.href);
    const link = event.href ? ` href="${escape(event.href)}"${external ? ' target="_blank" rel="noopener"' : ''}` : '';
    const photo = event.image ? `<img src="${escape(event.image.src)}" alt="${escape(event.image.alt || event.title)}" width="${escape(event.image.width)}" height="${escape(event.image.height)}" loading="lazy">` : '';
    const time = `<time datetime="${event.date}" aria-label="${event.date}">${recent ? event.date.replaceAll('-','.') : event.date.slice(8)}</time>`;
    return `<${tag} class="${recent ? 'news-recent-card' : 'event-banner-row'+(photo ? '' : ' archive-text-row')}"${link}>${photo}${recent ? '<div>'+time : time+'<div>'}<h3>${escape(event.title)}</h3><p>${escape(event.description)}</p></div></${tag}>`;
  }
  const recent = events.filter(event => event.date > today).sort((a,b) => a.date.localeCompare(b.date));
  const past = events.filter(event => event.date <= today).sort((a,b) => b.date.localeCompare(a.date));
  document.getElementById('news-recent-content').innerHTML = recent.length ? recent.map(event => card(event,true)).join('') : '<p class="news-empty">近期活動規劃中，歡迎先瀏覽過往活動紀錄。</p>';
  const years = [...new Set(past.map(event => event.date.slice(0,4)))];
  if (!years.length) {document.getElementById('news-archive-content').textContent='目前尚無過往活動。';return;}
  const picker = `<div class="term-bar"><span class="term-bar-label">年度</span><div class="term-picker" data-term-picker><button aria-controls="term-menu" aria-expanded="false" aria-haspopup="listbox" class="term-trigger" id="term-trigger" type="button"><span data-term-label>${years[0]} 年</span><span aria-hidden="true">⌄</span></button><ul aria-labelledby="term-trigger" class="term-menu" hidden id="term-menu" role="listbox">${years.map((year,i)=>`<li aria-selected="${!i}" class="term-option" data-value="${year}" role="option">${year} 年</li>`).join('')}</ul></div></div>`;
  const panels = years.map((year,i) => {
    const rows = past.filter(event => event.date.startsWith(year));
    const months = [...new Set(rows.map(event => event.date.slice(5,7)))];
    return `<div class="term-panel" data-term="${year}" id="year-${year}"${i ? ' hidden' : ''}>${months.map(month=>`<section class="month-group"><h3 class="month-heading">${year}<strong>${month}<small>月</small></strong></h3><div>${rows.filter(event=>event.date.slice(5,7)===month).map(event=>card(event,false)).join('')}</div></section>`).join('')}</div>`;
  }).join('');
  document.getElementById('news-archive-content').innerHTML = picker + panels;
})();
