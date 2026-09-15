'use strict';
(() => {
  const recap = document.querySelector('[data-recap]');
  if (recap) {
    const year = recap.querySelector('#recap-year');
    const search = recap.querySelector('#recap-search');
    const cards = [...recap.querySelectorAll('.recap-card')];
    const english = recap.dataset.language === 'en';
    const filter = () => {
      const query = search.value.trim().toLocaleLowerCase();
      let count = 0;
      cards.forEach(card => {
        const match = (year.value === 'all' || card.dataset.recapYear === year.value) && (card.dataset.recapTitle+' '+card.dataset.recapYear).toLocaleLowerCase().includes(query);
        card.hidden = !match;
        if (match) count++;
      });
      recap.querySelector('#recap-count').textContent = `${count} ${english ? 'events' : '筆活動'}`;
      recap.querySelector('.recap-empty').hidden = count !== 0;
    };
    year.addEventListener('change', filter);
    search.addEventListener('input', filter);
    filter();
  }
  const nominees = document.querySelector('[data-nominees]');
  if (nominees) {
    const year = nominees.querySelector('#nominee-year');
    const update = () => {
      nominees.querySelectorAll('.nominee-panel').forEach(panel => { panel.hidden = panel.dataset.nomineeYear !== year.value; });
    };
    year.addEventListener('change', update);
    const requested = new URLSearchParams(location.search).get('term');
    if ([...year.options].some(option => option.value === requested)) year.value = requested;
    update();
  }
})();
