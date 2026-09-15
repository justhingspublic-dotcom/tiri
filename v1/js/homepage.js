'use strict';
(() => {
  const hero = document.querySelector('[data-home-carousel]');
  if (!hero) return;
  const images = [...hero.querySelectorAll('.home-slide')];
  if (images.length < 2) return;
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  let index = 0;
  let inView = true;
  let timer;

  function schedule() {
    clearTimeout(timer);
    if (motion.matches || !inView || document.hidden || hero.contains(document.activeElement)) return;
    timer = setTimeout(() => {
      images[index].classList.remove('is-active');
      index = (index + 1) % images.length;
      images[index].classList.add('is-active');
      schedule();
    }, 6500);
  }

  hero.addEventListener('focusin', schedule);
  hero.addEventListener('focusout', () => queueMicrotask(schedule));
  document.addEventListener('visibilitychange', schedule);
  motion.addEventListener('change', schedule);
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(([entry]) => {
      inView = entry.isIntersecting;
      schedule();
    }).observe(hero);
  }
  schedule();
})();
