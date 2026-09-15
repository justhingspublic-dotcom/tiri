'use strict';
(() => {
  const recap = document.querySelector('[data-recap]');
  if (!recap) return;
  const picker = recap.querySelector('[data-recap-picker]');
  const trigger = picker.querySelector('.term-trigger');
  const menu = picker.querySelector('.term-menu');
  const options = [...menu.querySelectorAll('[role="option"]')];
  const selectedLabel = trigger.querySelector('[data-recap-year-value]');
  const search = recap.querySelector('#recap-search');
  const cards = [...recap.querySelectorAll('.recap-card')];
  const english = recap.dataset.language === 'en';
  function filter() {
    const query = search.value.trim().toLocaleLowerCase();
    let count = 0;
    cards.forEach(card => {
      const match = (trigger.value === 'all' || card.dataset.recapYear === trigger.value)
        && (card.dataset.recapTitle + ' ' + card.dataset.recapYear).toLocaleLowerCase().includes(query);
      card.hidden = !match;
      if (match) count++;
    });
    recap.querySelector('#recap-count').textContent = `${count} ${english ? 'events' : '筆活動'}`;
    recap.querySelector('.recap-empty').hidden = count !== 0;
  }
  function close(restoreFocus = false) {
    menu.hidden = true;
    trigger.setAttribute('aria-expanded', 'false');
    picker.classList.remove('is-open');
    if (restoreFocus) trigger.focus();
  }
  function open(index) {
    menu.hidden = false;
    trigger.setAttribute('aria-expanded', 'true');
    picker.classList.add('is-open');
    options[index ?? options.findIndex(option => option.dataset.year === trigger.value)].focus();
  }
  function choose(option) {
    trigger.value = option.dataset.year;
    selectedLabel.textContent = option.textContent;
    options.forEach(item => item.setAttribute('aria-selected', String(item === option)));
    close(true);
    filter();
  }
  trigger.addEventListener('click', () => menu.hidden ? open() : close());
  trigger.addEventListener('keydown', event => {
    if (['ArrowDown', 'ArrowUp'].includes(event.key)) {
      event.preventDefault();
      open(event.key === 'ArrowUp' ? options.length - 1 : undefined);
    } else if (event.key === 'Escape') close();
  });
  options.forEach((option, index) => {
    option.addEventListener('click', () => choose(option));
    option.addEventListener('keydown', event => {
      let next;
      if (event.key === 'ArrowDown') next = (index + 1) % options.length;
      if (event.key === 'ArrowUp') next = (index + options.length - 1) % options.length;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = options.length - 1;
      if (next !== undefined) { event.preventDefault(); options[next].focus(); }
      if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); choose(option); }
      if (event.key === 'Escape') { event.preventDefault(); close(true); }
      if (event.key === 'Tab') close(true);
    });
  });
  document.addEventListener('click', event => { if (!picker.contains(event.target)) close(); });
  // A pointer click can blur an option with no relatedTarget before click fires.
  // Close on focus entering another element, so the trigger can toggle reliably.
  document.addEventListener('focusin', event => { if (!picker.contains(event.target)) close(); });
  search.addEventListener('input', filter);
  filter();
})();
