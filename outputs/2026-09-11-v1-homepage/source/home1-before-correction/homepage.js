'use strict';
(() => {
  const carousel = document.querySelector('[data-home-carousel]');
  if (!carousel) return;
  const slides = [...carousel.querySelectorAll('.home-slide')];
  const selectors = [...carousel.querySelectorAll('[data-slide-to]')];
  const controls = carousel.querySelector('.home-carousel__controls');
  const toggle = carousel.querySelector('[data-carousel-toggle]');
  const count = carousel.querySelector('[data-carousel-count]');
  const status = carousel.querySelector('[data-carousel-status]');
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  let index = 0;
  let wantsPlay = !motion.matches;
  let hovered = false;
  let inView = true;
  let timer;
  let pointerStart;

  function schedule() {
    clearTimeout(timer);
    toggle.disabled = motion.matches;
    toggle.textContent = motion.matches ? '自動播放已停用' : wantsPlay ? '暫停輪播' : '播放輪播';
    toggle.setAttribute('aria-label', toggle.textContent);
    if (wantsPlay && !motion.matches && !hovered && inView && !document.hidden) {
      timer = setTimeout(() => show(index + 1), 6500);
    }
  }
  function show(next, manual = false) {
    index = (next + slides.length) % slides.length;
    if (manual) wantsPlay = false;
    slides.forEach((slide, i) => {
      const active = i === index;
      slide.classList.toggle('is-active', active);
      slide.inert = !active;
      slide.setAttribute('aria-hidden', String(!active));
      selectors[i].setAttribute('aria-current', String(active));
    });
    count.textContent = `${String(index + 1).padStart(2, '0')} / ${String(slides.length).padStart(2, '0')}`;
    if (manual) status.textContent = `第 ${index + 1} 張，共 ${slides.length} 張：${slides[index].dataset.slideName}`;
    schedule();
  }
  selectors.forEach(button => button.addEventListener('click', () => show(Number(button.dataset.slideTo), true)));
  carousel.querySelector('[data-carousel-prev]').addEventListener('click', () => show(index - 1, true));
  carousel.querySelector('[data-carousel-next]').addEventListener('click', () => show(index + 1, true));
  toggle.addEventListener('click', () => { wantsPlay = !wantsPlay; schedule(); });
  carousel.addEventListener('mouseenter', () => { hovered = true; schedule(); });
  carousel.addEventListener('mouseleave', () => { hovered = false; schedule(); });
  // Keyboard focus stops rotation until the visitor explicitly starts it again.
  carousel.addEventListener('focusin', event => {
    if (!carousel.contains(event.relatedTarget)) { wantsPlay = false; schedule(); }
  });
  carousel.addEventListener('keydown', event => {
    if (event.altKey || event.ctrlKey || event.metaKey) return;
    const next = {ArrowLeft:index - 1, ArrowRight:index + 1, Home:0, End:slides.length - 1}[event.key];
    if (next === undefined) return;
    event.preventDefault();
    // Keep focus on a stable control before making the previous slide inert.
    if (event.target.closest('.home-slide')) selectors[(next + slides.length) % slides.length].focus();
    show(next, true);
  });
  carousel.addEventListener('pointerdown', event => {
    if (event.pointerType !== 'touch' || !event.isPrimary || event.target.closest('a,button')) return;
    pointerStart = {x:event.clientX, y:event.clientY};
    clearTimeout(timer);
  }, {passive:true});
  carousel.addEventListener('pointerup', event => {
    if (!pointerStart) return;
    const dx = event.clientX - pointerStart.x, dy = event.clientY - pointerStart.y;
    pointerStart = null;
    if (Math.abs(dx) > 55 && Math.abs(dx) > Math.abs(dy) * 1.5) show(index + (dx < 0 ? 1 : -1), true);
    else schedule();
  }, {passive:true});
  carousel.addEventListener('pointercancel', () => { pointerStart = null; schedule(); }, {passive:true});
  document.addEventListener('visibilitychange', schedule);
  motion.addEventListener('change', () => { wantsPlay = false; schedule(); });
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(([entry]) => { inView = entry.isIntersecting; schedule(); }, {threshold:.2}).observe(carousel);
  }
  controls.hidden = false;
  show(0);
})();
