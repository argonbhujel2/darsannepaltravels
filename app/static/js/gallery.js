/* Lightbox Gallery */
(function () {
  'use strict';

  const items = document.querySelectorAll('[data-gallery-item]');
  if (!items.length) return;

  let current = 0;
  const images = Array.from(items).map(el => ({
    src: el.dataset.src || el.querySelector('img')?.src,
    caption: el.dataset.caption || el.querySelector('img')?.alt || ''
  }));

  // Create lightbox DOM
  const lb = document.createElement('div');
  lb.className = 'lightbox';
  lb.setAttribute('role', 'dialog');
  lb.setAttribute('aria-modal', 'true');
  lb.innerHTML = `
    <button class="lightbox-close" aria-label="Close">&times;</button>
    <button class="lightbox-prev" aria-label="Previous">&#8249;</button>
    <img class="lightbox-img" src="" alt="">
    <button class="lightbox-next" aria-label="Next">&#8250;</button>
    <div class="lightbox-caption"></div>
  `;
  document.body.appendChild(lb);

  const imgEl = lb.querySelector('.lightbox-img');
  const capEl = lb.querySelector('.lightbox-caption');

  function show(i) {
    current = (i + images.length) % images.length;
    imgEl.src = images[current].src;
    imgEl.alt = images[current].caption;
    capEl.textContent = images[current].caption;
    lb.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function close() {
    lb.classList.remove('open');
    document.body.style.overflow = '';
  }

  items.forEach((el, i) => {
    el.addEventListener('click', (e) => { e.preventDefault(); show(i); });
  });

  lb.querySelector('.lightbox-close').addEventListener('click', close);
  lb.querySelector('.lightbox-prev').addEventListener('click', () => show(current - 1));
  lb.querySelector('.lightbox-next').addEventListener('click', () => show(current + 1));
  lb.addEventListener('click', (e) => { if (e.target === lb) close(); });

  document.addEventListener('keydown', (e) => {
    if (!lb.classList.contains('open')) return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowLeft') show(current - 1);
    if (e.key === 'ArrowRight') show(current + 1);
  });

  // Touch swipe
  let touchX = 0;
  lb.addEventListener('touchstart', (e) => { touchX = e.changedTouches[0].screenX; }, { passive: true });
  lb.addEventListener('touchend', (e) => {
    const dx = e.changedTouches[0].screenX - touchX;
    if (Math.abs(dx) > 50) show(current + (dx < 0 ? 1 : -1));
  }, { passive: true });
})();
