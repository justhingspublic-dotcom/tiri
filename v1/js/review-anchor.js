/* Keep direct review links aligned after web fonts settle. Stop if the visitor interacts. */
(() => {
  if (!location.hash) return;
  let interacted = false;
  const stop = () => { interacted = true; };
  ['wheel', 'touchstart', 'pointerdown', 'keydown'].forEach(type => window.addEventListener(type, stop, {once:true, passive:true}));
  const align = () => {
    if (interacted) return;
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
    const target = document.getElementById(id);
    if (target) target.scrollIntoView({block:'start', behavior:'instant'});
  };
  const observer = new ResizeObserver(() => {
    if (interacted) observer.disconnect();
    else requestAnimationFrame(align);
  });
  observer.observe(document.body);
  setTimeout(() => observer.disconnect(), 5000);
  const ready = document.fonts ? document.fonts.ready : Promise.resolve();
  ready.then(() => requestAnimationFrame(() => requestAnimationFrame(align)));
  window.addEventListener('load', () => ready.then(align), {once:true});
})();
